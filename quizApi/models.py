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
        return f"{self.user.email} - {self.question.logo_name} ({'Solved' if self.is_solved else 'Unsolved'})"
#########################################################

# نموذج المسابقة المباشرة
class LiveQuiz(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField(verbose_name="تاريخ ووقت البدء")
    entry_fee_coins = models.PositiveIntegerField(default=5, verbose_name="رسوم الدخول")
    revive_cost_coins = models.PositiveIntegerField(default=5, verbose_name="تكلفة الفرصة الثانية")
    is_active = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.start_time})"

# نموذج السؤال ذو الخيارات الأربعة
class MultipleChoiceQuestion(models.Model):
    quiz =models.ForeignKey(LiveQuiz,related_name='questions', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(verbose_name="ترتيب السؤال (1-15)")
    question_text = models.TextField(verbose_name="نص السؤال")
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1,choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],verbose_name="الإجابة الصحيحة")
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"سؤال {self.order}: {self.question_text[:30]}"


# سجل مشاركة وتتبع حالة اللاعب في المسابقة المباشرة
class QuizParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    is_eliminated = models.BooleanField(default=False, verbose_name="مستبعد / خسر")
    is_spectator = models.BooleanField(default=False, verbose_name="مشاهد / ضيف")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')