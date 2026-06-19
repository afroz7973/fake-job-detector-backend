from .models import JobPost, ScamReport
from django.db.models import Count

def get_community_risk_boost(content):
    content_words = set(content.lower().split())
    
    reported_posts = JobPost.objects.annotate(
        report_count=Count('reports')
    ).filter(report_count__gte=3)
    
    for post in reported_posts:
        post_words = set(post.content.lower().split())
        overlap = len(content_words & post_words)
        similarity = overlap / max(len(content_words), 1)
        
        if similarity > 0.5:
            return {
                "boost": 20,
                "reason": f"Similar to a post reported {post.report_count} times by community"
            }
    
    return {"boost": 0, "reason": None}