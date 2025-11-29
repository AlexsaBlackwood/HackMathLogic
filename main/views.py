from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from main.forms import ThemeForm
from main.models import Theme


# Create your views here.

def index_page(request):
    return render(request, "index.html")


def themes_page(request):
    themes = Theme.objects.all()
    return render(request, "themes/list.html", {"themes": themes})


def theme_view_page(request, id):
    theme = get_object_or_404(Theme, id=id)
    return render(request, "themes/view.html", {"theme": theme})


def theme_add_page(request):
    if request.method == "GET":
        form = ThemeForm()
        return render(request, "themes/add.html", {"form": form})
    form = ThemeForm(request.POST)
    if form.is_valid():
        new_theme = Theme(title=form.cleaned_data['title'])
        new_theme.save()
        return redirect(reverse("theme_view", kwargs={"id": new_theme.id}))
    else:
        return render(request, "themes/add.html", {"form": form})

def theme_edit_page(request, id):
    theme = get_object_or_404(Theme, id=id)
    if request.method == "GET":
        form = ThemeForm(initial={"title": theme.title})
        return render(request, "themes/edit.html", {"form": form, "theme": theme})
    form = ThemeForm(request.POST)
    if form.is_valid():
        theme.title = form.cleaned_data['title']
        theme.save()
        return redirect(reverse("theme_view", kwargs={"id": theme.id}))
    else:
        return render(request, "themes/edit.html", {"form": form})


def theme_delete_page(request, id):
    if request.method == "GET":
        return redirect(reverse('theme_edit', kwargs={"id": id}))
    theme = get_object_or_404(Theme, id=id)
    theme.delete()
    return redirect(reverse('themes_list'))