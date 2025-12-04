from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Solicitud

class UserRegisterForm(UserCreationForm):
    rut = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT'}))
    rol = forms.ChoiceField(choices=Profile.ROLES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if Profile.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        return rut

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(user=user, rut=self.cleaned_data['rut'], rol=self.cleaned_data['rol'])
        return user

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['titulo', 'descripcion', 'cantidad_presidentes', 'cantidad_voluntarios', 'cantidad_beneficiarios']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la solicitud'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción detallada', 'rows': 4}),
            'cantidad_presidentes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'cantidad_voluntarios': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'cantidad_beneficiarios': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
