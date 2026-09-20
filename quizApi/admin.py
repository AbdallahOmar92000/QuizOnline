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



@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'correct_option')
    search_fields = ('question_text',)

class QuizQuestionOrderInline(admin.TabularInline):
    model = QuizQuestionOrder
    extra = 1
    autocomplete_fields = ['question']  # يحول القائمة لخانة بحث سريعة بنص السؤال

@admin.register(LiveQuiz)
class LiveQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_time', 'is_active', 'is_finished')
    inlines = [QuizQuestionOrderInline]
    actions = ['start_quiz_action']

    @admin.action(description='🚀 بدء المسابقة المباشرة الآن (Celery)')
    def start_quiz_action(self, request, queryset):
        for quiz in queryset:
            run_live_quiz_engine.delay(quiz.id)
        self.message_user(request, "تم إرسال أمر بدء المسابقة إلى Celery بنجاح!")