from dataclasses import dataclass


@dataclass
class Credentials:
    password: str
    api_base: str
    api_key: str
