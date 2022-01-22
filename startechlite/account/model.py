from dataclasses import dataclass
from flask_login import UserMixin


@dataclass
class User(UserMixin):
    id: int  # needs to be just id for UserMixin
    first_name: str
    last_name: str
    email: str
    password: str
    phone_number: str
    address: str
