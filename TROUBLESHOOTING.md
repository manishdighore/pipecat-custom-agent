# Troubleshooting Guide

Common issues and their solutions for the Pipecat Voice Agent.

## Installation Issues

### Problem: `pip install` fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement pipecat-ai
```

**Solution:**
1. Check Python version: `python --version` (need 3.10+)
2. Upgrade pip: `pip install --upgrade pip`
3. Try with specific version: `pip install pipecat-ai==0.0.90`

### Problem: Azure dependencies fail to install

**Error:**
```
ERROR: Failed building wheel for azure-cognitiveservices-speech
```

**Solution (Windows):**
1. Install Visual C++ Build Tools
2. Or use pre-built wheels: `pip install --only-binary :all: pipecat-ai[azure]`

**Solution (Linux):**
```bash
sudo apt-get install build-essential libssl-dev
pip install pipecat-ai[azure]
```

**Solution (macOS):**
```bash
brew install openssl
pip install pipecat-ai[azure]
```

## Configuration Issues

### Problem: Azure authentication fails

**Error:**
```
ERROR: Azure credentials not configured
```

**Solution:**
1. Create `.env` file from `.env.example`
2. Add your credentials:
   ```
   AZURE_SPEECH_API_KEY=your_actual_key
   AZURE_SPEECH_REGION=eastus
   ```
3. Verify key is valid in Azure Portal
4. Check region matches your resource

### Problem: Environment variables not loading

**Error:**
```
AZURE_SPEECH_API_KEY returns None
```

**Solution:**
1. Ensure `.env` file is in the same directory as `main.py`
2. Check file is named exactly `.env` (not `.env.txt`)
3. Verify no spaces around `=` in `.env`
4. Restart the server after editing `.env`

## Server Issues

### Problem: Server won't start

**Error:**
```
ImportError: No module named 'pipecat'
```

**Solution:**
1. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
2. Reinstall dependencies: `pip install -r requirements.txt`

### Problem: Port already in use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
1. Change port in `.env`:
   ```
   PORT=8001
   ```
2. Or kill process using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>
   ```

### Problem: Server crashes on startup

**Error:**
```
Exception: Missing module: azure
```

**Solution:**
1. Install Azure extras: `pip install pipecat-ai[azure]`
2. Or install all extras: `pip install pipecat-ai[all]`

## WebSocket Connection Issues

### Problem: Can't connect to WebSocket

**Symptoms:**
- Client shows "Connecting..." forever
- Browser console shows connection error

**Solution:**
1. Verify server is running: Check terminal for "Uvicorn running..."
2. Check URL matches server: `ws://localhost:8000/ws`
3. Clear browser cache and reload
4. Try different browser
5. Check firewall isn't blocking port 8000

### Problem: WebSocket disconnects immediately

**Error in browser console:**
```
WebSocket connection closed: code 1011
```

**Solution:**
1. Check server logs for detailed error
2. Verify Azure credentials are correct
3. Ensure .env file exists and is loaded
4. Check for exceptions in custom_llm.py

## Audio Issues

### Problem: Microphone not working

**Symptoms:**
- "Hold to Talk" button does nothing
- Browser doesn't ask for microphone permission

**Solution:**
1. Use HTTPS or localhost (HTTP only works on localhost)
2. Check browser microphone permissions in settings
3. Try different browser (Chrome/Firefox recommended)
4. Verify microphone works in other apps
5. Check browser console for detailed errors

### Problem: No audio response

**Symptoms:**
- Server processes request but no sound plays

**Solution:**
1. Check browser volume isn't muted
2. Verify Azure TTS credentials are correct
3. Check server logs for TTS errors:
   ```
   ERROR: Speech synthesis canceled
   ```
4. Test with different text in custom_llm.py
5. Verify audio output device is working

### Problem: Audio is choppy or distorted

**Solution:**
1. Check network connection (WebSocket requires stable connection)
2. Reduce audio quality in client if needed
3. Check CPU usage on server
4. Verify Azure region is geographically close
5. Try reducing VAD `stop_secs` in main.py

## Speech Recognition Issues

### Problem: STT not recognizing speech

**Symptoms:**
- User speaks but no transcription appears

**Solution:**
1. Check microphone is capturing audio
2. Speak clearly and louder
3. Reduce background noise
4. Adjust VAD settings in main.py:
   ```python
   VADParams(
       stop_secs=0.5,  # Try 0.3 or 0.7
       min_volume=0.6,  # Try 0.4
   )
   ```
5. Check Azure STT logs for errors

### Problem: Wrong language being recognized

**Solution:**
1. Set correct language in main.py:
   ```python
   stt = AzureSTTService(
       language=Language.EN_US,  # or Language.ES_ES, etc.
   )
   ```
2. Check available languages in Azure documentation

## Custom LLM Issues

### Problem: LLM not responding

**Symptoms:**
- STT works but no response generated

**Solution:**
1. Check custom_llm.py for errors
2. Verify `generate_response` method has no exceptions
3. Add debug logging:
   ```python
   logger.debug(f"Generating response for: {user_message}")
   ```
4. Test with simple static response first

### Problem: LLM response not streaming

**Symptoms:**
- Long delay then all audio at once

**Solution:**
1. Verify using `yield` in `generate_response`:
   ```python
   async def generate_response(self, user_message):
       for chunk in response.split():
           yield chunk + " "
           await asyncio.sleep(0.05)
   ```
2. Check TTS is not buffering entire response

### Problem: LLM responses are cut off

**Solution:**
1. Ensure `LLMFullResponseEndFrame()` is sent
2. Check for exceptions in generate_response
3. Verify all async generators are properly closed

## Performance Issues

### Problem: High latency (> 2 seconds)

**Solution:**
1. Check Azure region is geographically close
2. Optimize LLM response generation
3. Reduce text length before TTS
4. Use faster Azure voice models
5. Check server CPU/memory usage

### Problem: Server using too much memory

**Solution:**
1. Restart server regularly in production
2. Limit conversation history length
3. Clear audio buffers between sessions
4. Use streaming instead of buffering

## Production Deployment Issues

### Problem: HTTPS required for microphone

**Solution:**
1. Use Let's Encrypt for free SSL certificate
2. Or deploy behind reverse proxy (nginx/caddy)
3. Example nginx config:
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location /ws {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

### Problem: WebSocket timeout in production

**Solution:**
1. Increase timeout in Uvicorn:
   ```python
   uvicorn.run(app, timeout_keep_alive=120)
   ```
2. Add WebSocket ping/pong
3. Implement reconnection logic in client

## Debugging Tips

### Enable detailed logging

In main.py:
```python
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```

### Check server logs

Look for:
- Exception tracebacks
- Azure API errors
- Pipeline errors
- WebSocket connection status

### Check browser console

Look for:
- WebSocket errors
- Audio errors
- JavaScript exceptions
- Network errors

### Test components individually

1. Test Azure STT:
   ```python
   # Use Azure Speech SDK directly
   ```

2. Test Azure TTS:
   ```python
   # Generate audio file
   ```

3. Test custom LLM:
   ```python
   # Run generate_response() directly
   ```

4. Test WebSocket:
   ```python
   # Use websocat or similar tool
   ```

## Getting More Help

### Check logs in order:

1. **Browser Console** (F12)
   - WebSocket errors
   - JavaScript errors
   - Network tab for WS connection

2. **Server Logs** (Terminal)
   - Python exceptions
   - Azure API errors
   - Pipeline errors

3. **Pipecat Logs**
   - Frame processing
   - Service errors

### Common Log Messages

**"Client connected"** ✓
- WebSocket connection successful

**"Azure STT service initialized"** ✓
- STT ready to process audio

**"Generating response for: ..."** ✓
- LLM received user message

**"ERROR: Speech synthesis canceled"** ✗
- Check Azure TTS credentials/quota

**"WebSocket error: ..."** ✗
- Check connection stability

### Still stuck?

1. Check README.md for detailed documentation
2. Review ARCHITECTURE.md for system flow
3. Look at examples_llm.py for different LLM approaches
4. Visit Pipecat Discord: https://discord.gg/pipecat
5. Check Pipecat GitHub issues: https://github.com/pipecat-ai/pipecat/issues
6. Review Azure Speech documentation

## Quick Diagnostic Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] .env file exists with correct credentials
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/health
- [ ] Browser allows microphone access
- [ ] WebSocket connects successfully
- [ ] Audio can be recorded
- [ ] Audio can be played
- [ ] Azure services are responding

If all checked and still having issues, provide:
1. Error message from server logs
2. Error from browser console
3. Python version
4. Operating system
5. What you were trying to do

---

Most issues are resolved by:
1. Checking .env configuration
2. Verifying Azure credentials
3. Ensuring dependencies are installed
4. Activating virtual environment
5. Checking browser permissions
