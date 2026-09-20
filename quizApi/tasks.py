import time
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import LiveQuiz, QuizQuestionOrder
from .utils import generate_random_quiz_questions

import time
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import LiveQuiz, QuizQuestionOrder
from .utils import generate_random_quiz_questions

@shared_task
def run_live_quiz_engine(quiz_id):
    channel_layer = get_channel_layer()
    room_group_name = f'live_quiz_{quiz_id}'

    print(f"\n==========================================")
    print(f"[CELERY] 🚀 بدء تشغيل محرك المسابقة رقم: {quiz_id}")
    print(f"==========================================")

    try:
        quiz = LiveQuiz.objects.get(id=quiz_id)
        quiz.is_active = True
        quiz.save()
    except LiveQuiz.DoesNotExist:
        print(f"[CELERY ERROR] ❌ المسابقة رقم {quiz_id} غير موجودة!")
        return

    # 1. توليد الأسئلة إن لم تكن مجهزة
    quiz_questions = QuizQuestionOrder.objects.filter(quiz=quiz).select_related('question').order_by('order')
    if not quiz_questions.exists():
        print(f"[CELERY] 🎲 جاري توليد أسئلة عشوائية للمسابقة...")
        generate_random_quiz_questions(quiz)
        quiz_questions = QuizQuestionOrder.objects.filter(quiz=quiz).select_related('question').order_by('order')

    total_questions = quiz_questions.count()
    print(f"[CELERY] 📊 إجمالي عدد الأسئلة: {total_questions}")

    # 2. بث إشعار بداية المسابقة
    print(f"[CELERY] 📢 بث إشعار بداية المسابقة إلى الغرفة: {room_group_name}")
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'broadcast_quiz_start',
            'message': 'بدأت المسابقة الآن!',
            'total_questions': total_questions
        }
    )
    time.sleep(3)

    for index, item in enumerate(quiz_questions):
        q = item.question
        
        # 3. بث السؤال
        print(f"\n[CELERY] ❓ السؤال ({index + 1}/{total_questions}): {q.question_text}")
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'broadcast_question',
                'question_id': q.id,
                'order': item.order,
                'total_questions': total_questions,
                'question_text': q.question_text,
                'options': {
                    'A': q.option_a,
                    'B': q.option_b,
                    'C': q.option_c,
                    'D': q.option_d,
                },
                'duration_seconds': 15
            }
        )
        
        print(f"[CELERY] ⏳ انتظار 15 ثانية للإجابة...")
        time.sleep(15)

        # 4. بث الإجابة الصحيحة
        print(f"[CELERY] ✅ كشف الإجابة الصحيحة: ({q.correct_option})")
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'broadcast_answer_reveal',
                'question_id': q.id,
                'correct_option': q.correct_option,
                'revive_duration_seconds': 5,
                'is_last_question': (index == total_questions - 1)
            }
        )

        print(f"[CELERY] ⏳ انتظار 5 ثوانٍ للإنعاش...")
        time.sleep(5)

    # 5. إنهاء المسابقة
    quiz.is_active = False
    quiz.is_finished = True
    quiz.save()

    print(f"\n==========================================")
    print(f"[CELERY] 🏁 اكتملت المسابقة رقم {quiz_id} وتم إغلاقها بنجاح!")
    print(f"==========================================\n")

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'broadcast_quiz_finish',
            'message': 'انتهت المسابقة!'
        }
    )



from django.utils import timezone

@shared_task
def trigger_daily_quiz_at_3pm():
    """مهمة تعمل الساعة 3:00 مساءً للبحث عن مسابقة اليوم وتشغيلها"""
    now = timezone.now()
    
    # البحث عن مسابقة تبدأ اليوم وغير منتهية
    quiz = LiveQuiz.objects.filter(
        start_time__date=now.date(),
        is_finished=False
    ).first()

    # إن لم توجد مسابقة مجهزة، أنشئ مسابقة اليوم تلقائياً
    if not quiz:
        quiz = LiveQuiz.objects.create(
            title=f"مسابقة {now.strftime('%Y-%m-%d')} المباشرة",
            start_time=now,
            entry_fee_coins=5,
            revive_cost_coins=5
        )

    # تشغيل محرك المسابقة عبر Celery
    run_live_quiz_engine.delay(quiz.id)