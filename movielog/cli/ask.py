from typing import Optional, cast

from prompt_toolkit import key_binding
from prompt_toolkit import prompt as toolkit_prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import Validator


def prompt(
    message: str,
    rprompt: Optional[str] = None,
    validator: Optional[Validator] = None,
    default: str = "",
) -> Optional[str]:
    bindings = key_binding.KeyBindings()

    bindings.add("escape", eager=True)(handle_escape)

    right_side_prompt = "ESC to go back"

    if rprompt:
        right_side_prompt = "{0} | {1}".format(right_side_prompt, rprompt)

    return cast(
        Optional[str],
        toolkit_prompt(
            HTML(message),
            key_bindings=bindings,
            rprompt=right_side_prompt,
            validator=validator,
            default=default,
            validate_while_typing=False,
        ),
    )


def handle_escape(event: key_binding.key_processor.KeyPressEvent) -> None:
    """Exit when `ESC` is pressed."""
    event.app.exit()
