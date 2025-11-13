from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from src.core.models.user import User 
from src.core.database import db

class UserForm(FlaskForm):
    """Formulario para la creación o edición de un usuario ."""

    # Campo no presente en el formulario de registro 

    #  Nombre y Apellido (Coinciden con User.nombre, User.apellido)
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres.')
        ]
    )
    apellido = StringField(
        'Apellido',
        validators=[
            DataRequired(message='El apellido es obligatorio.'),
            Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres.')
        ]
    )
    
    #  Correo Electrónico (Coincide con User.email)
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Formato de correo electrónico inválido.'),
            Length(max=100, message='El email no puede superar los 100 caracteres.')
        ]
    )

    #  Contraseña (Coincide con User.password)
    password = PasswordField(
        'Contraseña',
        validators=[
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres.')
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            EqualTo('password', message='Las contraseñas no coinciden.')
        ]
    )

    #  Campo de Rol (Necesario en el modelo, pero se asigna por defecto en el registro)
    # Lo incluimos, pero se anularán sus validadores en la ruta de registro.
    role_id = SelectField('Rol', coerce=int, validators=[DataRequired()])
    
    #  Estado
    enabled = BooleanField('Habilitado / Activo')

    #  Validación Personalizada: Unicidad del Email
    def validate_email(self, field):
        """Asegura que el email no esté ya en uso."""
        # Durante el registro, user_id está vacío, por lo que busca cualquier coincidencia.
        query = User.query.filter_by(email=field.data)
        if self.user_id.data:
            query = query.filter(User.id != self.user_id.data)
        
        if query.first():
            raise ValidationError('Este correo electrónico ya está registrado.')

    # Validación Personalizada: Contraseña Obligatoria al Crear
    def validate_password(self, field):
        """Asegura que la contraseña sea obligatoria solo si es un nuevo usuario (registro)."""
        if not self.user_id.data and not field.data:
            raise ValidationError('La contraseña es obligatoria para el registro.')