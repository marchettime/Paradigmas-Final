from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import Required, Length


class LoginForm(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[Required()])#Label del campo, y las validaciones correspondientes, en este caso tiene el validador que busca que sea campo requerido
    password = PasswordField('Contraseña', validators=[Required()])
    enviar = SubmitField('Ingresar')


class SaludarForm(FlaskForm):
    usuario = StringField('Nombre: ', validators=[Required()])
    enviar = SubmitField('Saludar')


class RegistrarForm(LoginForm):
    password_check = PasswordField('Verificar Contraseña', validators=[Required()])
    enviar = SubmitField('Registrarse')

class BuscarForm(FlaskForm):
    palabra = StringField(u'Ingrese su filtro:', validators=[Required(),Length(min=3)])
    enviar = SubmitField('Buscar')
    
#class BuscarOpcionForm(FlaskForm, opciones):
    #palabra = StringField(u'Ingrese su filtro:', validators=[Required(),Length(min=6, message=('Too short for an email address?'))])
    #opcion = SelectedField('Valores encontrado:', choiches=[opciones])
    #enviar = SubmitField('Buscar')

