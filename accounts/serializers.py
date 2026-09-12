from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

# 1. Serializer التسجيل (Register)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        # التحقق من تطابق كلمتي المرور
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "كلمتا المرور غير متطابقتين."})
        return attrs

    def create(self, validated_data):
        # إزالة password_confirm قبل الإنشاء
        validated_data.pop('password_confirm')
        # إنشاء المستخدم وتشفير كلمة المرور
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user


# 2. Serializer تسجيل الدخول (Login)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    device_name = serializers.CharField(required=True, write_only=True)
    device_id = serializers.CharField(required=True, write_only=True)

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError({"detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة."})

            if user.is_blocked:
                raise serializers.ValidationError({"detail": "هذا الحساب محظور من قبل الإدارة."})

            if not user.can_access_quiz_app:
                raise serializers.ValidationError({"detail": "ليس لديك صلاحية للوصول لتطبيق المسابقات."})

            refresh = RefreshToken.for_user(user)

            return {
                'email': user.email,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'device_name': attrs.get('device_name'),
                'device_id': attrs.get('device_id'),
                'user_instance': user
            }
        else:
            raise serializers.ValidationError({"detail": "يجب تقديم جميع البيانات المطلوبة."})

    def get_user(self, obj):
        user = obj.get('user_instance')
        return UserProfileSerializer(user).data

# 3. Serializer عرض وتعديل بيانات البروفايل (GET /me)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'coins', 'can_access_quiz_app', 'can_access_other_app', 
            'is_blocked', 'is_email_verified'
        ]
        read_only_fields = ['id', 'email', 'coins', 'can_access_quiz_app', 'can_access_other_app', 'is_blocked', 'is_email_verified']


class UserDeviceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceSession
        fields = ['id', 'device_name', 'device_id', 'ip_address', 'is_active', 'last_login', 'created_at']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


