import sys as _sys
from typing import TYPE_CHECKING, Any, Callable, Sequence, TypeVar

from loguru import logger as _base_logger

if TYPE_CHECKING:
    import loguru

T = TypeVar("T")  # noqa: WPS111
Function = Callable[..., T]

logger_handlers: Sequence[loguru.HandlerConfig] = [
    {
        "sink": _sys.stdout,
        "format": "<green>{elapsed}</green> | "
        + "<level>{message}</level> "
        + "(<cyan>{file}</cyan>:<cyan>{line}</cyan>)",
    },
]

_base_logger.configure(handlers=logger_handlers)


class ExtendedLogger:
    def __init__(self, _logger: "loguru.Logger"):
        self.logger = _logger

    def log(self, message: str, *args: Any, **kwargs: Any) -> None:
        message_with_color = message

        if message.startswith("==== "):
            message_with_color = message.replace(
                "====",
                "<yellow>====</yellow>",
            ).replace("{}", "<yellow>{}</yellow>")
        else:
            message_with_color = message.replace("{}", "<green>{}</green>")

        self.logger.opt(colors=True, depth=1).info(
            message_with_color, *args, **kwargs
        )  # no-qa: WPS221

    def catch(self, function: Function[None]) -> Function[None]:
        return self.logger.catch(function)


logger: ExtendedLogger = ExtendedLogger(_base_logger.opt(colors=True))
