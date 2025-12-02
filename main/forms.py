from django import forms


class ThemeForm(forms.Form):
    title = forms.CharField(label="Название темы")


class SubThemeForm(forms.Form):
    title = forms.CharField(label="Название подтемы")
    text = forms.CharField(label="Текст статьи")
