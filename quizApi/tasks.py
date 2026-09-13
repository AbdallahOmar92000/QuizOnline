import time
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import LiveQuiz, MultipleChoiceQuestion

@shared_task
def run_live_quiz_engine(quiz_id):
    channel_layer = get_channel_layer()
    room_group_name = f'live_quiz_{quiz_id}'

    try:
        quiz = LiveQuiz.objects.get(id=quiz_id)
        quiz.is_active = True
        quiz.save()
    except LiveQuiz.DoesNotExist:
        return

    questions = list(MultipleChoiceQuestion.objects.filter(quiz=quiz).order_by('order'))
    total_questions = len(questions)

    # 1. بث إشعار بداية المسابقة
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'broadcast_quiz_start',
            'message': 'بدأت المسابقة الآن!',
            'total_questions': total_questions
        }
    )
    time.sleep(3)  # مهلة تحضيرية قبل السؤال الأول

    for index, q in enumerate(questions):
        # 2. بث السؤال للجميع (مدة 15 ثانية)
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'broadcast_question',
                'question_id': q.id,
                'order': q.order,
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
        
        # انتظار 15 ثانية لتلقي إجابات اللاعبين
        time.sleep(15)

        # 3. بث نتيجة السؤال والإجابة الصحيحة + فتح باب الإنعاش للمستبعدين (مدة 5 ثوانٍ)
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

        # انتظار 5 ثوانٍ كفرصة ثانية للانتقال أو خصم 5 Coins
        time.sleep(5)

    # 4. إنهاء المسابقة
    quiz.is_active = False
    quiz.is_finished = True
    quiz.save()

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'broadcast_quiz_finish',
            'message': 'انتهت المسابقة!'
        }
    )