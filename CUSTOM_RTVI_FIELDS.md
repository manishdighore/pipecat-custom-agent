# Custom RTVI Event Fields

This guide explains how to add custom fields (like `session_id`) to RTVI events sent from the Pipecat server to the frontend client.

## Overview

By default, RTVI events (like `onUserTranscript`, `onBotTtsText`) contain only standard fields. This implementation shows how to extend these events with custom metadata such as:
- Session IDs
- User identifiers
- Connection timestamps
- Custom application metadata

## Implementation

### Files Added

1. **`custom_rtvi_observer.py`** - Custom observer implementations
   - `CustomRTVIObserver` - Adds fields to specific event types
   - `GlobalFieldInjectorObserver` - Adds fields to ALL events

2. **`main.py`** - Updated to use custom observer with session tracking

## How It Works

### Standard RTVI Events (Before)

```json
{
  "type": "user-transcript",
  "data": {
    "text": "Hello there",
    "user_id": "default",
    "timestamp": "2025-11-09T17:30:00Z",
    "final": true
  }
}
```

### Custom RTVI Events (After)

```json
{
  "type": "user-transcript",
  "data": {
    "text": "Hello there",
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

## Usage

### Option 1: CustomRTVIObserver (Selective Control)

Use this when you want to add custom fields only to specific events.

```python
from custom_rtvi_observer import CustomRTVIObserver

# In your WebSocket endpoint:
session_id = str(uuid.uuid4())

observer = CustomRTVIObserver(
    rtvi,
    session_id=session_id,
    custom_metadata={
        "user_id": "john_doe",
        "connection_time": time.time(),
        "room": "lobby"
    }
)

task = PipelineTask(
    pipeline,
    observers=[observer]
)
```

**Events that get custom fields:**
- `user-transcript` (onUserTranscript)
- `bot-tts-text` (onBotTtsText)

### Option 2: GlobalFieldInjectorObserver (All Events)

Use this to inject custom fields into **every** RTVI message automatically.

```python
from custom_rtvi_observer import GlobalFieldInjectorObserver

observer = GlobalFieldInjectorObserver(
    rtvi,
    inject_fields={
        "session_id": session_id,
        "server_region": "us-west-2",
        "app_version": "1.0.0"
    }
)

task = PipelineTask(
    pipeline,
    observers=[observer]
)
```

**All RTVI events will include these fields in their `data` section.**

## Frontend Integration

Update your client to access the custom fields:

```javascript
import { PipecatClient, RTVIEvent } from '@pipecat-ai/client-js';

const client = new PipecatClient({
    transport: new WebSocketTransport(),
    enableMic: true,
    callbacks: {
        onUserTranscript: (data) => {
            console.log('User said:', data.text);
            console.log('Session ID:', data.session_id);  // 👈 Custom field
            console.log('Metadata:', data.metadata);      // 👈 Custom field
            
            // Use session_id for tracking, analytics, etc.
            trackUserMessage(data.session_id, data.text);
        },
        
        onBotTtsText: (data) => {
            console.log('Bot saying:', data.text);
            console.log('Session ID:', data.session_id);  // 👈 Custom field
            
            // Track agent responses by session
            trackAgentMessage(data.session_id, data.text);
        }
    }
});
```

## Customization Examples

### Example 1: Track User Information

```python
observer = CustomRTVIObserver(
    rtvi,
    session_id=session_id,
    custom_metadata={
        "user_email": user.email,
        "user_tier": user.subscription_tier,
        "connection_ip": request.client.host
    }
)
```

Frontend:
```javascript
onUserTranscript: (data) => {
    // Send to analytics
    analytics.track('user_message', {
        session: data.session_id,
        user: data.metadata.user_email,
        tier: data.metadata.user_tier
    });
}
```

### Example 2: Dynamic Session Updates

```python
# Create observer
observer = CustomRTVIObserver(rtvi, session_id=initial_session_id)

# Later, update the session ID dynamically
observer.update_session_id(new_session_id)

# Or add a new metadata field
observer.add_metadata_field("conversation_stage", "onboarding")
```

### Example 3: Multi-Tenant Application

```python
observer = CustomRTVIObserver(
    rtvi,
    session_id=session_id,
    custom_metadata={
        "tenant_id": organization.id,
        "workspace_id": workspace.id,
        "billing_plan": organization.plan
    }
)
```

### Example 4: A/B Testing

```python
import random

experiment_variant = random.choice(["control", "variant_a", "variant_b"])

observer = CustomRTVIObserver(
    rtvi,
    session_id=session_id,
    custom_metadata={
        "experiment": "llm_optimization_001",
        "variant": experiment_variant
    }
)
```

## Advanced: Custom Message Types

You can extend this further to create entirely custom message types:

```python
from pydantic import BaseModel
from pipecat.processors.frameworks.rtvi import RTVIMessage

class CustomAnalyticsMessageData(BaseModel):
    session_id: str
    event_type: str
    event_data: dict

class CustomAnalyticsMessage(RTVIMessage):
    label: str = "rtvi-ai"
    type: str = "custom-analytics"
    data: CustomAnalyticsMessageData

# In your custom observer:
async def send_analytics_event(self, event_type: str, event_data: dict):
    message = CustomAnalyticsMessage(
        data=CustomAnalyticsMessageData(
            session_id=self._session_id,
            event_type=event_type,
            event_data=event_data
        )
    )
    await self.send_rtvi_message(message)
```

## Architecture

```
┌─────────────────────────────────────────────┐
│         Pipecat Pipeline                    │
│                                             │
│  STT → User Aggregator → RTVI → LLM        │
│                           ↓                 │
│                    RTVIProcessor            │
│                           ↓                 │
│                    CustomRTVIObserver       │
│                           ↓                 │
│              _handle_user_transcriptions    │
│                           ↓                 │
│    Add session_id + metadata to event       │
│                           ↓                 │
│              send_rtvi_message              │
│                           ↓                 │
│           OutputTransportMessage            │
│                           ↓                 │
└───────────────────────────┼─────────────────┘
                            │
                            ▼
                    WebSocket Transport
                            │
                            ▼
┌───────────────────────────┼─────────────────┐
│         Frontend Client   ▼                 │
│                                             │
│  PipecatClient                              │
│       ↓                                     │
│  onUserTranscript(data)                     │
│       - data.text                           │
│       - data.session_id    ← Custom field   │
│       - data.metadata      ← Custom field   │
└─────────────────────────────────────────────┘
```

## Benefits

1. **Session Tracking** - Track conversations across multiple messages
2. **Analytics** - Correlate events with user data and experiments
3. **Multi-Tenancy** - Identify which organization/workspace events belong to
4. **Debugging** - Easier to trace issues with session identifiers
5. **Custom Logic** - Build features that depend on additional context

## TypeScript Types (Frontend)

Add these types to your frontend for proper TypeScript support:

```typescript
interface CustomUserTranscriptData {
    text: string;
    user_id: string;
    timestamp: string;
    final: boolean;
    // Custom fields
    session_id?: string;
    metadata?: {
        [key: string]: any;
    };
}

interface CustomBotTtsTextData {
    text: string;
    // Custom fields
    session_id?: string;
    metadata?: {
        [key: string]: any;
    };
}

// Usage in callbacks:
const client = new PipecatClient({
    callbacks: {
        onUserTranscript: (data: CustomUserTranscriptData) => {
            // TypeScript now knows about session_id
            console.log(data.session_id);
        }
    }
});
```

## Testing

### Test with console.log

```javascript
client.on(RTVIEvent.UserTranscript, (data) => {
    console.log('Full event data:', JSON.stringify(data, null, 2));
});
```

Expected output:
```json
{
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
```

## Performance Considerations

- **Minimal Overhead** - Adding a few fields has negligible performance impact
- **Serialization** - Fields are serialized once per event (not per frame)
- **Network** - Adds ~50-100 bytes per event depending on field values

## Security Notes

⚠️ **Be careful with sensitive data:**
- Don't include passwords or API keys in metadata
- Consider data privacy regulations (GDPR, CCPA)
- Session IDs should be unpredictable (use UUIDs)
- Sanitize any user-provided data before including

## Troubleshooting

### Custom fields not showing up

1. Check observer is actually used:
   ```python
   task = PipelineTask(pipeline, observers=[custom_observer])  # ✓
   task = PipelineTask(pipeline, observers=[RTVIObserver(rtvi)])  # ✗ Wrong
   ```

2. Verify field values are set:
   ```python
   print(f"Session ID: {session_id}")  # Should not be None
   ```

3. Check frontend callback:
   ```javascript
   console.log('Event data:', data);  // Check what you're receiving
   ```

### TypeError: model_dump() got unexpected keyword

If you see this error, you're using an older version of Pydantic. Update:
```bash
pip install --upgrade pydantic
```

### Import errors

Make sure the virtual environment is activated:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

## Next Steps

- Update `client/INTEGRATION.md` to document custom fields for frontend developers
- Add custom fields to other RTVI events (metrics, errors, etc.)
- Integrate with analytics services (Mixpanel, Segment, etc.)
- Store session data in database for conversation history

## References

- [RTVI Protocol Specification](https://docs.pipecat.ai/client/js/rtvi)
- [Pipecat Observers](https://docs.pipecat.ai/guides/fundamentals/observers)
- [Custom Frame Processors](https://docs.pipecat.ai/guides/fundamentals/custom-frame-processor)
