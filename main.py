"""
Pipecat Voice Agent with Azure STT/TTS and Custom LLM over FastAPI WebSocket
"""

import os
import sys
import logging
import time
import uuid

from dotenv import load_dotenv
from loguru import logger

# Filter out InterruptionFrame serialization warnings (these are expected)
logging.getLogger("pipecat.serializers.protobuf").setLevel(logging.ERROR)

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator,
)
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.tts import AzureTTSService
from pipecat.transcriptions.language import Language
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams, FastAPIWebsocketTransport

from custom_llm import CustomTextStreamLLM
from custom_rtvi_observer import CustomRTVIObserver, GlobalFieldInjectorObserver

# Load environment variables
load_dotenv()

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create FastAPI app
app = FastAPI(title="Pipecat Voice Agent")


async def run_voice_agent(websocket: WebSocket):
    """
    Run the voice agent pipeline for a WebSocket connection.
    
    Args:
        websocket: The FastAPI WebSocket connection
    """
    # Filter out benign InterruptionFrame warnings
    logging.getLogger("pipecat.serializers.protobuf").setLevel(logging.ERROR)
    
    logger.info("Starting voice agent for new WebSocket connection")
    
    # Get Azure credentials from environment
    azure_api_key = os.getenv("AZURE_SPEECH_API_KEY")
    azure_region = os.getenv("AZURE_SPEECH_REGION")
    
    if not azure_api_key or not azure_region:
        logger.error("Azure credentials not configured. Please set AZURE_SPEECH_API_KEY and AZURE_SPEECH_REGION")
        await websocket.close(code=1008, reason="Server configuration error")
        return
    
    # Initialize Azure Speech-to-Text service
    stt = AzureSTTService(
        api_key=azure_api_key,
        region=azure_region,
        language=Language.EN_US,
    )
    logger.info("Azure STT service initialized")
    
    # Initialize Azure Text-to-Speech service
    tts = AzureTTSService(
        api_key=azure_api_key,
        region=azure_region,
        voice="en-US-AvaMultilingualNeural",  # You can change the voice
    )
    logger.info("Azure TTS service initialized")
    
    # Initialize custom LLM service
    llm = CustomTextStreamLLM()
    logger.info("Custom LLM service initialized")
    
    # Set up conversation context
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI voice assistant. Keep your responses concise and conversational since they will be spoken aloud. Be friendly and engaging."
        }
    ]
    context = OpenAILLMContext(messages)
    
    # Create context aggregators
    user_aggregator = LLMUserContextAggregator(context)
    assistant_aggregator = LLMAssistantContextAggregator(context)
    
    # RTVI events for Pipecat client UI with transcription enabled
    rtvi = RTVIProcessor(
        config=RTVIConfig(
            config=[

            ]
        )
    )
    
    # Configure WebSocket transport with Protobuf serializer (required for official client SDK)
    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,  # Protobuf handles framing
            vad_analyzer=SileroVADAnalyzer(),
            serializer=ProtobufFrameSerializer(),  # Official serializer for WebSocket client
        ),
    )
    
    logger.info("WebSocket transport configured")
    
    # Build the processing pipeline with RTVI before LLM
    pipeline = Pipeline(
        [
            transport.input(),  # Receive audio from client
            stt,  # Convert speech to text (Azure STT)
            user_aggregator,  # Add user message to context
            rtvi,  # RTVI events for client UI (handles transcription events)
            llm,  # Generate response with custom LLM
            tts,  # Convert response to speech (Azure TTS)
            transport.output(),  # Send audio AND transcripts to client
            assistant_aggregator,  # Add assistant response to context
        ]
    )
    
    # Generate a unique session ID for this connection
    session_id = str(uuid.uuid4())
    
    logger.info(f"Session ID: {session_id}")
    
    # Create custom RTVI observer with session_id and metadata
    # Option 1: Use CustomRTVIObserver for specific control over which events get custom fields
    custom_observer = CustomRTVIObserver(
        rtvi,
        session_id=session_id,
        custom_metadata={
            "connection_time": time.time(),
            "user_agent": "pipecat-voice-agent"
        }
    )
    
    # Option 2: Use GlobalFieldInjectorObserver to inject fields into ALL messages
    # Uncomment this and comment out the CustomRTVIObserver above to use this approach:
    # custom_observer = GlobalFieldInjectorObserver(
    #     rtvi,
    #     inject_fields={
    #         "session_id": session_id,
    #         "connection_time": time.time()
    #     }
    # )
    
    # Create pipeline task with custom observer
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[custom_observer],
    )
    
    # Set up RTVI event handler for client ready
    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.info("Pipecat client ready.")
        await rtvi.set_bot_ready()
        # Don't send initial frame - let user speak first
    
    # Set up transport event handlers
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected: {client}")
    
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected: {client}")
        await task.cancel()
    
    # Run the pipeline
    runner = PipelineRunner(handle_sigint=False)
    
    try:
        await runner.run(task)
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
    finally:
        logger.info("Voice agent session ended")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice agent connections.
    
    Clients connect to this endpoint to start a voice conversation.
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        await run_voice_agent(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve a simple info page.
    """
    return """
    <html>
        <head>
            <title>Pipecat Voice Agent</title>
        </head>
        <body>
            <h1>Pipecat Voice Agent</h1>
            <p>This is a voice agent powered by:</p>
            <ul>
                <li>Azure Speech Services (STT/TTS)</li>
                <li>Custom Text Streaming LLM</li>
                <li>FastAPI WebSocket Transport</li>
            </ul>
            <p>Connect to <code>ws://localhost:8000/ws</code> to start a voice conversation.</p>
            <p><a href="/client">Try the web client</a></p>
        </body>
    </html>
    """


@app.get("/client", response_class=HTMLResponse)
async def client():
    """
    Serve the HTML client for testing the voice agent.
    """
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting Pipecat Voice Agent server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
