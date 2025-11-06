"""
Example: Advanced Custom LLM Implementations

This file shows different ways to implement your own LLM response generation.
Copy the approach that fits your needs into custom_llm.py
"""

import asyncio
from typing import AsyncGenerator
import json


# ============================================================================
# Example 1: Call OpenAI API directly (streaming)
# ============================================================================

async def example_openai_streaming(user_message: str) -> AsyncGenerator[str, None]:
    """
    Stream responses from OpenAI's API directly.
    Requires: pip install openai
    """
    import openai
    import os
    
    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": user_message}
        ],
        stream=True,
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ============================================================================
# Example 2: Call Anthropic Claude (streaming)
# ============================================================================

async def example_anthropic_streaming(user_message: str) -> AsyncGenerator[str, None]:
    """
    Stream responses from Anthropic's Claude API.
    Requires: pip install anthropic
    """
    import anthropic
    import os
    
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_message}
        ],
    ) as stream:
        async for text in stream.text_stream:
            yield text


# ============================================================================
# Example 3: Local LLM with Ollama (streaming)
# ============================================================================

async def example_ollama_streaming(user_message: str) -> AsyncGenerator[str, None]:
    """
    Use a local LLM via Ollama.
    Requires: Ollama installed and running, pip install aiohttp
    """
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',
                'prompt': user_message,
                'stream': True
            }
        ) as response:
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']


# ============================================================================
# Example 4: Custom HTTP API (streaming)
# ============================================================================

async def example_custom_api_streaming(user_message: str) -> AsyncGenerator[str, None]:
    """
    Call your own custom LLM API endpoint.
    Requires: pip install aiohttp
    """
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://your-api.com/generate',
            json={
                'prompt': user_message,
                'stream': True,
                'temperature': 0.7,
            },
            headers={
                'Authorization': f'Bearer {os.getenv("YOUR_API_KEY")}'
            }
        ) as response:
            async for line in response.content:
                if line:
                    # Parse your API's response format
                    chunk = line.decode('utf-8').strip()
                    if chunk:
                        yield chunk


# ============================================================================
# Example 5: Template-based responses (no API needed)
# ============================================================================

async def example_template_based(user_message: str) -> AsyncGenerator[str, None]:
    """
    Generate responses using templates and keyword matching.
    Good for demos or specific use cases.
    """
    user_lower = user_message.lower()
    
    # Define response templates
    templates = {
        'greeting': "Hello! I'm your AI assistant. How can I help you today?",
        'goodbye': "Thank you for chatting with me. Have a great day!",
        'weather': "I don't have access to real-time weather data, but I can help with other information.",
        'time': f"I don't have a clock, but I can help you with other questions!",
        'help': "I'm here to assist you. You can ask me questions, and I'll do my best to help!",
        'default': f"You asked about: {user_message}. I'm a demo assistant. Replace this with your own logic!"
    }
    
    # Match keywords to templates
    if any(word in user_lower for word in ['hello', 'hi', 'hey']):
        response = templates['greeting']
    elif any(word in user_lower for word in ['bye', 'goodbye', 'see you']):
        response = templates['goodbye']
    elif 'weather' in user_lower:
        response = templates['weather']
    elif any(word in user_lower for word in ['time', 'clock']):
        response = templates['time']
    elif 'help' in user_lower:
        response = templates['help']
    else:
        response = templates['default']
    
    # Simulate streaming
    words = response.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)


# ============================================================================
# Example 6: Hugging Face Inference API (streaming)
# ============================================================================

async def example_huggingface_streaming(user_message: str) -> AsyncGenerator[str, None]:
    """
    Use Hugging Face's Inference API.
    Requires: pip install aiohttp
    """
    import aiohttp
    import os
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api-inference.huggingface.co/models/microsoft/DialoGPT-large',
            headers={'Authorization': f'Bearer {os.getenv("HUGGINGFACE_API_KEY")}'},
            json={'inputs': user_message}
        ) as response:
            result = await response.json()
            
            # Parse response
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                
                # Simulate streaming
                words = generated_text.split()
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.03)


# ============================================================================
# Example 7: Context-aware conversation with memory
# ============================================================================

class ConversationMemory:
    """Simple conversation memory for context-aware responses."""
    
    def __init__(self):
        self.history = []
        self.max_history = 10
    
    def add_message(self, role: str, content: str):
        """Add a message to history."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self) -> str:
        """Get conversation context as a string."""
        return "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.history
        ])


async def example_context_aware(
    user_message: str, 
    memory: ConversationMemory
) -> AsyncGenerator[str, None]:
    """
    Generate responses with conversation memory.
    """
    # Add user message to memory
    memory.add_message("user", user_message)
    
    # Use context to generate better responses
    context = memory.get_context()
    
    # Simple example - you'd call your LLM here with the full context
    if len(memory.history) > 2:
        response = f"Based on our conversation, I understand you're asking about {user_message}. "
    else:
        response = f"You asked: {user_message}. "
    
    response += "This is a context-aware response that remembers previous messages."
    
    # Add response to memory
    memory.add_message("assistant", response)
    
    # Stream the response
    words = response.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)


# ============================================================================
# Example 8: Function calling / Tool use
# ============================================================================

async def example_with_tools(user_message: str) -> AsyncGenerator[str, None]:
    """
    Example showing how to add function/tool calling capabilities.
    """
    # Define available tools
    tools = {
        'get_weather': lambda city: f"The weather in {city} is sunny, 72°F",
        'get_time': lambda: "The current time is 3:45 PM",
        'calculate': lambda expr: f"The result is {eval(expr)}"
    }
    
    # Simple intent detection
    user_lower = user_message.lower()
    
    if 'weather' in user_lower:
        # Extract city (simple example)
        city = "your city"
        for word in user_message.split():
            if word[0].isupper() and word not in ['I', 'What', 'The']:
                city = word
                break
        
        result = tools['get_weather'](city)
        response = f"Let me check the weather for you. {result}"
    
    elif 'time' in user_lower:
        result = tools['get_time']()
        response = f"Sure! {result}"
    
    elif any(op in user_message for op in ['+', '-', '*', '/']):
        try:
            # WARNING: eval is dangerous in production! Use a proper math parser
            result = tools['calculate'](user_message)
            response = f"I can help with that calculation. {result}"
        except:
            response = "I couldn't calculate that. Can you rephrase?"
    
    else:
        response = f"You said: {user_message}. I can help with weather, time, or calculations!"
    
    # Stream response
    words = response.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)


# ============================================================================
# How to use these examples in custom_llm.py
# ============================================================================

"""
To use any of these examples, replace the generate_response method in 
custom_llm.py with your chosen implementation.

For example, to use OpenAI streaming:

class CustomTextStreamLLM(LLMService):
    async def generate_response(self, user_message: str) -> AsyncGenerator[str, None]:
        # Copy the example_openai_streaming implementation here
        import openai
        import os
        
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        stream = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": user_message}
            ],
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
"""
