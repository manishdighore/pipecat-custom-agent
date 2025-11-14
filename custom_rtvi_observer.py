"""
Custom RTVI Observer with additional fields in event payloads.

This module demonstrates how to extend the RTVIObserver to add custom fields
(like session_id) to RTVI events sent to the frontend.
"""

from typing import Optional
from pydantic import BaseModel

from pipecat.frames.frames import Frame, TranscriptionFrame, InterimTranscriptionFrame, TTSTextFrame, LLMTextFrame
from pipecat.processors.frameworks.rtvi import (
    RTVIObserver,
    RTVIObserverParams,
    RTVIUserTranscriptionMessage,
    RTVIBotTTSTextMessage,
    RTVIBotLLMTextMessage,
    RTVITextMessageData,
)
from pipecat.transports.base_output import BaseOutputTransport


class CustomRTVIObserver(RTVIObserver):
    """
    Custom RTVI Observer that adds session_id and other custom fields to event payloads.
    
    This observer injects custom fields by overriding send_rtvi_message to modify
    the message dict before sending it to the client.
    
    Example:
        observer = CustomRTVIObserver(
            rtvi=rtvi_processor,
            session_id="my-session-123",
            custom_metadata={"user": "john", "room": "lobby"}
        )
        
        task = PipelineTask(
            pipeline,
            observers=[observer]
        )
    """
    
    def __init__(
        self,
        rtvi: Optional["RTVIProcessor"] = None,
        *,
        session_id: Optional[str] = None,
        custom_metadata: Optional[dict] = None,
        params: Optional[RTVIObserverParams] = None,
        **kwargs,
    ):
        """
        Initialize the custom RTVI observer.
        
        Args:
            rtvi: The RTVI processor to push frames to.
            session_id: Session identifier to add to all events.
            custom_metadata: Additional metadata to include in events.
            params: Settings to enable/disable specific messages.
            **kwargs: Additional arguments passed to parent class.
        """
        super().__init__(rtvi, params=params, **kwargs)
        self._session_id = session_id
        self._custom_metadata = custom_metadata or {}
    
    async def send_rtvi_message(self, model: BaseModel, exclude_none: bool = True):
        """
        Send an RTVI message with injected custom fields.
        
        This overrides the default implementation to inject session_id and metadata
        into the message data before sending.
        """
        # Get the message dict
        message_dict = model.model_dump(exclude_none=exclude_none)
        
        # Inject custom fields into the 'data' section if it exists
        if 'data' in message_dict and isinstance(message_dict['data'], dict):
            # Add session_id if set
            if self._session_id:
                message_dict['data']['session_id'] = self._session_id
            
            # Add metadata if set
            if self._custom_metadata:
                message_dict['data']['metadata'] = self._custom_metadata
        
        # Push the modified message
        if self._rtvi:
            from pipecat.frames.frames import OutputTransportMessageUrgentFrame
            frame = OutputTransportMessageUrgentFrame(message=message_dict)
            await self._rtvi.push_frame(frame)
    
    def update_session_id(self, session_id: str):
        """
        Update the session ID dynamically.
        
        Args:
            session_id: New session identifier.
        """
        self._session_id = session_id
    
    def update_metadata(self, metadata: dict):
        """
        Update custom metadata dynamically.
        
        Args:
            metadata: New metadata dictionary.
        """
        self._custom_metadata = metadata
    
    def add_metadata_field(self, key: str, value: any):
        """
        Add or update a single metadata field.
        
        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self._custom_metadata[key] = value


# Alternative approach: Global custom field injector
# This wraps send_rtvi_message to inject fields into ALL messages

class GlobalFieldInjectorObserver(RTVIObserver):
    """
    Alternative approach: Inject custom fields into ALL RTVI messages.
    
    This observer automatically adds custom fields to every RTVI message payload
    by overriding the send_rtvi_message method.
    
    Example:
        observer = GlobalFieldInjectorObserver(
            rtvi=rtvi_processor,
            inject_fields={"session_id": "abc123", "user_id": "john"}
        )
    """
    
    def __init__(
        self,
        rtvi: Optional["RTVIProcessor"] = None,
        *,
        inject_fields: Optional[dict] = None,
        params: Optional[RTVIObserverParams] = None,
        **kwargs,
    ):
        """
        Initialize the global field injector observer.
        
        Args:
            rtvi: The RTVI processor to push frames to.
            inject_fields: Dictionary of fields to inject into all messages.
            params: Settings to enable/disable specific messages.
            **kwargs: Additional arguments passed to parent class.
        """
        super().__init__(rtvi, params=params, **kwargs)
        self._inject_fields = inject_fields or {}
    
    async def send_rtvi_message(self, model: BaseModel, exclude_none: bool = True):
        """
        Send an RTVI message with injected custom fields.
        
        This overrides the default implementation to inject custom fields
        into the message data before sending.
        """
        # Get the message dict
        message_dict = model.model_dump(exclude_none=exclude_none)
        
        # Inject custom fields into the 'data' section if it exists
        if 'data' in message_dict and isinstance(message_dict['data'], dict):
            message_dict['data'].update(self._inject_fields)
        
        # Push the modified message
        if self._rtvi:
            from pipecat.frames.frames import OutputTransportMessageUrgentFrame
            frame = OutputTransportMessageUrgentFrame(message=message_dict)
            await self._rtvi.push_frame(frame)
    
    def update_inject_fields(self, fields: dict):
        """
        Update the fields to inject.
        
        Args:
            fields: New dictionary of fields to inject.
        """
        self._inject_fields = fields
