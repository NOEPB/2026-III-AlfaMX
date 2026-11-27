import json

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User, Group
from django.utils import timezone

from alfabetizacion.models import PerfilUsuario
from .models import Actividad, Leccion, Modulo


class StyledFormMixin:
    def add_css_classes(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} form-control'.strip()
            field.widget.attrs.setdefault('autocomplete', 'off')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu usuario', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña', 'autocomplete': 'current-password'}),
    )


class RegistroEstudianteForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre(s)', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    acepto_aviso_privacidad = forms.BooleanField(
        label='He leído y acepto el aviso de privacidad.'
    )
    autorizacion_tutor = forms.BooleanField(
        label='Cuento con autorización de mi madre, padre o tutor (si soy menor de edad).',
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'fecha_nacimiento',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].help_text = 'Será el nombre que usarás para iniciar sesión.'

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        fecha = cleaned.get('fecha_nacimiento')
        autorizado = cleaned.get('autorizacion_tutor')
        if fecha:
            hoy = timezone.localdate()
            edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
            if edad < 18 and not autorizado:
                self.add_error(
                    'autorizacion_tutor',
                    'Para registrar a una persona menor de edad se requiere autorización de su madre, padre o tutor.',
                )
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.rol = PerfilUsuario.ROL_ESTUDIANTE
            perfil.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
            perfil.acepto_aviso_privacidad = self.cleaned_data['acepto_aviso_privacidad']
            perfil.autorizacion_tutor = self.cleaned_data.get('autorizacion_tutor', False)
            perfil.save()
            grupo, _ = Group.objects.get_or_create(name='Estudiante')
            user.groups.set([grupo])
        return user


class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ('nombre', 'orden')
        labels = {'nombre': 'Nombre del módulo', 'orden': 'Orden de aparición'}
        widgets = {'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Vocales'}),
                   'orden': forms.NumberInput(attrs={'min': 0})}


class LeccionForm(forms.ModelForm):
    class Meta:
        model = Leccion
        fields = ('modulo', 'titulo', 'nivel', 'orden')
        labels = {
            'modulo': 'Módulo al que pertenece', 'titulo': 'Nombre de la lección',
            'nivel': 'Nivel', 'orden': 'Orden de aparición',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ej. Conociendo la A'}),
            'nivel': forms.NumberInput(attrs={'min': 1}),
            'orden': forms.NumberInput(attrs={'min': 0}),
        }


class ActividadForm(forms.ModelForm):
    contenido = forms.JSONField(
        label='Contenido (JSON)',
        widget=forms.Textarea(attrs={
            'rows': 7,
            'placeholder': '{\n  "letra": "A",\n  "respuesta": "A"\n}',
            'spellcheck': 'false',
        }),
        help_text='Escribe un objeto JSON válido con los datos que usa la actividad.',
    )

    class Meta:
        model = Actividad
        fields = ('leccion', 'tipo', 'instruccion_audio', 'contenido', 'orden')
        labels = {
            'leccion': 'Lección', 'tipo': 'Tipo de actividad',
            'instruccion_audio': 'Instrucción para reproducir en voz',
            'orden': 'Orden de aparición',
        }
        widgets = {
            'instruccion_audio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escucha y realiza la actividad.'}),
            'orden': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leccion'].queryset = Leccion.objects.select_related('modulo').order_by('modulo__orden', 'orden')
        if self.instance and self.instance.pk:
            self.initial['contenido'] = json.dumps(self.instance.contenido, ensure_ascii=False, indent=2)


class AdministrarUsuarioCreateForm(UserCreationForm):
    ROLES = PerfilUsuario.ROLES
    first_name = forms.CharField(label='Nombre(s)', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    rol = forms.ChoiceField(label='Rol', choices=ROLES)
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    autorizacion_tutor = forms.BooleanField(
        label='Cuenta con autorización de madre, padre o tutor (si es menor de edad).', required=False
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        fecha = cleaned.get('fecha_nacimiento')
        if fecha:
            hoy = timezone.localdate()
            edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
            if edad < 18 and not cleaned.get('autorizacion_tutor'):
                self.add_error('autorizacion_tutor', 'Se requiere autorización para una cuenta de menor de edad.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self._actualizar_perfil_y_rol(user)
        return user

    def _actualizar_perfil_y_rol(self, user):
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.rol = self.cleaned_data['rol']
        perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        perfil.autorizacion_tutor = self.cleaned_data.get('autorizacion_tutor', False)
        perfil.save()
        grupo, _ = Group.objects.get_or_create(name=perfil.get_rol_display())
        user.groups.set([grupo])


class AdministrarUsuarioUpdateForm(forms.ModelForm):
    rol = forms.ChoiceField(label='Rol', choices=PerfilUsuario.ROLES)
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    autorizacion_tutor = forms.BooleanField(
        label='Cuenta con autorización de madre, padre o tutor.', required=False
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')
        labels = {
            'username': 'Nombre de usuario', 'first_name': 'Nombre(s)',
            'last_name': 'Apellidos', 'email': 'Correo electrónico',
            'is_active': 'Cuenta activa',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perfil, _ = PerfilUsuario.objects.get_or_create(user=self.instance)
        self.fields['rol'].initial = perfil.rol
        self.fields['fecha_nacimiento'].initial = perfil.fecha_nacimiento
        self.fields['autorizacion_tutor'].initial = perfil.autorizacion_tutor
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese correo ya está asociado a otra cuenta.')
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.rol = self.cleaned_data['rol']
            perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
            perfil.autorizacion_tutor = self.cleaned_data.get('autorizacion_tutor', False)
            perfil.save()
            grupo, _ = Group.objects.get_or_create(name=perfil.get_rol_display())
            if not user.is_superuser:
                user.groups.set([grupo])
        return user
