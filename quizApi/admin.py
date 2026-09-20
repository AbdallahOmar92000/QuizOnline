from django.contrib import admin
from .models import QuestionBank, LiveQuiz, QuizQuestionOrder, QuizParticipant
from .utils import generate_random_quiz_questions
from django.contrib import admin
from .models import QuestionBank, LiveQuiz, QuizQuestionOrder, QuizParticipant
from .tasks import run_live_quiz_engine




class QuizQuestionOrderInline(admin.TabularInline):
    model = QuizQuestionOrder
    extra = 0
    readonly_fields = ('order', 'question')
    can_delete = True



@admin.register(QuizParticipant)
class QuizParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'is_eliminated', 'is_spectator', 'joined_at')
    list_filter = ('is_eliminated', 'is_spectator', 'quiz')
    search_fields = ('user__email', 'quiz__title')



from django.contrib import admin
from .models import LiveQuiz, QuestionBank, QuizQuestionOrder
from .tasks import run_live_quiz_engine # استدراك استيراد مهمة Celery


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'correct_option')
    search_fields = ('question_text',)
    ordering = ('id',)


class QuizQuestionOrderInline(admin.TabularInline):
    model = QuizQuestionOrder
    extra = 1
    autocomplete_fields = ['question']
    ordering = ('order',)


@admin.register(LiveQuiz)
class LiveQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_time', 'is_active', 'is_finished')
    list_filter = ('is_active', 'is_finished', 'start_time')
    search_fields = ('title',)
    inlines = [QuizQuestionOrderInline]
    actions = ['start_quiz_action']

    @admin.action(description='🚀 بدء المسابقة المباشرة الآن (Celery)')
    def start_quiz_action(self, request, queryset):
        count = 0
        for quiz in queryset:
            if not quiz.is_finished:
                quiz.is_active = True
                quiz.save()
                run_live_quiz_engine.delay(quiz.id)
                count += 1
        self.message_user(request, f"تم إرسال أمر بدء {count} مسابقة إلى Celery بنجاح!")