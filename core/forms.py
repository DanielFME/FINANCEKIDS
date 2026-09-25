from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.template import loader
from django.utils import timezone
from smtplib import SMTPException

from game.models import UserProfile


class PasswordResetEmailDeliveryError(Exception):
    """Raised when the reset email could not be delivered by the mail backend."""


class FinanceKidsPasswordResetForm(auth_forms.PasswordResetForm):
    email = forms.EmailField(
        error_messages={'required': 'El email es obligatorio.'},
        widget=forms.EmailInput(
            attrs={
                'class': 'input-kids',
                'placeholder': 'Correo electrónico',
                'autocomplete': 'email',
            }
        )
    )

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        try:
            email_message.send()
        except (SMTPException, OSError) as exc:
            raise PasswordResetEmailDeliveryError from exc


class FinanceKidsSetPasswordForm(auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'input-kids',
            'placeholder': 'Nueva contraseña',
            'autocomplete': 'new-password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'input-kids',
            'placeholder': 'Confirmar nueva contraseña',
            'autocomplete': 'new-password',
        })


class RegistroForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=True, error_messages={'required': 'El email es obligatorio.'})
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    fecha_nacimiento = forms.DateField(required=False)
    genero = forms.ChoiceField(
        required=False,
        choices=[('', 'Selecciona una opcion'), ('M', 'Masculino'), ('F', 'Femenino')],
    )
    nombre_tutor = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'El nombre del tutor es obligatorio.'},
    )
    email_tutor = forms.EmailField(
        required=True,
        error_messages={'required': 'El email del tutor es obligatorio.'},
    )
    pais = forms.CharField(max_length=50, required=False)
    acepto_terminos = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes aceptar los términos y condiciones.'},
    )
    consentimiento_tutor = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes confirmar el consentimiento del tutor.'},
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('El nombre de usuario ya existe.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ese correo ya se encuentra registrado.')
        return email

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento and fecha_nacimiento > timezone.localdate():
            raise ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return fecha_nacimiento

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')

        if password1:
            try:
                validate_password(password1)
            except ValidationError as exc:
                self.add_error('password1', exc)

        return cleaned_data

    def save(self, request=None):
        now = timezone.now()
        registro_ip = None
        if request is not None:
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarded:
                registro_ip = forwarded.split(',')[0].strip()
            else:
                registro_ip = request.META.get('REMOTE_ADDR')

        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        UserProfile.objects.update_or_create(
            usuario=user,
            defaults={
                'fecha_nacimiento': self.cleaned_data.get('fecha_nacimiento'),
                'genero': self.cleaned_data.get('genero') or None,
                'nombre_tutor': self.cleaned_data.get('nombre_tutor') or None,
                'email_tutor': self.cleaned_data.get('email_tutor') or None,
                'pais': self.cleaned_data.get('pais') or None,
                'acepto_terminos': True,
                'acepto_terminos_en': now,
                'consentimiento_tutor': True,
                'consentimiento_tutor_en': now,
                'registro_ip': registro_ip,
            },
        )
        return user
