import logging
from collections.abc import Callable
from typing import Any

from ..domain.commands import Command
from ..domain.events import Event

logger = logging.getLogger(__name__)

Message = Command | Event


class InMemoryMessageBus:
    def __init__(self) -> None:
        self.command_handlers: dict[type[Command], Callable[..., Any]] = {}
        self.event_handlers: dict[type[Event], list[Callable[..., Any]]] = {}

    def handle(self, message: Message) -> Any:
        if isinstance(message, Command):
            self.handle_command(message)
        elif isinstance(message, Event):
            self.handle_event(message)
        else:
            raise ValueError(f"No handler registered for message type: {type(message)}")

    def register_handler(self, message_type: type[Message], handler: Callable[..., Any]) -> None:
        if issubclass(message_type, Command):
            self.register_command_handler(message_type, handler)
        elif issubclass(message_type, Event):
            self.register_event_handler(message_type, handler)
        else:
            raise ValueError(f"Message type {message_type} is not recognized.")

    def handle_command(self, command: Command) -> Any:
        handler = self.command_handlers.get(type(command))
        if handler:
            logger.debug(f"Handling command {command}")
            return handler(command)
        raise ValueError(f"No handler registered for command: {type(command)}")

    def handle_event(self, event: Event) -> None:
        handlers = self.event_handlers.get(type(event), [])
        for handler in handlers:
            try:
                logger.debug(f"Handling event {event} with handler {handler}")
                handler(event)
            except Exception:
                logger.exception(f"Exception handling event {event}")
                continue

    def register_command_handler(self, command_type: type[Command], handler: Callable[..., Any]) -> None:
        self.command_handlers[command_type] = handler

    def register_event_handler(self, event_type: type[Event], handler: Callable[..., Any]) -> None:
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
