# Voice Agent Data Flow

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Browser Client)                        │
│                                                                     │
│  ┌──────────────┐        ┌──────────────┐      ┌────────────────┐ │
│  │  Microphone  │───────▶│  JavaScript  │◀────▶│   Speaker      │ │
│  │  (Input)     │        │  WebSocket   │      │   (Output)     │ │
│  └──────────────┘        └──────┬───────┘      └────────────────┘ │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                                 │ WebSocket
                                 │ ws://localhost:8000/ws
                                 │
┌────────────────────────────────┼─────────────────────────────────┐
│                        SERVER (FastAPI)                           │
│                                ▼                                  │
│                    ┌───────────────────────┐                      │
│                    │  WebSocket Transport  │                      │
│                    │  (FastAPI)            │                      │
│                    └──────┬─────────┬──────┘                      │
│                           │         │                             │
│                      Input│         │Output                       │
│                           │         │                             │
│              ┌────────────▼─────────▼────────────┐                │
│              │      PIPECAT PIPELINE             │                │
│              │                                   │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 1. Audio Input              │  │                │
│              │  │    (Raw audio bytes)        │  │                │
│              │  └──────────┬──────────────────┘  │                │
│              │             ▼                     │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 2. Azure STT Service        │  │                │
│              │  │    Speech → Text            │  │                │
│              │  │    "Hello, how are you?"    │  │                │
│              │  └──────────┬──────────────────┘  │                │
│              │             ▼                     │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 3. Context Aggregator       │  │                │
│              │  │    (User message)           │  │                │
│              │  │    Manages conversation     │  │                │
│              │  └──────────┬──────────────────┘  │                │
│              │             ▼                     │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 4. Custom LLM Service       │  │                │
│              │  │    Text → Text Stream       │  │                │
│              │  │    "I'm doing great..."     │  │                │
│              │  └──────────┬──────────────────┘  │                │
│              │             ▼                     │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 5. Azure TTS Service        │  │                │
│              │  │    Text → Speech            │  │                │
│              │  │    (Audio chunks)           │  │                │
│              │  └──────────┬──────────────────┘  │                │
│              │             ▼                     │                │
│              │  ┌─────────────────────────────┐  │                │
│              │  │ 6. Audio Output             │  │                │
│              │  │    (Streams back to client) │  │                │
│              │  └─────────────────────────────┘  │                │
│              │             │                     │                │
│              │  ┌──────────▼──────────────────┐  │                │
│              │  │ 7. Context Aggregator       │  │                │
│              │  │    (Assistant message)      │  │                │
│              │  └─────────────────────────────┘  │                │
│              │                                   │                │
│              └───────────────────────────────────┘                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Message Flow Example

### User Says: "Hello, how are you?"

```
1. Browser captures audio
   ↓
2. Audio sent via WebSocket as binary data
   ↓
3. Server receives audio in transport.input()
   ↓
4. Azure STT processes audio
   Output: TranscriptionFrame("Hello, how are you?")
   ↓
5. Context Aggregator adds to conversation
   Context: [{"role": "user", "content": "Hello, how are you?"}]
   ↓
6. Custom LLM generates streaming response
   Yields: "I'm " → "doing " → "great, " → "thank " → "you! " → ...
   ↓
7. Each text chunk sent to Azure TTS
   Converts: "I'm doing" → [audio_chunk_1]
             "great, thank" → [audio_chunk_2]
             "you!" → [audio_chunk_3]
   ↓
8. Audio chunks sent to transport.output()
   ↓
9. WebSocket sends audio to browser
   ↓
10. Browser plays audio in real-time
    User hears: "I'm doing great, thank you!"
```

## Component Interaction

```
┌──────────────────┐
│   custom_llm.py  │
│                  │
│  Custom LLM      │──┐
│  - Receives text │  │
│  - Generates     │  │
│    streaming     │  │
│    response      │  │
└──────────────────┘  │
                      │
                      │ Used by
                      │
┌──────────────────┐  │
│     main.py      │  │
│                  │  │
│  FastAPI Server  │◀─┘
│  - WebSocket     │
│  - Pipeline      │──┐
│  - Azure STT     │  │
│  - Azure TTS     │  │
└──────────────────┘  │
         │            │
         │ Serves     │
         ▼            │
┌──────────────────┐  │
│   client.html    │  │
│                  │  │
│  Web Interface   │  │
│  - Audio capture │  │
│  - WebSocket     │  │
│  - Audio playback│  │
└──────────────────┘  │
         │            │
         │ Uses       │
         ▼            │
┌──────────────────┐  │
│  .env file       │◀─┘
│                  │
│  Azure Creds     │
│  - API Key       │
│  - Region        │
└──────────────────┘
```

## Frame Types in Pipeline

```
Audio Flow:
AudioRawFrame ──▶ [STT] ──▶ TranscriptionFrame ──▶ [Context] ──▶ LLMContextFrame
                                                                        │
                                                                        ▼
TTSAudioRawFrame ◀── [TTS] ◀── TextFrame ◀── [LLM] ◀── LLMFullResponseStartFrame
```

## State Machine

```
┌─────────────┐
│ Disconnected│
└──────┬──────┘
       │ User clicks "Connect"
       ▼
┌─────────────┐
│ Connected   │◀──┐
└──────┬──────┘   │
       │          │ Conversation continues
       │          │
       │ User holds "Talk"
       ▼          │
┌─────────────┐   │
│ Recording   │   │
└──────┬──────┘   │
       │          │
       │ User releases button
       ▼          │
┌─────────────┐   │
│ Processing  │   │
│ (STT→LLM→TTS)   │
└──────┬──────┘   │
       │          │
       │ Audio plays
       ▼          │
┌─────────────┐   │
│ Playing     │───┘
│ Response    │
└─────────────┘
```

## Error Handling Flow

```
Error Occurs
    │
    ├── Azure STT Error ──▶ Log + Retry
    │
    ├── Azure TTS Error ──▶ Log + Retry
    │
    ├── LLM Error ──────▶ Log + Fallback Response
    │
    ├── WebSocket Disconnect ──▶ Cleanup + Close Pipeline
    │
    └── General Exception ──▶ Log + EndFrame + Cleanup
```

## Timing Diagram

```
Time →
User:     [Speak: 2s]───────────[Listen: 3s]───────────
          │                     │
WebSocket:│                     │
          [Send Audio]──────┐   [Receive Audio]
                           │   │
Server:                    │   │
                           ▼   │
          [STT: 200ms]─────────┤
          [LLM: 500ms]─────────┤
          [TTS: 300ms]─────────┤
                               │
Total Latency: ~1000ms ────────┘
```

## Key Performance Metrics

- **TTFB (Time to First Byte)**: ~200-500ms
  - Time from user stops speaking to first audio response
  
- **End-to-End Latency**: ~800-1200ms
  - Complete round trip including STT, LLM, and TTS

- **Streaming**: Text and audio stream in real-time
  - User hears response while it's still being generated

---

This diagram shows the complete data flow through your voice agent system.
