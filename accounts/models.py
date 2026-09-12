from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('يجب تقديم البريد الإلكتروني')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # إزالة اسم المستخدم واكتفاء بالبريد كمعرف أساسي
    username = None
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الهاتف")
    
    # حقول نظام الـ Coins
    coins = models.PositiveIntegerField(default=10, verbose_name="رصيد الـ Coins")
    
    # الصلاحيات والتحكم الإداري بالتطبيقات
    can_access_quiz_app = models.BooleanField(default=True, verbose_name="السماح بتطبيق المسابقات")
    can_access_other_app = models.BooleanField(default=True, verbose_name="السماح بالتطبيق الآخر")
    is_blocked = models.BooleanField(default=False, verbose_name="حظر المستخدم")
    is_email_verified = models.BooleanField(default=False, verbose_name="تم تأكيد البريد")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name})"


class UserDeviceSession(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='device_session', verbose_name="المستخدم")
    device_name = models.CharField(max_length=255,verbose_name='اسم الجهاز / الموديل')
    device_id = models.CharField(max_length=255,verbose_name='المعرف الفريد للجهاز')
    ip_address = models.GenericIPAddressField(null=True,blank=True, verbose_name="عنوان IP")
    refresh_token = models.TextField(verbose_name="Refresh Token")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_login = models.DateTimeField(auto_now=True, verbose_name="آخر ظهور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ تسجيل الدخول")

    class Meta:
        verbose_name = "جلسة جهاز"
        verbose_name_plural = "جلسات الأجهزة"
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"{self.user.email} - {self.device_name}"

    