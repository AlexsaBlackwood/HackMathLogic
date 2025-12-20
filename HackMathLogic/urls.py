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
    path('register/', main.views.RegisterView.as_view(), name="register"),
    path('login/', main.views.LoginView.as_view(), name="login"),
    path('logout/', main.views.LogoutView.as_view(), name="logout"),
    path('themes/', main.views.ThemeListView.as_view(), name="themes_list"),
    path('themes/<int:id>/', main.views.ThemeDetailView.as_view(), name="theme_view"),
    path('themes/add/', main.views.ThemeAddView.as_view(), name="theme_add"),
    path('themes/<int:id>/edit/', main.views.ThemeEditView.as_view(), name="theme_edit"),
    path('themes/<int:id>/delete/', main.views.ThemeDeleteView.as_view(), name="theme_delete"),
    path('themes/<int:t_id>/<int:st_id>/', main.views.SubThemeDetailView.as_view(), name="subtheme_view"),
    path('themes/<int:t_id>/<int:st_id>/edit/', main.views.SubThemeUpdateView.as_view(), name="subtheme_edit"),
    path('themes/<int:t_id>/add/', main.views.SubThemeCreateView.as_view(), name="subtheme_add"),
    path('themes/<int:t_id>/<int:st_id>/delete/', main.views.SubThemeDeleteView.as_view(), name="subtheme_delete"),
    path('themes/<int:t_id>/<int:st_id>/tests/', main.views.TestListView.as_view(), name="tests_list"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/', main.views.TestDetailView.as_view(), name="test_view"),
    path('themes/<int:t_id>/<int:st_id>/tests/add/', main.views.TestCreateView.as_view(), name="test_add"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/edit/', main.views.TestUpdateView.as_view(), name="test_edit"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/run/', main.views.TestRunView.as_view(), name="test_run"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/delete/', main.views.TestDeleteView.as_view(), name="test_delete"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/', main.views.TestQuestionDetailView.as_view(), name="testquestion_view"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/add/', main.views.TestQuestionCreateView.as_view(), name="testquestion_add"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/edit/', main.views.TestQuestionUpdateView.as_view(), name="testquestion_edit"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/delete/', main.views.TestQuestionDeleteView.as_view(), name="testquestion_delete"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/answers/<int:a_id>/', main.views.TestAnswerVariantDetailView.as_view(), name="testanswervariant_view"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/answers/add/', main.views.TestAnswerVariantCreateView.as_view(), name="testanswervariant_add"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/answers/<int:a_id>/edit/', main.views.TestAnswerVariantUpdateView.as_view(), name="testanswervariant_edit"),
    path('themes/<int:t_id>/<int:st_id>/tests/<int:test_id>/questions/<int:q_id>/answers/<int:a_id>/delete/', main.views.TestAnswerVariantDeleteView.as_view(), name="testanswervariant_delete"),
]
