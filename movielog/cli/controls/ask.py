from typing import Optional, cast

from prompt_toolkit import key_binding
from prompt_toolkit import prompt as toolkit_prompt
from prompt_toolkit.validation import Validator


def prompt(
    message: str,
    extra_rprompt: Optional[str] = None,
    validator: Optional[Validator] = None,
) -> Optional[str]:
    bindings = key_binding.KeyBindings()

    @bindings.add("escape")  # type: ignore  # noqa WPS430
    def exit_prompt_(event: key_binding.key_processor.KeyPressEvent) -> None:
        """ Exit when `ESC` is pressed. """
        event.app.exit()

    rprompt = "ESC to go back"

    if extra_rprompt:
        rprompt = f"{extra_rprompt} | {rprompt}"

    return cast(
        Optional[str],
        toolkit_prompt(
            message,
            key_bindings=bindings,
            rprompt=rprompt,
            validator=validator,
            validate_while_typing=False,
        ),
    )
