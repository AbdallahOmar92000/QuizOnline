from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,permissions,generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LogInView1(APIView):
    permission_classes =[permissions.AllowAny]

    def post(self,request):
        serializer = LoginSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            data = serializer.validate_date
            user = data['user_instance']
            # جلب IP المستخدم
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

            # تحديث أو إنشاء جلسة الجهاز
            UserDeviceSession.objects.update_or_create(
                user = user,
                device_id=data['device_id'],
                defaults={
                    'device_name': data['device_name'],
                    'ip_address': ip_address,
                    'refresh_token': data['refresh_token'],
                    'is_active': True,
                }
            )
            return Response({
                'access':data['access_token'],
                'refresh':data['refresh_token'],
                'user':data['user']
            },status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# {
#      "email": "a@a.com",
#      "password": "aaa",
#      "device_name": "اسم الجهاز",
#      "device_id": "معرّف الجهاز"
#  }

class LogInView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            data = serializer.validated_data

            user = data['user_instance']

            # جلب IP المستخدم
            ip_address = (
                request.META.get('HTTP_X_FORWARDED_FOR')
                or request.META.get('REMOTE_ADDR')
            )

            # تحديث أو إنشاء جلسة الجهاز
            UserDeviceSession.objects.update_or_create(
                user=user,
                device_id=data['device_id'],
                defaults={
                    'device_name': data['device_name'],
                    'ip_address': ip_address,
                    'refresh_token': data['refresh_token'],
                    'is_active': True,
                }
            )

            # تحويل المستخدم إلى JSON
            user_serializer = UserProfileSerializer(user)

            return Response({
                'access': data['access_token'],
                'refresh': data['refresh_token'],
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



# 3. عرض وتعديل البروفايل (GET/PUT /me)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# 4. تسجيل الخروج من الجهاز الحالي
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            device_id = request.data.get("device_id")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # إبطال التوكن

            if device_id:
                UserDeviceSession.objects.filter(user=request.user, device_id=device_id).delete()

            return Response({"detail": "تم تسجيل الخروج بنجاح."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "الرمز غير صالح أو تم إبطاله مسبقاً."}, status=status.HTTP_400_BAD_REQUEST)


# 5. تسجيل الخروج من جميع الأجهزة
class LogoutAllDevicesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sessions = UserDeviceSession.objects.filter(user=request.user)
        for session in sessions:
            try:
                token = RefreshToken(session.refresh_token)
                token.blacklist()
            except Exception:
                pass
        sessions.delete()
        return Response({"detail": "تم تسجيل الخروج من جميع الأجهزة بنجاح."}, status=status.HTTP_200_OK)        


# 6. عرض قائمة الأجهزة المسجلة للمستخدم
class UserDevicesListView (generics.ListAPIView):
    serializer_class = UserDeviceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserDeviceSession.objects.filter(user=self.request.user)


class AddCoinsRewardView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request):
        reward_coins=5
        user = request.user

        user.coins += reward_coins
        user.save()

        return Response({
            "detail": f"تمت إضافة {reward_coins} عملة بنجاح.",
            "current_coins": user.coins
        }, status=status.HTTP_200_OK)



class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"detail": "كلمة المرور القديمة غير صحيحة."}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "تم تغيير كلمة المرور بنجاح."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Create your views here.
