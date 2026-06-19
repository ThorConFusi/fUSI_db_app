from dataclasses import dataclass
from typing import Optional


@dataclass
class Mouse:
    pyrat_id: str
    dob: Optional[str]
    sex: Optional[str]
    line: Optional[str]
    dos: Optional[str]
    tos: Optional[str]
    surgeon: Optional[str]
    license: Optional[str]
    dod: Optional[str]
    tod: Optional[str]
    kill_method: Optional[str]
    kill_purpose: Optional[str]
    kill_comment: Optional[str]
