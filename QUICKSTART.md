# Quick Start Guide

Get your voice agent running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Azure Speech Services account with API key

## Steps

### 1. Setup (First time only)

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file

### 2. Configure Azure Credentials

Edit the `.env` file:
```env
AZURE_SPEECH_API_KEY=your_key_here
AZURE_SPEECH_REGION=your_region_here
```

Get your Azure credentials:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Speech Service resource
3. Click "Keys and Endpoint" in the left menu
4. Copy Key 1 and Region

### 3. Run the Server

**Windows:**
```bash
venv\Scripts\activate
python main.py
```

**macOS/Linux:**
```bash
source venv/bin/activate
python main.py
```

### 4. Test It Out

1. Open browser to: http://localhost:8000/client
2. Click "Connect"
3. Hold "Hold to Talk" and speak
4. Release and listen to the response!

## Example Conversation

Try saying:
- "Hello, how are you?"
- "Tell me about yourself"
- "What's the weather like?"
- "Goodbye!"

## Troubleshooting

**Can't connect?**
- Check if server is running
- Ensure no firewall blocking port 8000

**No microphone?**
- Allow browser microphone permission
- Check microphone is working in system settings

**Azure errors?**
- Verify API key and region in .env
- Check Azure subscription is active

## Next Steps

- Customize the LLM in `custom_llm.py`
- Change the voice in `main.py`
- Read the full README.md for more options

---

**Need help?** Check the full README.md or Pipecat documentation at https://docs.pipecat.ai
