# Pipecat Voice Agent with Azure Services

A real-time voice AI agent built with [Pipecat](https://github.com/pipecat-ai/pipecat), featuring:

- 🎤 **Azure Speech-to-Text (STT)** - Convert voice to text in real-time
- 🔊 **Azure Text-to-Speech (TTS)** - Natural-sounding voice responses
- 🤖 **Custom LLM Function** - Your own text generation logic that streams responses
- 🌐 **FastAPI WebSocket Transport** - Real-time bidirectional communication
- 🎙️ **Voice Activity Detection (VAD)** - Automatic speech detection using Silero

## Architecture

```
User (Browser) <--WebSocket--> FastAPI Server
                                     |
                                  Pipeline
                                     |
      +--------------------------------+--------------------------------+
      |                                |                                |
  Azure STT                      Custom LLM                        Azure TTS
  (Speech to Text)           (Text Stream Generator)          (Text to Speech)
```

The pipeline processes data in real-time:
1. **Audio Input** → WebSocket receives raw audio from browser
2. **Speech Recognition** → Azure STT converts speech to text
3. **Context Aggregation** → User message added to conversation context
4. **LLM Generation** → Custom function generates streaming text response
5. **Speech Synthesis** → Azure TTS converts text to natural speech
6. **Audio Output** → WebSocket sends audio back to browser

## Prerequisites

- Python 3.10 or higher (recommended: 3.12)
- Azure Speech Services account ([Create one here](https://portal.azure.com))
- Modern web browser with microphone access

## Setup

### 1. Clone or Download

```bash
cd pipecat_voice
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pipecat-ai[azure,fastapi]` - Pipecat framework with Azure and FastAPI support
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management
- `loguru` - Logging

### 4. Configure Azure Credentials

1. Copy the example environment file:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # macOS/Linux
   ```

2. Edit `.env` and add your Azure credentials:
   ```env
   AZURE_SPEECH_API_KEY=your_actual_api_key_here
   AZURE_SPEECH_REGION=your_region_here
   ```

   - **API Key**: Find in Azure Portal → Speech Services → Keys and Endpoint
   - **Region**: e.g., `eastus`, `westus2`, `westeurope`

### 5. Run the Server

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the Voice Agent

Open your browser and navigate to:
```
http://localhost:8000/client
```

1. Click **"Connect"** to establish WebSocket connection
2. Hold **"Hold to Talk"** button and speak
3. Release the button to send your audio
4. Listen to the AI's voice response

## File Structure

```
pipecat_voice/
├── main.py              # FastAPI server & Pipecat pipeline
├── custom_llm.py        # Custom LLM with text streaming
├── client.html          # Web client for testing
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual credentials (git-ignored)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Customizing the LLM

The `custom_llm.py` file contains a `CustomTextStreamLLM` class with a placeholder implementation. To use your own LLM:

### Option 1: Simple Text Generation

Replace the `generate_response` method with your logic:

```python
async def generate_response(self, user_message: str) -> AsyncGenerator[str, None]:
    # Your custom logic here
    response = my_llm_function(user_message)
    
    # Stream word by word
    for word in response.split():
        yield word + " "
        await asyncio.sleep(0.05)
```

### Option 2: Call External API

```python
async def generate_response(self, user_message: str) -> AsyncGenerator[str, None]:
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://your-llm-api.com/generate",
            json={"prompt": user_message, "stream": True}
        ) as response:
            async for line in response.content:
                chunk = line.decode('utf-8')
                yield chunk
```

### Option 3: Use OpenAI/Anthropic

If you want to use OpenAI or Anthropic instead of the custom LLM:

1. Install the service:
   ```bash
   pip install pipecat-ai[openai]  # or [anthropic]
   ```

2. Replace in `main.py`:
   ```python
   from pipecat.services.openai.llm import OpenAILLMService
   
   llm = OpenAILLMService(
       api_key=os.getenv("OPENAI_API_KEY"),
       model="gpt-4"
   )
   ```

## Changing the Azure Voice

In `main.py`, modify the `voice` parameter:

```python
tts = AzureTTSService(
    api_key=azure_api_key,
    region=azure_region,
    voice="en-US-JennyNeural",  # Change this
)
```

Popular voices:
- `en-US-AvaMultilingualNeural` - Natural female voice (default)
- `en-US-JennyNeural` - Friendly female voice
- `en-US-GuyNeural` - Male voice
- `en-US-AriaNeural` - Expressive female voice
- `en-GB-SonicNeural` - British male voice

[See all available voices](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)

## Configuration Options

### VAD (Voice Activity Detection) Settings

In `main.py`, adjust the `VADParams`:

```python
vad_analyzer=SileroVADAnalyzer(
    params=VADParams(
        stop_secs=0.5,  # Silence duration before stopping (default: 0.5)
        # min_volume=0.6,  # Minimum volume threshold
        # start_secs=0.2,  # Delay before starting
    )
)
```

### Server Settings

In `.env`:
```env
HOST=0.0.0.0      # Listen on all interfaces
PORT=8000          # Server port
```

### Pipeline Options

In `main.py`, configure the `PipelineParams`:

```python
task = PipelineTask(
    pipeline,
    params=PipelineParams(
        allow_interruptions=True,  # Let user interrupt AI
        enable_metrics=True,        # Track performance
        enable_usage_metrics=True,  # Track token usage
    ),
)
```

## Troubleshooting

### Import Errors

If you see import errors, ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Azure Authentication Errors

- Verify your API key is correct in `.env`
- Check the region matches your Azure resource
- Ensure your Azure subscription is active

### Microphone Not Working

- Grant browser permission to access microphone
- Use HTTPS in production (HTTP works for localhost)
- Check browser console for errors

### No Audio Response

- Check Azure TTS configuration
- Verify browser can play audio
- Look for errors in server logs

### WebSocket Connection Failed

- Ensure server is running on the correct port
- Check firewall settings
- Verify WebSocket URL matches server address

## API Endpoints

- `GET /` - Info page
- `GET /client` - Web client UI
- `GET /health` - Health check endpoint
- `WS /ws` - WebSocket endpoint for voice agent

## Development

### Enable Debug Logging

In `main.py`, change logger level:
```python
logger.add(sys.stderr, level="DEBUG")
```

### Test Without Client

You can test the WebSocket using tools like:
- [websocat](https://github.com/vi/websocat)
- Browser console
- Python WebSocket client

Example with Python:
```python
import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # Send binary audio data
        await ws.send(audio_bytes)
        
        # Receive response
        response = await ws.recv()
        print(f"Received: {len(response)} bytes")

asyncio.run(test())
```

## Production Deployment

For production use:

1. **Use HTTPS/WSS** - Required for browser microphone in production
2. **Set up reverse proxy** - Use Nginx or similar
3. **Configure CORS** - If serving client from different domain
4. **Add authentication** - Secure your WebSocket endpoint
5. **Scale with workers** - Use Uvicorn workers for concurrency
6. **Monitor performance** - Enable metrics and logging
7. **Handle errors gracefully** - Add reconnection logic in client

Example production run:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## Resources

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Pipecat GitHub](https://github.com/pipecat-ai/pipecat)
- [Azure Speech Services Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## License

This project is provided as-is for educational and development purposes.

## Support

For issues with:
- **Pipecat**: [GitHub Issues](https://github.com/pipecat-ai/pipecat/issues)
- **Azure Speech**: [Azure Support](https://azure.microsoft.com/support/)
- **This implementation**: Check server logs and browser console

---

Built with ❤️ using [Pipecat](https://pipecat.ai)
