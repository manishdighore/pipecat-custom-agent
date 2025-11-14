# Session ID and Custom Fields Implementation Summary

## What Was Implemented

Added ability to include custom fields (like `session_id`) in RTVI events sent to the frontend client.

## Files Created/Modified

### New Files

1. **`custom_rtvi_observer.py`**
   - `CustomRTVIObserver` - Selectively adds custom fields to specific events
   - `GlobalFieldInjectorObserver` - Adds custom fields to ALL events
   - Fully documented with examples

2. **`CUSTOM_RTVI_FIELDS.md`**
   - Complete guide for adding custom fields
   - Usage examples
   - Frontend integration
   - Testing and troubleshooting

### Modified Files

1. **`main.py`**
   - Imports custom observer classes
   - Generates unique session ID per connection (UUID)
   - Creates `CustomRTVIObserver` with session_id and metadata
   - Passes custom observer to PipelineTask

2. **`client/INTEGRATION.md`**
   - Updated event schemas to show custom fields
   - Added section on accessing custom fields in callbacks
   - TypeScript type definitions
   - Use cases and examples

## How It Works

### Server Side

```python
# Generate session ID
session_id = str(uuid.uuid4())

# Create custom observer with session tracking
observer = CustomRTVIObserver(
    rtvi,
    session_id=session_id,
    custom_metadata={
        "connection_time": time.time(),
        "user_agent": "pipecat-voice-agent"
    }
)

# Use in pipeline
task = PipelineTask(pipeline, observers=[observer])
```

### Frontend Side

```javascript
onUserTranscript: (data) => {
    console.log('User:', data.text);
    console.log('Session:', data.session_id);      // ← Custom field
    console.log('Metadata:', data.metadata);       // ← Custom field
},

onBotTtsText: (data) => {
    console.log('Bot:', data.text);
    console.log('Session:', data.session_id);      // ← Custom field
}
```

## Event Payloads

### Before (Standard RTVI)

```json
{
  "type": "user-transcript",
  "data": {
    "text": "Hello",
    "user_id": "default",
    "timestamp": "2025-11-09T17:30:00Z",
    "final": true
  }
}
```

### After (With Custom Fields)

```json
{
  "type": "user-transcript",
  "data": {
    "text": "Hello",
    "user_id": "default",
    "timestamp": "2025-11-09T17:30:00Z",
    "final": true,
    "session_id": "abc-123-def-456",
    "metadata": {
      "connection_time": 1699545000.123,
      "user_agent": "pipecat-voice-agent"
    }
  }
}
```

## Implementation Approach

The solution uses **RTVIObserver subclassing**:

1. **RTVIObserver** monitors pipeline frames and converts them to RTVI messages
2. **CustomRTVIObserver** overrides `_handle_user_transcriptions()` and other handlers
3. Adds custom fields to event payloads before sending
4. Uses Pydantic models for type safety

## Two Observer Options

### Option 1: CustomRTVIObserver (Selective)
- Adds fields to specific events (user-transcript, bot-tts-text)
- More control over which events get custom data
- Lower overhead
- **Currently enabled by default in main.py**

### Option 2: GlobalFieldInjectorObserver (Global)
- Automatically injects fields into ALL RTVI messages
- Overrides `send_rtvi_message()` to modify all payloads
- Simpler if you need fields everywhere
- **Commented out in main.py, can be enabled**

## Use Cases

1. **Session Tracking** - Track full conversations across messages
2. **Analytics** - Correlate events with user data, A/B tests
3. **Multi-Tenancy** - Identify organization/workspace
4. **Debugging** - Trace issues with session IDs
5. **Custom Features** - Build features requiring additional context

## Testing

### Check Server Logs

```
INFO: Session ID: abc-123-def-456
```

### Check Frontend Console

```javascript
console.log('Event data:', data);
// Should show session_id and metadata fields
```

## Benefits

✅ **Non-intrusive** - Extends existing RTVI protocol without breaking changes  
✅ **Type-safe** - Uses Pydantic models for validation  
✅ **Flexible** - Easy to add more fields or create custom events  
✅ **Documented** - Complete guides for both server and client  
✅ **Production-ready** - Minimal performance overhead  

## Next Steps

1. **Test the implementation** - Run server and check events in browser console
2. **Customize metadata** - Add fields relevant to your application
3. **Frontend integration** - Update your UI to use session_id for tracking
4. **Analytics** - Send events with session_id to analytics platform
5. **Database** - Store conversation history keyed by session_id

## Documentation References

- **Server implementation**: `CUSTOM_RTVI_FIELDS.md`
- **Frontend integration**: `client/INTEGRATION.md`
- **Code examples**: `custom_rtvi_observer.py`
- **Main server**: `main.py` (lines 147-178)

## Architecture Diagram

```
User speaks
    ↓
STT Service (Azure)
    ↓
TranscriptionFrame
    ↓
RTVIObserver.on_push_frame()
    ↓
CustomRTVIObserver._handle_user_transcriptions()
    ↓
Add session_id + metadata to event data
    ↓
send_rtvi_message()
    ↓
OutputTransportMessageUrgentFrame
    ↓
WebSocket Transport
    ↓
Frontend client.onUserTranscript()
    ↓
Access data.session_id, data.metadata
```

## Ready to Use

The implementation is complete and ready to test:

1. Start server: `python main.py`
2. Open client: `http://localhost:8000/client` (or use your custom frontend)
3. Open browser console (F12)
4. Start session and speak
5. Check console for events with `session_id` field

---

**Questions?** See `CUSTOM_RTVI_FIELDS.md` for detailed documentation.
