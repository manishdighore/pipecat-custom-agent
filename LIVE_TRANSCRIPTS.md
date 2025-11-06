# Live Transcript Streaming in Pipecat

## Overview

Pipecat supports real-time transcript streaming by emitting `TranscriptionFrame` and `InterimTranscriptionFrame` objects as soon as speech is recognized. These frames can be sent to the client over the WebSocket, allowing you to display live transcripts in your UI while the user is speaking.

## How It Works

- **Speech-to-Text (STT) Service** (e.g., AzureSTTService) processes incoming audio and emits:
  - `InterimTranscriptionFrame`: Partial, in-progress transcript (updates as user speaks)
  - `TranscriptionFrame`: Final transcript for a segment/turn

- **Pipeline**: These frames are available in the Pipecat pipeline and can be intercepted by a custom FrameProcessor or sent directly to the client.

- **WebSocket Transport**: You can send transcript frames to the client as JSON messages, allowing the UI to display live updates.

## Example: Sending Transcripts to Client

In your pipeline, add a custom FrameProcessor to intercept transcript frames and send them to the client:

```python
from pipecat.frames.frames import TranscriptionFrame, InterimTranscriptionFrame
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

class TranscriptSender(FrameProcessor):
    def __init__(self, transport):
        super().__init__()
        self.transport = transport

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        if isinstance(frame, (TranscriptionFrame, InterimTranscriptionFrame)):
            # Send transcript as JSON over WebSocket
            await self.transport.send_json({
                "type": "transcript",
                "text": frame.text,
                "final": isinstance(frame, TranscriptionFrame)
            })
        else:
            await self.push_frame(frame, direction)
```

Add `TranscriptSender` to your pipeline after STT:

```python
pipeline = Pipeline([
    transport.input(),
    stt,
    TranscriptSender(transport),  # <-- Add here
    ...existing pipeline...
])
```

## Client-Side (WebSocket)

On the client, listen for transcript messages:

```js
ws.onmessage = (event) => {
    let msg = null;
    try { msg = JSON.parse(event.data); } catch {}
    if (msg && msg.type === "transcript") {
        // Display live transcript
        transcriptDiv.textContent = msg.text;
        if (msg.final) {
            // Optionally add to transcript history
        }
    }
};
```

## Notes
- Interim transcripts update in real time as the user speaks.
- Final transcripts are sent when the user stops speaking or a turn ends.
- You can display both interim and final transcripts in your UI.

## References
- [Pipecat Frame Types](https://docs.pipecat.ai/guides/learn/pipeline#pipeline-and-frame-processing)
- [Custom FrameProcessor](https://docs.pipecat.ai/guides/fundamentals/custom-frame-processor#custom-frameprocessor)
- [WebSocket Messaging](https://docs.pipecat.ai/client/js/api-reference/messages#sending-custom-messages-to-the-server)

---

This guide explains how to stream live transcripts from Pipecat to your client UI.
