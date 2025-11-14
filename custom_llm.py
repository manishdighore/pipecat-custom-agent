"""
Custom LLM Service that generates text responses as a stream.
This is a simple example that can be replaced with your actual LLM implementation.
"""

import asyncio
from typing import AsyncGenerator

from loguru import logger
from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    TextFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService
import time

class CustomTextStreamLLM(LLMService):
    """
    A custom LLM service that generates text responses as a stream.
    
    This example splits a response into words and yields them one at a time,
    simulating a streaming LLM response. Replace the `generate_response` method
    with your actual LLM implementation that returns an async generator of text chunks.
    """

    def __init__(self, **kwargs):
        """Initialize the custom LLM service."""
        super().__init__(**kwargs)
        self._conversation_history = []

    async def generate_response(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Generate a streaming text response for the given user message.
        
        This is a placeholder implementation that you should replace with your
        actual LLM logic (e.g., calling an API, running a local model, etc.).
        
        Args:
            user_message: The user's input message
            
        Yields:
            str: Text chunks to be spoken by the TTS service
        """
        # Example: A simple response that simulates streaming
        # Replace this with your actual LLM implementation
        
        logger.info(f"🎤 USER TRANSCRIPT: {user_message}")
        
        # Example responses based on simple keyword matching
        user_lower = user_message.lower()
        
        if "hello" in user_lower or "hi" in user_lower:
            response = (
                "Hello! How can I help you today? I'm here to assist you with any questions you might have. "
                "Whether you need information, advice, or just want to chat, feel free to ask me anything. "
                "I'm always ready to help make your experience enjoyable and productive. "
                "Is there something specific you'd like to talk about or learn more about today?"
            )
        elif "how are you" in user_lower:
            response = "I'm doing great, thank you for asking! I'm an AI assistant ready to help you. How are you doing?"
        elif "weather" in user_lower:
            response = "I don't have access to real-time weather data, but I'd be happy to help you with something else. What would you like to know?"
        elif "bye" in user_lower or "goodbye" in user_lower:
            response = "Goodbye! It was nice talking to you. Have a wonderful day!"
        else:
            response = f"You said: {user_message}. That's interesting! I'm a custom LLM processor. You can replace this logic with your own text generation function that returns a stream of text chunks."
        
        # Simulate streaming by yielding words one at a time
        # In a real implementation, your LLM would yield chunks as they're generated
        words = response.split()
        
        for i, word in enumerate(words):
            # Add a space after each word except the last one
            chunk = word if i == len(words) - 1 else word + " "
            logger.info(f"🔊 Yielding chunk: {chunk}")
            yield chunk
            
            # Simulate some processing delay (remove this in production)
            await asyncio.sleep(0.05)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames from the pipeline."""
        await super().process_frame(frame, direction)
        
        # Import here to avoid circular imports
        from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
        
        # When we receive a context frame with user input, generate a response
        if isinstance(frame, OpenAILLMContextFrame):
            context = frame.context
            messages = context.messages
            
            if messages and len(messages) > 0:
                last_message = messages[-1]
                
                if last_message.get("role") == "user":
                    user_text = last_message.get("content", "")
                    logger.info(f"🎤 User: {user_text}")
                    
                    # Add to conversation history
                    self._conversation_history.append({
                        "role": "user",
                        "content": user_text
                    })
                    
                    # Signal start of response
                    await self.push_frame(LLMFullResponseStartFrame())
                    
                    # Generate and stream the response
                    full_response = ""
                    async for text_chunk in self.generate_response(user_text):
                        full_response += text_chunk
                        await asyncio.sleep(0.02)
                        # Push LLMTextFrame so RTVIObserver can stream it to frontend
                        await self.push_frame(LLMTextFrame(text_chunk))
                    
                    # Add assistant response to history
                    self._conversation_history.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    
                    # Signal end of response
                    await self.push_frame(LLMFullResponseEndFrame())
                    
                    logger.info(f"🤖 Bot: {full_response}")
        else:
            # Pass through other frames
            await self.push_frame(frame, direction)
