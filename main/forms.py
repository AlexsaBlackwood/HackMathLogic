from django import forms


class ThemeForm (forms.Form):
    title = forms.CharField(label="Название темы")
