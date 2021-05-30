from typing import Optional, Sequence

from typing_extensions import Protocol


class SequenceError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class HasSequence(Protocol):
    sequence: int


def next_sequence(existing_instances: Sequence[HasSequence]) -> int:
    next_sequence_number = len(existing_instances) + 1
    last_instance: Optional[HasSequence] = None

    if next_sequence_number > 1:
        last_instance = existing_instances[-1]

    if last_instance and (last_instance.sequence != (next_sequence_number - 1)):
        raise SequenceError(
            "Last item {0} has sequence {1} but next sequence is {2}".format(
                existing_instances[-1:],
                last_instance.sequence,
                next_sequence_number,
            ),
        )

    return next_sequence_number
