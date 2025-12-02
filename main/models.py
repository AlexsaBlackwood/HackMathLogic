from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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
