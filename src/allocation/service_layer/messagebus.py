from typing import Callable, Dict, List, Type, Union
import logging

from allocation.domain import commands, events
from allocation.service_layer import handlers, unit_of_work
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

Message = Union[commands.Command, events.Event]

logger = logging.getLogger(__name__)


class AbstractMessageBus:
    EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]]
    COMMAND_HANDLERS: Dict[Type[commands.Command], Callable]

    def __init__(self, uow: unit_of_work.AbstractUnitOfWork):
        self.uow = uow

    def handle(self, message: Message):
        results = []
        queue = [message]

        while queue:
            message = queue.pop(0)

            if isinstance(message, events.Event):
                self.handle_event(message, queue, self.uow)
            elif isinstance(message, commands.Command):
                cmd_result = self.handle_command(message, queue, self.uow)
                results.append(cmd_result)
            else:
                raise Exception(f"{message} was not an Event or Command")

        return results

    def handle_event(
        self,
        event: events.Event,
        queue: List[Message],
        uow: unit_of_work.AbstractUnitOfWork,
    ):
        for handler in self.EVENT_HANDLERS[type(event)]:
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(3), wait=wait_exponential()
                ):
                    with attempt:
                        logger.debug(f"handling event {event} with handler {handler}")
                        handler(event, uow=uow)
                        queue.extend(uow.collect_new_events())
            except Exception:
                logger.exception(f"Exception handling event {event}")
                continue

    def handle_command(
        self,
        command: commands.Command,
        queue: List[Message],
        uow: unit_of_work.AbstractUnitOfWork,
    ):
        logger.debug(f"Handling command {command}")

        try:
            handler = self.COMMAND_HANDLERS[type(command)]
            result = handler(command, uow=uow)
            queue.extend(uow.collect_new_events())
            return result
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise


class MessageBus(AbstractMessageBus):
    EVENT_HANDLERS = {
        events.OutOfStock: [handlers.send_out_of_stock_notification],
    }  # type: Dict[Type[events.Event], List[Callable]]

    COMMAND_HANDLERS = {
        commands.Allocate: handlers.allocate,
        commands.CreateBatch: handlers.add_batch,
        commands.ChangeBatchQuantity: handlers.change_batch_quantity,
    }  # type: Dict[Type[commands.Command], Callable]
