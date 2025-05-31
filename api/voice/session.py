import json
from typing import Literal, Union
from prompty.tracer import trace
from api.connection import Connection
from fastapi import WebSocketDisconnect
from fastapi.websockets import WebSocketState
from api.agent.common import create_thread_message

from openai.resources.beta.realtime.realtime import (
    AsyncRealtimeConnection,
)
from openai.types.beta.realtime.session_update_event import (
    Session,
    SessionTurnDetection,
    SessionInputAudioTranscription,
    SessionTool,
)
from openai.types.beta.realtime import (
    ErrorEvent,
    SessionCreatedEvent,
    SessionUpdatedEvent,
    ConversationCreatedEvent,
    ConversationItemCreatedEvent,
    ConversationItemInputAudioTranscriptionCompletedEvent,
    ConversationItemInputAudioTranscriptionFailedEvent,
    ConversationItemInputAudioTranscriptionDeltaEvent,
    ConversationItemTruncatedEvent,
    ConversationItemDeletedEvent,
    InputAudioBufferCommittedEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferSpeechStartedEvent,
    InputAudioBufferSpeechStoppedEvent,
    ResponseCreatedEvent,
    ResponseDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    RateLimitsUpdatedEvent,
)

from openai.types.beta.realtime import (
    SessionUpdateEvent,
    InputAudioBufferAppendEvent,
    # InputAudioBufferCommitEvent,
    # InputAudioBufferClearEvent,
    ConversationItemCreateEvent,
    # ConversationItemTruncateEvent,
    # ConversationItemDeleteEvent,
    ResponseCreateEvent,
    # ResponseCancelEvent,
)

from openai.types.beta.realtime import (
    ConversationItem,
    ConversationItemContent,
)

from api.model import Update


class RealtimeSession:
    """
    Realtime session for handling websocket connections and messages.
    """

    def __init__(
        self,
        realtime: AsyncRealtimeConnection,
        client: Connection,
        thread_id: Union[str, None] = None,
    ):
        self.realtime: AsyncRealtimeConnection = realtime
        self.connection: Connection = client
        self.response_queue: list[ConversationItemCreateEvent] = []
        self.active = True
        self.thread_id = thread_id

    async def update_realtime_session(
        self,
        instructions: str,
        detection_type: Literal["semantic_vad", "server_vad"] = "semantic_vad",
        transcription_model: str = "whisper-1",
        threshold: float = 0.8,
        silence_duration_ms: int = 500,
        prefix_padding_ms: int = 300,
        eagerness: Literal["low", "medium", "high", "auto"] = "auto",
        voice: str = "sage",
        tools: list[SessionTool] = [],
    ):
        if self.realtime is not None:

            vad: SessionTurnDetection | None = None
            if detection_type == "semantic_vad":
                vad = SessionTurnDetection(
                    type=detection_type,
                    eagerness=eagerness,
                    create_response=True,
                    interrupt_response=True,
                )

            elif detection_type == "server_vad":
                vad = SessionTurnDetection(
                    type=detection_type,
                    threshold=threshold,
                    silence_duration_ms=silence_duration_ms,
                    prefix_padding_ms=prefix_padding_ms,
                )
            else:
                raise ValueError(
                    f"Invalid detection type: {detection_type}. "
                    "Must be 'semantic_vad' or 'server_vad'."
                )

            session: Session = Session(
                input_audio_format="pcm16",
                turn_detection=vad,
                input_audio_transcription=SessionInputAudioTranscription(
                    model=transcription_model,
                ),
                voice=voice,
                instructions=instructions,
                modalities=["text", "audio"],
                tool_choice="auto",
                tools=tools,
            )
            await self.realtime.send(
                SessionUpdateEvent(
                    type="session.update",
                    session=session,
                )
            )

    @trace
    async def receive_realtime(self):
        # signature = "api.session.RealtimeSession.receive_realtime"
        # while self.realtime is not None:
        async for event in self.realtime:
            if "delta" not in event.type:
                print(event.type)
            self.active = True
            if (
                self.realtime is None
                or self.connection.state != WebSocketState.CONNECTED
            ):
                break

            match event.type:
                case "error":
                    print(json.dumps(event.model_dump(), indent=2))
                    # await self._handle_error(event)
                case "session.created":
                    await self._session_created(event)
                case "session.updated":
                    await self._session_updated(event)
                case "conversation.created":
                    await self._conversation_created(event)
                case "conversation.item.created":
                    await self._conversation_item_created(event)
                case "conversation.item.input_audio_transcription.completed":
                    await self._conversation_item_input_audio_transcription_completed(
                        event
                    )
                case "conversation.item.input_audio_transcription.delta":
                    await self._conversation_item_input_audio_transcription_delta(event)
                case "conversation.item.input_audio_transcription.failed":
                    await self._conversation_item_input_audio_transcription_failed(
                        event
                    )
                case "conversation.item.truncated":
                    await self._conversation_item_truncated(event)
                case "conversation.item.deleted":
                    await self._conversation_item_deleted(event)
                case "input_audio_buffer.committed":
                    await self._input_audio_buffer_committed(event)
                case "input_audio_buffer.cleared":
                    await self._input_audio_buffer_cleared(event)
                case "input_audio_buffer.speech_started":
                    await self._input_audio_buffer_speech_started(event)
                case "input_audio_buffer.speech_stopped":
                    await self._input_audio_buffer_speech_stopped(event)
                case "response.created":
                    await self._response_created(event)
                case "response.done":
                    await self._response_done(event)
                case "response.output_item.added":
                    await self._response_output_item_added(event)
                case "response.output_item.done":
                    await self._response_output_item_done(event)
                case "response.content_part.added":
                    await self._response_content_part_added(event)
                case "response.content_part.done":
                    await self._response_content_part_done(event)
                case "response.text.delta":
                    await self._response_text_delta(event)
                case "response.text.done":
                    await self._response_text_done(event)
                case "response.audio_transcript.delta":
                    await self._response_audio_transcript_delta(event)
                case "response.audio_transcript.done":
                    await self._response_audio_transcript_done(event)
                case "response.audio.delta":
                    await self._response_audio_delta(event)
                case "response.audio.done":
                    await self._response_audio_done(event)
                case "response.function_call_arguments.delta":
                    await self._response_function_call_arguments_delta(event)
                case "response.function_call_arguments.done":
                    await self._response_function_call_arguments_done(event)
                case "rate_limits.updated":
                    await self._rate_limits_updated(event)
                case _:
                    print(
                        f"Unhandled event type {event.type}",
                    )

    @trace(name="error")
    async def _handle_error(self, event: ErrorEvent):
        print("Error event", event.error)

    @trace(name="session.created")
    async def _session_created(self, event: SessionCreatedEvent):
        pass

    @trace(name="session.updated")
    async def _session_updated(self, event: SessionUpdatedEvent):
        pass

    @trace(name="conversation.created")
    async def _conversation_created(self, event: ConversationCreatedEvent):
        pass

    @trace(name="conversation.item.created")
    async def _conversation_item_created(self, event: ConversationItemCreatedEvent):
        pass

    @trace(name="conversation.item.input_audio_transcription.completed")
    async def _conversation_item_input_audio_transcription_completed(
        self, event: ConversationItemInputAudioTranscriptionCompletedEvent
    ):
        if event.transcript is None or len(event.transcript.strip()) == 0:
            return

        await self.connection.send_update(
            Update.message(
                id=event.item_id,
                role="user",
                content=event.transcript.strip(),
            )
        )

        if self.thread_id is not None:
            await create_thread_message(
                thread_id=self.thread_id,
                role="user",
                content=event.transcript.strip(),
                metadata={
                    "id": event.item_id,
                    "event": "conversation.item.input_audio_transcription.completed",
                    "source": "realtime",
                },
            )

    async def _conversation_item_input_audio_transcription_delta(
        self, event: ConversationItemInputAudioTranscriptionDeltaEvent
    ):
        pass

    @trace(name="conversation.item.input_audio_transcription.failed")
    async def _conversation_item_input_audio_transcription_failed(
        self, event: ConversationItemInputAudioTranscriptionFailedEvent
    ):
        pass

    @trace(name="conversation.item.truncated")
    async def _conversation_item_truncated(self, event: ConversationItemTruncatedEvent):
        pass

    @trace(name="conversation.item.deleted")
    async def _conversation_item_deleted(self, event: ConversationItemDeletedEvent):
        pass

    @trace(name="input_audio_buffer.committed")
    async def _input_audio_buffer_committed(
        self, event: InputAudioBufferCommittedEvent
    ):
        pass

    @trace(name="input_audio_buffer.cleared")
    async def _input_audio_buffer_cleared(self, event: InputAudioBufferClearedEvent):
        pass

    @trace(name="input_audio_buffer.speech_started")
    async def _input_audio_buffer_speech_started(
        self, event: InputAudioBufferSpeechStartedEvent
    ):
        await self.connection.send_update(Update.interrupt())

    @trace(name="input_audio_buffer.speech_stopped")
    async def _input_audio_buffer_speech_stopped(
        self, event: InputAudioBufferSpeechStoppedEvent
    ):
        pass

    @trace(name="response.created")
    async def _response_created(self, event: ResponseCreatedEvent):
        pass

    @trace(name="response.done")
    async def _response_done(self, event: ResponseDoneEvent):
        if event.response.output is not None and len(event.response.output) > 0:
            output = event.response.output[0]
            match output.type:
                case "message":
                    if output.content and len(output.content) > 0:
                        content = str(output.content[0].transcript)
                        await self.connection.send_update(
                            Update.message(
                                id=str(output.id),
                                role="user" if output.role == "user" else "assistant",
                                content=content,
                            )
                        )

                        if self.thread_id is not None:
                            await create_thread_message(
                                thread_id=self.thread_id,
                                role=output.role if output.role else "assistant",
                                content=str(
                                    output.content[0].transcript
                                    if output.content
                                    else "" if output.content else ""
                                ),
                                metadata={
                                    "id": str(output.id),
                                    "event": "response.done",
                                    "source": "realtime",
                                },
                            )
                case "function_call_output":
                    await self.connection.send_update(
                        Update.console(
                            id=str(output.call_id),
                            payload=output.model_dump(exclude={"id", "call_id"}),
                        )
                    )

        if len(self.response_queue) > 0 and self.realtime is not None:
            for item in self.response_queue:
                await self.realtime.send(item)
            self.response_queue.clear()
            await self.realtime.response.create()

        self.active = False

    @trace(name="response.output_item.added")
    async def _response_output_item_added(self, event: ResponseOutputItemAddedEvent):
        pass

    @trace(name="response.output_item.done")
    async def _response_output_item_done(self, event: ResponseOutputItemDoneEvent):
        if event.item.type == "function_call":
            await self.connection.send_update(
                Update.function(
                    id=str(event.item.id),
                    call_id=str(event.item.call_id),
                    name=str(event.item.name),
                    arguments=json.loads(event.item.arguments or "{}"),
                )
            )

            if self.thread_id is not None:
                await create_thread_message(
                    thread_id=self.thread_id,
                    role="assistant",
                    content=f"Calling {event.item.name} with {str(event.item.arguments)}",
                    metadata={
                        "id": str(event.item.id),
                        "event": "response.done",
                        "source": "realtime",
                    },
                )

    @trace(name="response.content_part.added")
    async def _response_content_part_added(self, event: ResponseContentPartAddedEvent):
        pass

    @trace(name="response.content_part.done")
    async def _response_content_part_done(self, event: ResponseContentPartDoneEvent):
        pass

    @trace(name="response.text.delta")
    async def _response_text_delta(self, event: ResponseTextDeltaEvent):
        pass

    @trace(name="response.text.done")
    async def _response_text_done(self, event: ResponseTextDoneEvent):
        pass

    async def _response_audio_transcript_delta(
        self, event: ResponseAudioTranscriptDeltaEvent
    ):
        pass

    @trace(name="response.audio.transcript.done")
    async def _response_audio_transcript_done(
        self, event: ResponseAudioTranscriptDoneEvent
    ):
        pass

    async def _response_audio_delta(self, event: ResponseAudioDeltaEvent):
        await self.connection.send_update(
            Update.audio(id=event.event_id, data=event.delta)
        )

    @trace(name="response.audio.done")
    async def _response_audio_done(self, event: ResponseAudioDoneEvent):
        pass

    async def _response_function_call_arguments_delta(
        self, event: ResponseFunctionCallArgumentsDeltaEvent
    ):
        pass

    @trace(name="response.function_call_arguments.done")
    async def _response_function_call_arguments_done(
        self, event: ResponseFunctionCallArgumentsDoneEvent
    ):
        pass

    @trace(name="rate_limits.updated")
    async def _rate_limits_updated(self, event: RateLimitsUpdatedEvent):
        pass

    @trace
    async def receive_client(self):
        if self.connection.state != WebSocketState.CONNECTED or self.realtime is None:
            return

        try:
            while self.connection.state != WebSocketState.DISCONNECTED:
                text = await self.connection.receive_text()
                event = json.loads(text)

                match event["type"]:
                    case "audio":
                        await self.realtime.send(
                            InputAudioBufferAppendEvent(
                                type="input_audio_buffer.append", audio=event["content"]
                            )
                        )

                    case "message":
                        await self.realtime.send(
                            ConversationItemCreateEvent(
                                type="conversation.item.create",
                                item=ConversationItem(
                                    role="user",
                                    type="message",
                                    content=[
                                        ConversationItemContent(
                                            type="input_text",
                                            text=event["content"],
                                        )
                                    ],
                                ),
                            )
                        )

                    case "interrupt":
                        await self.realtime.send(
                            ResponseCreateEvent(type="response.create")
                        )

                    case "function_completion":
                        await self.realtime.send(
                            ConversationItemCreateEvent(
                                type="conversation.item.create",
                                item=ConversationItem(
                                    call_id=event["call_id"],
                                    type="function_call_output",
                                    output=event["output"],
                                ),
                            )
                        )

                        await self.realtime.response.create()

                    case _:
                        await self.connection.send_update(
                            Update.console(
                                id="unhandled_message",
                                payload={"message": "Unhandled message"},
                            )
                        )

        except WebSocketDisconnect:
            print("Realtime Socket Disconnected")
            await self.close()

    async def close(self):
        try:
            await self.connection.close()
            await self.realtime.close()
        except Exception as e:
            print("Error closing session", e)
