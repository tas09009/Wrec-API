from flask_wtf import FlaskForm
from wtforms import FileField , SubmitField, StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UploadFile(FlaskForm):
    importFile = SubmitField('Import File')
    csv_file = FileField('CSV File')
    upload = SubmitField('Upload') 
    # UploadFile is a subclass of WTForm 
