from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import UserProfile


class ThemeForm(forms.Form):
    title = forms.CharField(
        label="Название темы",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название темы'})
    )


class SubThemeForm(forms.Form):
    title = forms.CharField(
        label="Название подтемы",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название подтемы'})
    )
    text = forms.CharField(
        label="Текст статьи",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'Введите теоретический материал. Вы можете использовать HTML-разметку для форматирования.'
        })
    )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)
    role = forms.ChoiceField(
        label="Роль",
        choices=UserProfile.ROLE_CHOICES,
        initial='STUDENT',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Обновляем роль в профиле
            if hasattr(user, 'profile'):
                user.profile.role = self.cleaned_data['role']
                user.profile.save()
            else:
                UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
