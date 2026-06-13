from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

class JobPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisResult(models.Model):
    job_post = models.OneToOneField(JobPost, on_delete=models.CASCADE, related_name='analysis')
    scam_score = models.IntegerField()
    risk_level = models.CharField(max_length=20)
    reasons = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

class ScamReport(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmed_scam = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)