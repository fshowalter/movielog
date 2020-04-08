from typing import List, Tuple

from prompt_toolkit.input import posix_pipe

PosixPipeInput = posix_pipe.PosixPipeInput
PersonTuple = Tuple[str, str]
MovieTuple = Tuple[str, str, int, List[PersonTuple]]
