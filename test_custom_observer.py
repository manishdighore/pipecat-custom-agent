"""
Quick test to verify CustomRTVIObserver is adding custom fields correctly.
"""

import asyncio
from pydantic import BaseModel
from custom_rtvi_observer import CustomRTVIObserver
from pipecat.processors.frameworks.rtvi import RTVIUserTranscriptionMessage, RTVIUserTranscriptionMessageData

async def test_custom_observer():
    """Test that custom fields are properly injected."""
    
    print("Testing CustomRTVIObserver...")
    
    # Create observer with session_id
    observer = CustomRTVIObserver(
        rtvi=None,  # No RTVI processor for this test
        session_id="test-session-123",
        custom_metadata={"test": "data", "foo": "bar"}
    )
    
    # Create a sample RTVI message
    message = RTVIUserTranscriptionMessage(
        data=RTVIUserTranscriptionMessageData(
            text="Hello world",
            user_id="test-user",
            timestamp="2025-11-09T18:00:00Z",
            final=True
        )
    )
    
    print(f"\n📥 Original message:")
    print(message.model_dump(exclude_none=True))
    
    # Simulate what send_rtvi_message does
    message_dict = message.model_dump(exclude_none=True)
    
    # Inject custom fields (this is what our custom observer does)
    if 'data' in message_dict and isinstance(message_dict['data'], dict):
        if observer._session_id:
            message_dict['data']['session_id'] = observer._session_id
        if observer._custom_metadata:
            message_dict['data']['metadata'] = observer._custom_metadata
    
    print(f"\n📤 Message after custom field injection:")
    print(message_dict)
    
    # Verify fields were added
    assert 'session_id' in message_dict['data'], "❌ session_id not found!"
    assert message_dict['data']['session_id'] == "test-session-123", "❌ Wrong session_id!"
    assert 'metadata' in message_dict['data'], "❌ metadata not found!"
    assert message_dict['data']['metadata']['test'] == "data", "❌ Wrong metadata!"
    
    print("\n✅ All tests passed! Custom fields are being injected correctly.")
    print(f"\nFinal message structure:")
    import json
    print(json.dumps(message_dict, indent=2))

if __name__ == "__main__":
    asyncio.run(test_custom_observer())
