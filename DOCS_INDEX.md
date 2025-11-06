# 📚 Documentation Index

Welcome to the Pipecat Voice Agent documentation! This guide will help you find what you need.

## 🚀 Quick Start

**New to the project?** Start here:

1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
   - Installation steps
   - Configuration
   - First run
   - Testing the agent

## 📖 Main Documentation

### Core Documentation

- **[README.md](README.md)** - Complete project documentation
  - Overview and features
  - Detailed setup instructions
  - Configuration options
  - Customization guide
  - Production deployment
  - FAQ

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level overview
  - What you have
  - Architecture summary
  - Key features
  - Technologies used
  - Quick reference

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - Data flow diagrams
  - Component interactions
  - Pipeline flow
  - Timing diagrams
  - Performance metrics

### Troubleshooting

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions to common issues
  - Installation problems
  - Configuration errors
  - Connection issues
  - Audio problems
  - Performance optimization
  - Debugging tips

## 💻 Code Files

### Main Application

- **[main.py](main.py)** - FastAPI server and Pipecat pipeline
  ```python
  # Key components:
  - FastAPIWebsocketTransport
  - AzureSTTService
  - AzureTTSService
  - CustomTextStreamLLM
  - Pipeline configuration
  ```

- **[custom_llm.py](custom_llm.py)** - Custom LLM implementation
  ```python
  # Replace generate_response() with your LLM logic
  async def generate_response(self, user_message: str) -> AsyncGenerator[str, None]:
      # Your implementation here
  ```

- **[examples_llm.py](examples_llm.py)** - 8 different LLM approaches
  - OpenAI streaming
  - Anthropic Claude
  - Local Ollama
  - Custom HTTP API
  - Template-based responses
  - HuggingFace API
  - Context-aware conversation
  - Function calling

### Client

- **[client.html](client.html)** - Web interface
  - Beautiful UI
  - Audio recording
  - WebSocket communication
  - Real-time playback

## ⚙️ Configuration Files

- **[requirements.txt](requirements.txt)** - Python dependencies
  ```
  pipecat-ai[azure,fastapi]
  fastapi
  uvicorn[standard]
  python-dotenv
  loguru
  ```

- **[.env.example](.env.example)** - Environment variables template
  ```
  AZURE_SPEECH_API_KEY=your_key
  AZURE_SPEECH_REGION=your_region
  HOST=0.0.0.0
  PORT=8000
  ```

- **[.gitignore](.gitignore)** - Files to ignore in git

## 🛠️ Setup Scripts

- **[setup.bat](setup.bat)** - Windows setup script
  - Creates virtual environment
  - Installs dependencies
  - Configures .env file

- **[setup.sh](setup.sh)** - Unix/Mac setup script
  - Same as setup.bat for Linux/macOS
  - Make executable: `chmod +x setup.sh`

## 📋 Documentation by Topic

### Getting Started
1. [QUICKSTART.md](QUICKSTART.md) - Fast setup
2. [README.md](README.md) - Full documentation
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview

### Understanding the System
1. [ARCHITECTURE.md](ARCHITECTURE.md) - How it works
2. [main.py](main.py) - See the code
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Key features

### Customizing
1. [custom_llm.py](custom_llm.py) - Your LLM logic
2. [examples_llm.py](examples_llm.py) - 8 examples
3. [README.md](README.md) - Configuration options

### Troubleshooting
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
2. [README.md](README.md) - FAQ section
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand flow

### Deployment
1. [README.md](README.md) - Production section
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Production issues
3. [.env.example](.env.example) - Configuration

## 🎯 Common Tasks

### "I want to run the voice agent"
→ [QUICKSTART.md](QUICKSTART.md)

### "I want to use my own LLM"
→ [custom_llm.py](custom_llm.py) + [examples_llm.py](examples_llm.py)

### "I want to change the voice"
→ [README.md](README.md#changing-the-azure-voice)

### "Something isn't working"
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### "I want to understand the architecture"
→ [ARCHITECTURE.md](ARCHITECTURE.md)

### "I want to deploy to production"
→ [README.md](README.md#production-deployment)

### "I want to customize VAD settings"
→ [README.md](README.md#vad-voice-activity-detection-settings)

### "I want examples of different LLMs"
→ [examples_llm.py](examples_llm.py)

## 📚 Reading Order

### For Beginners
1. Start with [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview
2. Follow [QUICKSTART.md](QUICKSTART.md) to get it running
3. Read [README.md](README.md) for full details
4. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise

### For Developers
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand system
2. Review [main.py](main.py) for implementation
3. Explore [examples_llm.py](examples_llm.py) for LLM options
4. Customize [custom_llm.py](custom_llm.py) for your needs

### For Deployers
1. Read [README.md](README.md) production section
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for production issues
3. Review [.env.example](.env.example) for configuration
4. Study [ARCHITECTURE.md](ARCHITECTURE.md) for optimization

## 🔗 External Resources

### Pipecat
- [Official Documentation](https://docs.pipecat.ai/)
- [GitHub Repository](https://github.com/pipecat-ai/pipecat)
- [Discord Community](https://discord.gg/pipecat)
- [Examples Repository](https://github.com/pipecat-ai/pipecat-examples)

### Azure Speech Services
- [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [Voice Gallery](https://speech.microsoft.com/portal/voicegallery)
- [Language Support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

### FastAPI
- [Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)

## 📝 File Structure Reference

```
pipecat_voice/
│
├── 📄 Documentation
│   ├── README.md              # Main documentation
│   ├── QUICKSTART.md          # 5-minute setup
│   ├── PROJECT_SUMMARY.md     # Project overview
│   ├── ARCHITECTURE.md        # System architecture
│   ├── TROUBLESHOOTING.md     # Problem solutions
│   └── DOCS_INDEX.md          # This file
│
├── 💻 Application Code
│   ├── main.py                # FastAPI server
│   ├── custom_llm.py          # Custom LLM service
│   ├── examples_llm.py        # LLM examples
│   └── client.html            # Web interface
│
├── ⚙️ Configuration
│   ├── requirements.txt       # Dependencies
│   ├── .env.example           # Config template
│   └── .gitignore            # Git ignore
│
└── 🛠️ Setup Scripts
    ├── setup.bat             # Windows setup
    └── setup.sh              # Unix/Mac setup
```

## 🎓 Learning Path

### Beginner Path (1-2 hours)
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (5 min)
2. Follow [QUICKSTART.md](QUICKSTART.md) (15 min)
3. Test with [client.html](client.html) (10 min)
4. Browse [README.md](README.md) (30 min)

### Developer Path (3-4 hours)
1. Complete Beginner Path
2. Study [ARCHITECTURE.md](ARCHITECTURE.md) (45 min)
3. Read [main.py](main.py) code (45 min)
4. Experiment with [examples_llm.py](examples_llm.py) (60 min)
5. Customize [custom_llm.py](custom_llm.py) (60 min)

### Production Path (4-6 hours)
1. Complete Developer Path
2. Read production section in [README.md](README.md) (60 min)
3. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (45 min)
4. Test deployment scenarios (120 min)
5. Optimize and secure (120 min)

## 🆘 Getting Help

### Self-Service
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Review error in browser console (F12)
3. Check server logs in terminal
4. Search [README.md](README.md) for keywords

### Community Support
1. [Pipecat Discord](https://discord.gg/pipecat)
2. [GitHub Issues](https://github.com/pipecat-ai/pipecat/issues)
3. [Stack Overflow](https://stackoverflow.com/questions/tagged/pipecat)

### When Asking for Help
Include:
- Error message (from browser console and server logs)
- Python version: `python --version`
- Operating system
- What you were trying to do
- What you've already tried

## 🎉 Next Steps

Now that you know where everything is:

1. **[Run it](QUICKSTART.md)** - Get the agent working
2. **[Understand it](ARCHITECTURE.md)** - Learn how it works
3. **[Customize it](custom_llm.py)** - Make it your own
4. **[Deploy it](README.md#production-deployment)** - Go to production

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md)

**Need help?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Want to learn more?** → [README.md](README.md)
