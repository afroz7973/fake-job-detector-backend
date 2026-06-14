from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import JobPost, AnalysisResult
from .serializers import RegisterSerializer, UserSerializer, JobPostSerializer
from .analyzer import analyze_job_post

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_post(request):
    content = request.data.get('content', '')
    title = request.data.get('title', '')
    source = request.data.get('source', '')

    if not content:
        return Response(
            {'error': 'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    job_post = JobPost.objects.create(
    user=request.user,
    title=title,
    content=content,
    source=source
    )

    result = analyze_job_post(title, content)
    score = result["score"]
    risk = result["risk"]
    reasons = result["reasons"]

    analysis = AnalysisResult.objects.create(
        job_post=job_post,
        scam_score=score,
        risk_level=risk,
        reasons=reasons
    )

    return Response(JobPostSerializer(job_post).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_history(request):
    posts = JobPost.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return Response(JobPostSerializer(posts, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_scam(request):
    post_id = request.data.get('post_id')
    if not post_id:
        return Response(
            {'error': 'post_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        job_post = JobPost.objects.get(id=post_id, user=request.user)
    except JobPost.DoesNotExist:
        return Response(
            {'error': 'Post not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    from .models import ScamReport
    report, created = ScamReport.objects.get_or_create(
        job_post=job_post,
        user=request.user
    )
    return Response({'reported': True, 'created': created})