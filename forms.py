from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DecimalField, IntegerField, validators
from wtforms.validators import Required, Length, Regexp, NumberRange
from decimal import ROUND_HALF_UP

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
    palabra = StringField(u'Ingrese su filtro:', validators=[Required(),Length(min=3, message='Minimo 3 caracteres de largo')])
    enviar = SubmitField('Buscar')

class AltaVentaForm(FlaskForm):
    codigo = StringField(u'Codigo de Producto:', validators=[Required(), Regexp('[A-Z]+[A-Z]+[A-Z]+[0-9]+[0-9]+[0-9]+',message='Debe cumplir con el formato: 3 letras mayúsculas y 3 números'), Length(min=6, max=6, message='No cumple con el largo necesario')])
    producto = StringField(u'Nombre de Producto:', validators=[Required(), Length(min=3, message='Ingresar minimo 3 caracteres')])
    cantidad = IntegerField(u'Cantidad:', validators=[Required(), NumberRange(min=1,message='Minimo valor admitido: 1')])
    precio = StringField(u'Precio Unitario de Producto (en $): ', validators=[Required(), Regexp('[0-9]+.[0-9][0-9]?',message='Debe ingresar un valor tipo: N.NN')])
	#precio = DecimalField(u'Precio Unitario de Producto (en $): ', places = 2, use_locale=False, validators=[Required(), NumberRange(min=0.01,message='$Minimo valor admitido: 0.01')])
    nombreCliente = StringField(u'Nombre de Cliente:', validators=[Required(), Length(min=3, message='Ingresar minimo 3 caracteres')])
    enviar = SubmitField('Registrar!')
    

