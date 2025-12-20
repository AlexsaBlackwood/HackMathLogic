from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


# ------------------------
# Темы → Подтемы → Статьи
# ------------------------
class Theme(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("theme_view", kwargs={"id": self.id})


class SubTheme(models.Model):
    title = models.CharField(max_length=255)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="subthemes")

    def __str__(self):
        return f"{self.theme.title} — {self.title}"


class Article(models.Model):
    text = models.TextField()
    subtheme = models.ForeignKey(SubTheme, on_delete=models.CASCADE, related_name="articles")

    def __str__(self):
        return f"Статья: {self.subtheme.title}"


# ------------------------
# Тесты
# ------------------------
class Test(models.Model):
    question = models.CharField(max_length=500)
    subtheme = models.ForeignKey(SubTheme, on_delete=models.CASCADE, related_name="tests")

    def __str__(self):
        return self.question


class TestQuestion(models.Model):
    text = models.CharField(max_length=500)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.text


class TestAnswerVariant(models.Model):
    text = models.CharField(max_length=400)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name="answers")
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'верный' if self.is_right else 'неверный'})"


# ------------------------
# Результаты тестов
# ------------------------
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="results")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Результат {self.user.username} — тест {self.test.id}"


class ResultItem(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="items")
    answer = models.ForeignKey(TestAnswerVariant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ответ #{self.id} (Result {self.result.id})"


# ------------------------
# Профили пользователей
# ------------------------
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Учащийся'),
        ('TEACHER', 'Преподаватель'),
        ('ADMIN', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT', verbose_name="Роль")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_student(self):
        return self.role == 'STUDENT'
    
    def is_teacher(self):
        return self.role == 'TEACHER'
    
    def is_admin(self):
        return self.role == 'ADMIN'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Если пользователь - суперпользователь, устанавливаем роль ADMIN
        role = 'ADMIN' if instance.is_superuser else 'STUDENT'
        UserProfile.objects.create(user=instance, role=role)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        # Если пользователь стал суперпользователем, обновляем роль
        if instance.is_superuser and instance.profile.role != 'ADMIN':
            instance.profile.role = 'ADMIN'
            instance.profile.save()
        instance.profile.save()
