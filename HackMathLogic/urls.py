"""
URL configuration for HackMathLogic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import main.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main.views.index_page, name="index"),
    path('themes/', main.views.ThemeListView.as_view(), name="themes_list"),
    path('themes/<int:id>/', main.views.ThemeDetailView.as_view(), name="theme_view"),
    path('themes/add/', main.views.ThemeAddView.as_view(), name="theme_add"),
    path('themes/<int:id>/edit/', main.views.ThemeEditView.as_view(), name="theme_edit"),
    path('themes/<int:id>/delete/', main.views.ThemeDeleteView.as_view(), name="theme_delete"),
    path('themes/<int:t_id>/<int:st_id>/', main.views.subtheme_view_page, name="subtheme_view"),
    path('themes/<int:t_id>/<int:st_id>/edit/', main.views.subtheme_edit_page, name="subtheme_edit"),
    path('themes/<int:t_id>/add/', main.views.subtheme_add_page, name="subtheme_add"),
    path('themes/<int:t_id>/<int:st_id>/delete/', main.views.subtheme_delete_page, name="subtheme_delete"),
]
