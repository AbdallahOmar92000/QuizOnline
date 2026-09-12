from django.db import models
from django.conf import settings
# Create your models here.

class Level(models.Model):
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    unlock_coins_required = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Level {self.number}: {self.title}"



class Question(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='questions')
    logo_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='logos/')
    hint = models.CharField(max_length=255, blank=True, null=True)
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['level', 'order']

    def __str__(self):
        return f"{self.logo_name} - Level {self.level.number}"


class UserQuizProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.question.logo_name} ({'Solved' if self.is_solved else 'Unsolved'})"

    