from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from main.models import (
    Theme, SubTheme, Article, Test, TestQuestion, 
    TestAnswerVariant, Result, ResultItem, UserProfile
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'get_role_display')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)


# Расширяем админку User для отображения профиля
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title',)


@admin.register(SubTheme)
class SubThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'id')
    list_filter = ('theme',)
    search_fields = ('title', 'theme__title')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('subtheme', 'id')
    list_filter = ('subtheme__theme',)
    search_fields = ('text', 'subtheme__title')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('question', 'subtheme', 'id')
    list_filter = ('subtheme__theme', 'subtheme')
    search_fields = ('question', 'subtheme__title')


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'id')
    list_filter = ('test__subtheme__theme', 'test')
    search_fields = ('text',)


@admin.register(TestAnswerVariant)
class TestAnswerVariantAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_right', 'id')
    list_filter = ('is_right', 'question__test__subtheme__theme')
    search_fields = ('text',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'created_at', 'id')
    list_filter = ('created_at', 'test__subtheme__theme')
    search_fields = ('user__username', 'test__question')
    readonly_fields = ('created_at',)


@admin.register(ResultItem)
class ResultItemAdmin(admin.ModelAdmin):
    list_display = ('result', 'answer', 'id')
    list_filter = ('result__test__subtheme__theme',)
    search_fields = ('result__user__username', 'answer__text')
