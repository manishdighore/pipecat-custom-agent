# Frontend Integration Guide

This guide explains how to integrate the Pipecat voice agent into your own frontend application.

## Overview

The frontend uses the official **@pipecat-ai/client-js** SDK to connect to the Pipecat voice agent server via WebSocket. It handles:
- Real-time voice input/output
- Streaming transcripts (user speech → text)
- Streaming agent responses (text → speech)
- Audio playback management

## Quick Start

### 1. Install Dependencies

```bash
npm install @pipecat-ai/client-js @pipecat-ai/websocket-transport
```

### 2. Basic Setup

```javascript
import { PipecatClient, RTVIEvent } from '@pipecat-ai/client-js';
import { WebSocketTransport } from '@pipecat-ai/websocket-transport';

const client = new PipecatClient({
    transport: new WebSocketTransport(),
    enableCam: false,
    enableMic: true,
    callbacks: {
        // Your event handlers here
    }
});

// Initialize devices
await client.initDevices();

// Connect to server
await client.connect({ wsUrl: 'ws://localhost:8000/ws' });
```

## Event Handling

### Key Events for Chat UI

The following events are essential for building a streaming chat interface:

#### User Events

**`onUserTranscript`** - User's speech being transcribed
```javascript
onUserTranscript: (data) => {
    const text = data.text || '';
    const isFinal = data.final || false;
    
    // Skip final transcripts - we finalize on UserStoppedSpeaking
    if (isFinal) return;
    
    // Update streaming user message
    updateUserMessage(text, isStreaming: true);
}
```

**Event Schema:**
```typescript
{
    text: string;       // Transcribed text
    final: boolean;     // true = final version, false = partial/streaming
    user_id: string;    // User identifier
    timestamp: string;  // ISO timestamp
    // Custom fields (if using CustomRTVIObserver):
    session_id?: string;   // Session identifier
    metadata?: {           // Custom metadata
        [key: string]: any;
    };
}
```

**`onUserStartedSpeaking`** - VAD detected user started speaking
```javascript
onUserStartedSpeaking: () => {
    showSpeakingIndicator();
}
```

**`onUserStoppedSpeaking`** - VAD detected user stopped speaking
```javascript
onUserStoppedSpeaking: () => {
    hideSpeakingIndicator();
    finalizeUserMessage();  // Remove streaming cursor
}
```

#### Agent Events

**`onBotTtsText`** - Text that TTS is about to speak
```javascript
onBotTtsText: (data) => {
    const text = data.text || '';
    
    // Accumulate text in single agent message
    appendToAgentMessage(text);
}
```

**Event Schema:**
```typescript
{
    text: string;  // Text chunk from TTS
    // Custom fields (if using CustomRTVIObserver):
    session_id?: string;   // Session identifier
    metadata?: {           // Custom metadata
        [key: string]: any;
    };
}
```

**`onBotStoppedSpeaking`** - Agent finished speaking
```javascript
onBotStoppedSpeaking: () => {
    finalizeAgentMessage();  // Remove streaming cursor
}
```

#### Connection Events

**`onConnected`** - WebSocket connected successfully
```javascript
onConnected: () => {
    updateConnectionStatus('connected');
}
```

**`onBotReady`** - Bot is ready to start conversation
```javascript
onBotReady: () => {
    setupAudioTracks();
}
```

**`onDisconnected`** - Connection closed
```javascript
onDisconnected: () => {
    updateConnectionStatus('disconnected');
    cleanup();
}
```

**`onError`** - Error occurred
```javascript
onError: (error) => {
    console.error('Error:', error);
}
```

## Audio Track Management

The Pipecat client uses WebRTC tracks for audio. You must set up audio playback:

```javascript
let botAudio = null;

function setupAudioTrack(track) {
    if (!botAudio) {
        botAudio = document.createElement('audio');
        botAudio.autoplay = true;
        document.body.appendChild(botAudio);
    }
    botAudio.srcObject = new MediaStream([track]);
}

function setupMediaTracks() {
    const tracks = client.tracks();
    if (tracks.bot?.audio) {
        setupAudioTrack(tracks.bot.audio);
    }
}

// Listen for track events
client.on(RTVIEvent.TrackStarted, (track, participant) => {
    if (!participant?.local && track.kind === 'audio') {
        setupAudioTrack(track);
    }
});
```

## Message Management Pattern

### Streaming Message Updates

To achieve a ChatGPT-like streaming experience:

```javascript
let currentUserMessage = null;
let currentAgentMessage = null;
let lastUserText = '';  // Prevent duplicates

// Create a new message
function addMessage(text, type, isStreaming = false) {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.innerHTML = `
        <div class="message-header">${type === 'user' ? 'You' : 'Agent'}</div>
        <div class="message-bubble ${isStreaming ? 'streaming' : ''}">${text}</div>
        <div class="timestamp">${formatTime()}</div>
    `;
    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return message;
}

// Update existing message
function updateMessage(messageElement, text, isStreaming = false) {
    const bubble = messageElement.querySelector('.message-bubble');
    bubble.textContent = text;
    bubble.className = `message-bubble ${isStreaming ? 'streaming' : ''}`;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
```

### User Message Flow

```javascript
callbacks: {
    onUserTranscript: (data) => {
        const text = data.text || '';
        const isFinal = data.final || false;
        
        if (!text) return;
        
        // Skip duplicate finals
        if (isFinal && text === lastUserText) {
            return;
        }
        
        // Skip finals - finalize on UserStoppedSpeaking
        if (isFinal) {
            lastUserText = text;
            return;
        }
        
        // Update streaming message
        if (!currentUserMessage) {
            currentUserMessage = addMessage(text, 'user', true);
            lastUserText = text;
        } else {
            updateMessage(currentUserMessage, text, true);
            lastUserText = text;
        }
    },
    
    onUserStoppedSpeaking: () => {
        if (currentUserMessage) {
            const bubble = currentUserMessage.querySelector('.message-bubble');
            bubble.classList.remove('streaming');
            lastUserText = bubble.textContent;
            currentUserMessage = null;
        }
    }
}
```

### Agent Message Flow

```javascript
callbacks: {
    onBotTtsText: (data) => {
        const text = data.text || '';
        
        if (text) {
            // Accumulate in single message
            if (!currentAgentMessage) {
                currentAgentMessage = addMessage(text, 'agent', true);
            } else {
                const currentText = currentAgentMessage.querySelector('.message-bubble').textContent;
                updateMessage(currentAgentMessage, currentText + ' ' + text, true);
            }
        }
    },
    
    onBotStoppedSpeaking: () => {
        if (currentAgentMessage) {
            currentAgentMessage.querySelector('.message-bubble').classList.remove('streaming');
            currentAgentMessage = null;
        }
    }
}
```

## CSS for Streaming Cursor

Add a blinking cursor effect for streaming messages:

```css
.message-bubble.streaming::after {
    content: '▋';
    animation: blink 1s infinite;
    margin-left: 2px;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

## Important Implementation Notes

### 1. Skip Final User Transcripts

The server sends both partial and final transcripts. To avoid duplicates:
- Use **partial transcripts** for streaming display
- **Skip final transcripts** (`data.final === true`)
- Finalize the message in `onUserStoppedSpeaking`

### 2. Accumulate Agent Text

`onBotTtsText` fires multiple times as TTS processes chunks:
- **Accumulate all chunks** in a single message bubble
- Don't create a new message for each chunk
- Append with spaces: `currentText + ' ' + newText`

### 3. Prevent Duplicate Messages

Track the last user text to prevent duplicates:
```javascript
let lastUserText = '';

if (isFinal && text === lastUserText) {
    return;  // Skip duplicate
}
```

### 4. Audio Element Required

The bot's voice comes through a MediaStream, not WebSocket audio data:
- Create an `<audio>` element with `autoplay`
- Set `srcObject` to the bot's audio track
- Listen for `RTVIEvent.TrackStarted` to capture tracks

### 5. Initialize Devices First

Always call `initDevices()` before `connect()`:
```javascript
await client.initDevices();  // MUST be first
await client.connect({ wsUrl: 'ws://localhost:8000/ws' });
```

## Event Filtering for Debugging

To see only relevant events in console:

```javascript
const relevantEvents = Object.values(RTVIEvent).filter(e => 
    e.includes('Bot') || e.includes('User') || e.includes('Transcript')
);

relevantEvents.forEach(eventName => {
    client.on(eventName, (...args) => {
        console.log(`🎯 ${eventName}:`, ...args);
    });
});
```

## Complete Minimal Example

```javascript
import { PipecatClient, RTVIEvent } from '@pipecat-ai/client-js';
import { WebSocketTransport } from '@pipecat-ai/websocket-transport';

let client = null;
let currentUserMessage = null;
let currentAgentMessage = null;
let lastUserText = '';
let botAudio = null;

async function startSession() {
    client = new PipecatClient({
        transport: new WebSocketTransport(),
        enableCam: false,
        enableMic: true,
        callbacks: {
            onUserTranscript: (data) => {
                const text = data.text || '';
                const isFinal = data.final || false;
                
                if (!text || isFinal) return;
                
                if (!currentUserMessage) {
                    currentUserMessage = addMessage(text, 'user', true);
                } else {
                    updateMessage(currentUserMessage, text, true);
                }
                lastUserText = text;
            },
            
            onUserStoppedSpeaking: () => {
                if (currentUserMessage) {
                    finalizeMessage(currentUserMessage);
                    currentUserMessage = null;
                }
            },
            
            onBotTtsText: (data) => {
                const text = data.text || '';
                if (!text) return;
                
                if (!currentAgentMessage) {
                    currentAgentMessage = addMessage(text, 'agent', true);
                } else {
                    const current = currentAgentMessage.querySelector('.message-bubble').textContent;
                    updateMessage(currentAgentMessage, current + ' ' + text, true);
                }
            },
            
            onBotStoppedSpeaking: () => {
                if (currentAgentMessage) {
                    finalizeMessage(currentAgentMessage);
                    currentAgentMessage = null;
                }
            },
            
            onBotReady: () => {
                const tracks = client.tracks();
                if (tracks.bot?.audio) {
                    if (!botAudio) {
                        botAudio = document.createElement('audio');
                        botAudio.autoplay = true;
                        document.body.appendChild(botAudio);
                    }
                    botAudio.srcObject = new MediaStream([tracks.bot.audio]);
                }
            }
        }
    });
    
    await client.initDevices();
    await client.connect({ wsUrl: 'ws://localhost:8000/ws' });
}

function addMessage(text, type, isStreaming) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.innerHTML = `
        <div class="message-bubble ${isStreaming ? 'streaming' : ''}">${text}</div>
    `;
    document.getElementById('messages').appendChild(msg);
    return msg;
}

function updateMessage(element, text, isStreaming) {
    const bubble = element.querySelector('.message-bubble');
    bubble.textContent = text;
    bubble.className = `message-bubble ${isStreaming ? 'streaming' : ''}`;
}

function finalizeMessage(element) {
    element.querySelector('.message-bubble').classList.remove('streaming');
}
```

## Troubleshooting

### No audio playback
- Check that audio element has `autoplay` attribute
- Verify bot audio track is set in `onBotReady`
- Listen for `RTVIEvent.TrackStarted` events

### Duplicate user messages
- Ensure you're skipping final transcripts (`if (isFinal) return`)
- Track last user text to prevent duplicates
- Only create new messages for partial transcripts

### Agent messages not accumulating
- Verify you're using `onBotTtsText` (not `onBotTranscript`)
- Check you're appending text: `currentText + ' ' + newText`
- Don't create new message for each TTS chunk

### Messages out of order
- Ensure timestamps are added at creation time
- Scroll container to bottom after each update
- Don't batch DOM updates

## Custom Fields in Events

This server implementation supports custom fields in RTVI events (like `session_id`).

### Accessing Custom Fields

```javascript
onUserTranscript: (data) => {
    const text = data.text || '';
    const sessionId = data.session_id;  // Custom field
    const metadata = data.metadata;      // Custom metadata object
    
    if (sessionId) {
        // Track by session
        console.log(`[Session ${sessionId}] User: ${text}`);
        
        // Send to analytics
        analytics.track('user_message', {
            session: sessionId,
            text: text,
            metadata: metadata
        });
    }
},

onBotTtsText: (data) => {
    const text = data.text || '';
    const sessionId = data.session_id;  // Custom field
    
    if (sessionId) {
        console.log(`[Session ${sessionId}] Bot: ${text}`);
    }
}
```

### TypeScript Types

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

// Use in callbacks
const client = new PipecatClient({
    callbacks: {
        onUserTranscript: (data: CustomUserTranscriptData) => {
            console.log('Session:', data.session_id);
            console.log('Metadata:', data.metadata);
        }
    }
});
```

### Use Cases

1. **Session Tracking** - Track conversation flows across multiple messages
2. **Analytics** - Correlate events with user segments and experiments
3. **Multi-Tenancy** - Identify which organization events belong to
4. **Debugging** - Trace issues with unique session identifiers

## Server-Side Requirements

Your Pipecat server must:
1. Use `ProtobufFrameSerializer` for WebSocket transport
2. Include `RTVIProcessor` in the pipeline for event emission
3. Position `RTVIProcessor` before LLM to capture transcript events
4. Use Azure STT/TTS or compatible services
5. (Optional) Use `CustomRTVIObserver` for custom event fields - see `CUSTOM_RTVI_FIELDS.md`

## Further Reading

- [Pipecat Client SDK Docs](https://docs.pipecat.ai/client/js)
- [RTVI Protocol](https://docs.pipecat.ai/client/js/rtvi)
- [WebSocket Transport](https://docs.pipecat.ai/client/js/transports/websocket)
- [Custom RTVI Fields](../CUSTOM_RTVI_FIELDS.md) - Server-side implementation guide
