from flask_wtf import FlaskForm
from wtforms.fields.simple import BooleanField, FileField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from startechlite.dbmanager.dbmanager import DBManager

dbmanager = DBManager()

class UserRegistrationForm(FlaskForm):
    firstname = StringField("First Name", validators=[
                            DataRequired(), Length(max=20)])

    lastname = StringField("Last Name", validators=[
        DataRequired(), Length(max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    telephone = StringField("Telephone", validators=[DataRequired()])
    submit = SubmitField("Continue")

    def validate_email(self, email: StringField):
        user = dbmanager
