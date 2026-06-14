from rest_framework import serializers
from .models import User, JobPost, AnalysisResult

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = ['scam_score', 'risk_level', 'reasons', 'created_at']

class JobPostSerializer(serializers.ModelSerializer):
    analysis = AnalysisResultSerializer(read_only=True)

    class Meta:
        model = JobPost
        fields = ['id', 'title', 'content', 'source', 'created_at', 'analysis']