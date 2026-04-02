from datetime import date


def full_viewing_sequence(viewing_date: date, sequence: int) -> str:
    return f"{viewing_date.isoformat()}-{sequence:02}"
