from collections.abc import Sequence
from typing import cast

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import (
    HTML,
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Container, Float, FloatContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.widgets import Label


class RadioList[T]:
    """
    List of radio buttons. Only one can be checked at the same time.
    :param values: List of (value, label) tuples.
    """

    open_character = "("
    close_character = ")"
    container_style = "class:radio-list"
    default_style = "class:radio"
    selected_style = "class:radio-selected"
    checked_style = "class:radio-checked"

    def __init__(self, options: Sequence[tuple[T, AnyFormattedText]]) -> None:
        self.options = options
        self.current_option: T = options[0][0]
        self._selected_index = 0

        # Key bindings.
        kb = KeyBindings()

        kb.add("escape")(self._handle_exit)
        kb.add("up")(self._handle_up)
        kb.add("down")(self._handle_down)
        kb.add("enter")(self._handle_enter)
        kb.add("c-d")(self._handle_exit)
        kb.add("c-a")(self._handle_home)
        kb.add("c-e")(self._handle_end)

        # Control and window.
        self.control = FormattedTextControl(
            self._get_text_fragments, key_bindings=kb, focusable=True
        )

        self.window = Window(
            content=self.control,
            style=self.container_style,
            right_margins=[ScrollbarMargin(display_arrows=True)],
            dont_extend_height=True,
        )

    def __pt_container__(self) -> Container:
        return self.window

    def _get_text_fragments(self) -> StyleAndTextTuples:
        output_result: StyleAndTextTuples = []
        for index, option in enumerate(self.options):
            selected = index == self._selected_index

            style = ""
            if selected:
                style = f"{style} {self.selected_style}"

            output_result.append((style, self.open_character))

            if selected:
                output_result.append(("[SetCursorPosition]", ""))
                output_result.append((style, "*"))
            else:
                output_result.append((style, " "))

            output_result.append((style, self.close_character))
            output_result.append((self.default_style, " "))
            output_result.extend(to_formatted_text(option[1], style=self.default_style))
            output_result.append(("", "\n"))

        output_result.pop()  # Remove last newline.
        return output_result

    def _handle_enter(self, event: KeyPressEvent) -> None:
        self.current_value = self.options[self._selected_index][0]
        event.app.exit(result=self.current_value)

    def _handle_up(self, event: KeyPressEvent) -> None:
        new_index = self._selected_index - 1

        if new_index < 0:
            new_index = len(self.options) - 1

        self._selected_index = new_index

    def _handle_down(self, event: KeyPressEvent) -> None:
        new_index = self._selected_index + 1

        if new_index > len(self.options) - 1:
            new_index = 0

        self._selected_index = new_index

    def _handle_home(self, event: KeyPressEvent) -> None:
        self._selected_index = 0

    def _handle_end(self, event: KeyPressEvent) -> None:
        self._selected_index = len(self.options) - 1

    def _handle_exit(self, event: KeyPressEvent) -> None:
        event.app.exit(result=None)


def prompt[T](
    title: str,
    options: Sequence[tuple[T, AnyFormattedText]],
    rprompt: str | None = None,
) -> T | None:
    control = RadioList(options_to_html(options))

    application: Application[None] = Application(
        layout=Layout(
            HSplit(
                [
                    FloatContainer(
                        HSplit(
                            [
                                Label(HTML(title)),
                                control,
                            ]
                        ),
                        [
                            Float(
                                right=0,
                                top=0,
                                hide_when_covering_content=True,
                                content=Label(rprompt or "ESC to go back"),
                            ),
                        ],
                    )
                ]
            )
        ),
        mouse_support=False,
        full_screen=False,
    )

    return cast(T, application.run())


def options_to_html[T](
    options: Sequence[tuple[T, AnyFormattedText]],
) -> Sequence[tuple[T, AnyFormattedText]]:
    formatted_options: list[tuple[T, AnyFormattedText]] = []

    for option in options:
        option_text = HTML(cast(str, option[1]))
        formatted_options.append((option[0], option_text))

    return formatted_options
