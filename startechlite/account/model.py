from dataclasses import dataclass
from flask_login import UserMixin
from wtforms.form import Form
from wtforms.fields import StringField, EmailField, PasswordField, TelField, TextAreaField
from wtforms import validators
from startechlite.constants import *


@dataclass
class User(UserMixin):
    id: int  # needs to be just id for UserMixin
    first_name: str
    last_name: str
    email: str
    password: str
    phone_number: str
    address: str

    @property
    def is_admin(self) -> bool:
        return self.email == ADMIN_EMAIL

    class UserForm(Form):
        first_name = StringField("First Name", validators=[
                                 validators.input_required(), validators.length(max=15)])
        last_name = StringField("Last Name", validators=[
                                validators.input_required(), validators.length(max=15)])
        email = EmailField("Email")
        password = PasswordField("Password", validators=[
                                 validators.input_required()])
        phone_number = TelField("Phone Number")
        address = TextAreaField("Address")


if __name__ == "__main__":
    user = User(99, "fn", "ln", "em", "pw", "ph", "ad")
