from rest_framework import status
from .explainability import get_top_contributing_words
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import JobPost, AnalysisResult
from .serializers import RegisterSerializer, UserSerializer, JobPostSerializer
from .analyzer import analyze_job_post
from .ml_analyzer import ml_analyze
from .domain_verifier import verify_company_domain
from .community_signal import get_community_risk_boost


def get_combined_analysis(title, content):
    rule_result = analyze_job_post(title, content)
    
    try:
        ml_result = ml_analyze(title, content)
        combined_score = int(
            (ml_result['score'] * 0.6) +
            (rule_result['score'] * 0.4)
        )
        combined_score = min(combined_score, 100)
        reasons = rule_result['reasons'].copy()
        reasons.append(f"ML model confidence: {ml_result['score']}%")
        
        if combined_score >= 40:
            top_words = get_top_contributing_words(title, content)
            if top_words:
                reasons.append(f"Key flagged words: {', '.join(top_words)}")
    except Exception:
        combined_score = rule_result['score']
        reasons = rule_result['reasons']

    domain_result = verify_company_domain(content)
    if domain_result['domain_found']:
        if domain_result['trust_score'] < 40:
            combined_score = min(combined_score + 15, 100)
        reasons.extend(domain_result['flags'])

    community_result = get_community_risk_boost(content)
    if community_result['boost'] > 0:
        combined_score = min(combined_score + community_result['boost'], 100)
        reasons.append(community_result['reason'])

    if combined_score >= 70:
        risk = "High"
    elif combined_score >= 40:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "score": combined_score,
        "risk": risk,
        "reasons": reasons
    }

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
    title = request.data.get('title', '')
    content = request.data.get('content', '')
    source = request.data.get('source', '')

    job_post = JobPost.objects.create(
        user=request.user,
        title=title,
        content=content,
        source=source
    )

    result = get_combined_analysis(title, content)

    AnalysisResult.objects.create(
        job_post=job_post,
        scam_score=result['score'],
        risk_level=result['risk'],
        reasons=result['reasons']
    )

    serializer = JobPostSerializer(job_post)

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )

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
        job_post = JobPost.objects.get(id=post_id)
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
    
    report_count = ScamReport.objects.filter(job_post=job_post).count()
        
    if report_count >= 3:
        analysis = job_post.analysis
        if "community reports" not in str(analysis.reasons):
            analysis.scam_score = min(analysis.scam_score + 25, 100)
            analysis.risk_level = "High"
            reasons = analysis.reasons
            reasons.append(f"Flagged by {report_count} community reports")
            analysis.reasons = reasons
            analysis.save()
    
    return Response({
        'reported': True,
        'created': created,
        'total_reports': report_count
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_history(request):
    posts = JobPost.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return Response(JobPostSerializer(posts, many=True).data)

