from datetime import date


def full_viewing_sequence(date: date, sequence: int) -> str:
    return f"{date.isoformat()}-{sequence:02}"
