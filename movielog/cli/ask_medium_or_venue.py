from typing import Literal

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys

ReturnResult = Literal["v", "m"]


def ask_medium_or_venue(
    message: str = "Seen at a <cyan>(v)</cyan>enue or via a <cyan>(m)</cyan>edium?",
    suffix: str = " (v/m) ",
) -> ReturnResult | None:
    bindings = KeyBindings()

    @bindings.add("m")
    @bindings.add("M")
    def medium(event: KeyPressEvent) -> None:  # noqa: WPS430
        session.default_buffer.text = "m"
        event.app.exit(result="m")

    @bindings.add("v")
    @bindings.add("V")
    def venue(event: KeyPressEvent) -> None:  # noqa: WPS430
        session.default_buffer.text = "v"
        event.app.exit(result="v")

    @bindings.add(Keys.Escape)
    def _exit(event: KeyPressEvent) -> None:  # noqa: WPS430
        event.app.exit(result=None)

    @bindings.add(Keys.Any)
    def _(event: KeyPressEvent) -> None:  # noqa: WPS430
        """
        Disallow inserting other text.
        """

    complete_message = merge_formatted_text([HTML(message), suffix])
    session: PromptSession[ReturnResult] = PromptSession(complete_message, key_bindings=bindings)
    return session.prompt()
