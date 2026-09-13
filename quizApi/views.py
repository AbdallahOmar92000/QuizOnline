from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import LiveQuiz, QuizParticipant
from .serializers import LiveQuizSerializer, QuizParticipantSerializer

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