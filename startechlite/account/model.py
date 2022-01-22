from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    first_name: str
    last_name: str
    email: str
    password: str
    phone_numbers: list[str]
    address: str