from typing import Literal

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys

ReturnResult = Literal["y", "n"]


def ask_review(
    message: str = "Create a review?",
    suffix: str = " (y/n) ",
) -> ReturnResult | None:
    bindings = KeyBindings()

    @bindings.add("y")
    @bindings.add("Y")
    def yes(event: KeyPressEvent) -> None:
        session.default_buffer.text = "y"
        event.app.exit(result="y")

    @bindings.add("n")
    @bindings.add("N")
    def no_review(event: KeyPressEvent) -> None:
        session.default_buffer.text = "n"
        event.app.exit(result="n")

    @bindings.add(Keys.Escape)
    def _exit(event: KeyPressEvent) -> None:
        event.app.exit(result=None)

    @bindings.add(Keys.Any)
    def _(event: KeyPressEvent) -> None:
        """
        Disallow inserting other text.
        """

    complete_message = merge_formatted_text([HTML(message), suffix])
    session: PromptSession[ReturnResult] = PromptSession(complete_message, key_bindings=bindings)
    return session.prompt()
