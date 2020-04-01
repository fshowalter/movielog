from sqlite3 import Connection as SqlConnection
from typing import Any, List, Tuple

TableInfoType = List[Tuple[int, str, str, int, Any, int]]
Connection = SqlConnection
