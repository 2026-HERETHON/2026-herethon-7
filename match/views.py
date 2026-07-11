from django.shortcuts import render


def home(request):
    """Render the home dashboard with temporary data until backend wiring is ready."""
    context = {
        'user_name': '슬기',
        'provided_talent_count': 5,
        'needed_talent_count': 2,
        'ongoing_project_count': 2,
        'ongoing_project': {
            'id': 1,
            'title': '콘텐츠 브랜딩 리뉴얼 프로젝트',
            'progress': 70,
        },
    }
    return render(request, 'match/home.html', context)
