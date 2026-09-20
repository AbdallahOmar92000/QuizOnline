from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import LiveQuiz, QuizParticipant
from .serializers import LiveQuizSerializer, QuizParticipantSerializer
from django.shortcuts import render, get_object_or_404


class UpcomingQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # جلب أول مسابقة قادمة أو مسابقة جارية
        quiz = LiveQuiz.objects.filter(is_finished=False).order_by('start_time').first()
        if not quiz:
            return Response({"detail": "لا توجد مسابقات مجدولة حالياً."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LiveQuizSerializer(quiz)
        
        # التحقق مما إذا كان المستخدم مسجلاً مسبقاً
        participant = QuizParticipant.objects.filter(user=request.user, quiz=quiz).first()
        participant_data = QuizParticipantSerializer(participant).data if participant else None

        return Response({
            "quiz": serializer.data,
            "participant_status": participant_data
        }, status=status.HTTP_200_OK)


class JoinQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        try:
            quiz = LiveQuiz.objects.get(id=quiz_id, is_finished=False)
        except LiveQuiz.DoesNotExist:
            return Response({"detail": "المسابقة غير متاحة."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        participant, created = QuizParticipant.objects.get_or_create(user=user, quiz=quiz)

        now = timezone.now()

        # الدخول كمتسابق أصلي قبل بداية الوقت المحدد
        if now <= quiz.start_time:
            if created or participant.is_spectator:
                if user.coins < quiz.entry_fee_coins:
                    return Response({"detail": "رصيد الـ Coins غير كافٍ للدخول كمتسابق."}, status=status.HTTP_400_BAD_REQUEST)
                
                user.coins -= quiz.entry_fee_coins
                user.save()
                
                participant.is_spectator = False
                participant.save()

            return Response({
                "detail": "تم التسجيل كمتسابق رسمياً.",
                "is_spectator": False,
                "current_coins": user.coins
            }, status=status.HTTP_200_OK)

        # الدخول المتأخر (بعد الانطلاق) -> تسجيلة كـ "ضيف"
        else:
            participant.is_spectator = True
            participant.is_eliminated = True
            participant.save()

            return Response({
                "detail": "لقد بدأت المسابقة بالفعل! تم تسجيلك كـ (ضيف/مشاهد) فقط.",
                "is_spectator": True,
                "current_coins": user.coins
            }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from .models import LiveQuiz, QuizParticipant, QuestionBank

class SubmitAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        user = request.user
        question_id = request.data.get('question_id')
        selected_option = request.data.get('selected_option')

        try:
            quiz = LiveQuiz.objects.get(id=quiz_id, is_active=True)
            question = QuestionBank.objects.get(id=question_id)
            participant, _ = QuizParticipant.objects.get_or_create(user=user, quiz=quiz)
        except (LiveQuiz.DoesNotExist, QuestionBank.DoesNotExist):
            return Response({"error": "المسابقة غير نشطة أو السؤال غير موجود"}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من الإجابة وزيادة النقاط
        is_correct = (selected_option == question.correct_option)
        if is_correct:
            participant.score += 10
            participant.save()

        return Response({
            "is_correct": is_correct,
            "correct_option": question.correct_option,
            "current_score": participant.score
        }, status=status.HTTP_200_OK)


class ReviveParticipantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, quiz_id):
        user = request.user
        try:
            quiz = LiveQuiz.objects.get(id=quiz_id, is_active=True)
            participant = QuizParticipant.objects.get(user=user, quiz=quiz)
        except (LiveQuiz.DoesNotExist, QuizParticipant.DoesNotExist):
            return Response({"error": "المشارك أو المسابقة غير موجودة"}, status=status.HTTP_400_BAD_REQUEST)

        # اقتطاع الـ Coins لإعادة الإنعاش
        revive_cost = quiz.revive_cost_coins
        if user.coins < revive_cost:
            return Response({"error": "رصيد الكوينز غير كافٍ للإنعاش"}, status=status.HTTP_400_BAD_REQUEST)

        user.coins -= revive_cost
        user.save()

        participant.is_eliminated = False
        participant.save()

        return Response({
            "message": "تم الإنعاش بنجاح والعودة للمسابقة",
            "remaining_coins": user.coins
        }, status=status.HTTP_200_OK)



def test_quiz_view(request, quiz_id):
    quiz = get_object_or_404(LiveQuiz, id=quiz_id)
    return render(request, 'quizApi/index.html', {'quiz_id': quiz_id})