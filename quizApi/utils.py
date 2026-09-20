import random
from .models import QuestionBank, QuizQuestionOrder

def generate_random_quiz_questions(quiz):
    # إزالة الأسئلة القديمة إن وجدت للمسابقة
    QuizQuestionOrder.objects.filter(quiz=quiz).delete()
    
    # جلب جميع الأسئلة النشطة واختيار 15 عشوائياً
    active_questions = list(QuestionBank.objects.filter(is_active=True))
    if len(active_questions) < 15:
        selected_questions = active_questions
    else:
        selected_questions = random.sample(active_questions, 15)

    # حفظ الترتيب من 1 إلى 15
    for index, q in enumerate(selected_questions, start=1):
        QuizQuestionOrder.objects.create(quiz=quiz, question=q, order=index)