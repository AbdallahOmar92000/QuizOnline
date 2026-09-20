from django.db import models
from django.conf import settings
# Create your models here.

# class Level(models.Model):
#     number = models.PositiveIntegerField(unique=True)
#     title = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     unlock_coins_required = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ['number']

#     def __str__(self):
#         return f"Level {self.number}: {self.title}"



# class Question(models.Model):
#     level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='questions')
#     logo_name = models.CharField(max_length=100)
#     image = models.ImageField(upload_to='logos/')
#     hint = models.CharField(max_length=255, blank=True, null=True)
#     points = models.PositiveIntegerField(default=10)
#     order = models.PositiveIntegerField(default=1)

#     class Meta:
#         ordering = ['level', 'order']

#     def __str__(self):
#         return f"{self.logo_name} - Level {self.level.number}"


# class UserQuizProgress(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_progress')
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     is_solved = models.BooleanField(default=False)
#     solved_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'question')

#     def __str__(self):
#         return f"{self.user.email} - {self.question.logo_name} ({'Solved' if self.is_solved else 'Unsolved'})"
# #########################################################

# # نموذج المسابقة المباشرة
# class LiveQuiz(models.Model):
#     title = models.CharField(max_length=200)
#     start_time = models.DateTimeField(verbose_name="تاريخ ووقت البدء")
#     entry_fee_coins = models.PositiveIntegerField(default=5, verbose_name="رسوم الدخول")
#     revive_cost_coins = models.PositiveIntegerField(default=5, verbose_name="تكلفة الفرصة الثانية")
#     is_active = models.BooleanField(default=False)
#     is_finished = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.title} ({self.start_time})"

# # نموذج السؤال ذو الخيارات الأربعة
# class MultipleChoiceQuestion(models.Model):
#     quiz =models.ForeignKey(LiveQuiz,related_name='questions', on_delete=models.CASCADE)
#     order = models.PositiveIntegerField(verbose_name="ترتيب السؤال (1-15)")
#     question_text = models.TextField(verbose_name="نص السؤال")
#     option_a = models.CharField(max_length=255)
#     option_b = models.CharField(max_length=255)
#     option_c = models.CharField(max_length=255)
#     option_d = models.CharField(max_length=255)
#     correct_option = models.CharField(max_length=1,choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],verbose_name="الإجابة الصحيحة")
#     class Meta:
#         ordering = ['order']

#     def __str__(self):
#         return f"سؤال {self.order}: {self.question_text[:30]}"


# # سجل مشاركة وتتبع حالة اللاعب في المسابقة المباشرة
# class QuizParticipant(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE)
#     score = models.PositiveIntegerField(default=0)
#     is_eliminated = models.BooleanField(default=False, verbose_name="مستبعد / خسر")
#     is_spectator = models.BooleanField(default=False, verbose_name="مشاهد / ضيف")
#     joined_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'quiz')


###################################
from django.db import models
from django.conf import settings


class QuestionBank(models.Model):
    """بنك الأسئلة العام لحفظ الأسئلة والخيارات"""
    question_text = models.CharField(max_length=255,verbose_name="نص السؤال")
    option_a = models.CharField(max_length=255, verbose_name="الخيار A")
    option_b = models.CharField(max_length=255, verbose_name="الخيار B")
    option_c = models.CharField(max_length=255, verbose_name="الخيار C")
    option_d = models.CharField(max_length=255, verbose_name="الخيار D")
    correct_option = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        verbose_name="الإجابة الصحيحة"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط للاستخدام")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سؤال في بنك الأسئلة"
        verbose_name_plural = "بنك الأسئلة"

    def __str__(self):
        return f"{self.id} - {self.question_text[:40]}"


class LiveQuiz(models.Model):
    """نموذج المسابقة المباشرة"""
    title = models.CharField(max_length=200, verbose_name="عنوان المسابقة")
    start_time = models.DateTimeField(verbose_name="تاريخ ووقت البدء (توقيت الأردن)")
    entry_fee_coins = models.PositiveIntegerField(default=5, verbose_name="رسوم الدخول")
    revive_cost_coins = models.PositiveIntegerField(default=5, verbose_name="تكلفة الفرصة الثانية")
    is_active = models.BooleanField(default=False, verbose_name="جارية الآن")
    is_finished = models.BooleanField(default=False, verbose_name="منتهية")
    
    # ربط الأسئلة من بنك الأسئلة عبر نموذج الترتيب الوسيط
    questions = models.ManyToManyField(
        QuestionBank, 
        through='QuizQuestionOrder', 
        related_name='quizzes',
        verbose_name="أسئلة المسابقة"
    )

    class Meta:
        verbose_name = "مسابقة مباشرة"
        verbose_name_plural = "المسابقات المباشرة"

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"


class QuizQuestionOrder(models.Model):
    """جدول وسيط لترتيب الـ 15 سؤالاً المختارة للمسابقة"""
    quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE, verbose_name="المسابقة")
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, verbose_name="السؤال")
    order = models.PositiveIntegerField(verbose_name="ترتيب السؤال (1-15)")

    class Meta:
        ordering = ['order']
        unique_together = ('quiz', 'order')
        verbose_name = "ترتيب سؤال في المسابقة"
        verbose_name_plural = "ترتيب أسئلة المسابقات"

    def __str__(self):
        return f"{self.quiz.title} - سؤال {self.order}"


class QuizParticipant(models.Model):
    """سجل مشاركة وتتبع حالة اللاعب في المسابقة المباشرة"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="المستخدم")
    quiz = models.ForeignKey(LiveQuiz, on_delete=models.CASCADE, verbose_name="المسابقة")
    score = models.PositiveIntegerField(default=0, verbose_name="النقاط")
    is_eliminated = models.BooleanField(default=False, verbose_name="مستبعد / خسر")
    is_spectator = models.BooleanField(default=False, verbose_name="مشاهد / ضيف")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")

    class Meta:
        unique_together = ('user', 'quiz')
        verbose_name = "مشارك في المسابقة"
        verbose_name_plural = "المشاركون في المسابقات"

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title}"