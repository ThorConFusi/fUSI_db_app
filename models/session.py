from dataclasses import dataclass


@dataclass
class Session:
    pyrat_id: str
    experiment: str
    session_number: str
    d_recording: str
    t_recording: str
    session: str
    session_comment: str
