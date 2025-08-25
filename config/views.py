from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "message": "안녕 API 서버",
        "status": "running",
        "available_endpoints": [
            "/admin/",
            "/users/",
            "/api/chatrooms/",
            "/reviews/"
        ]
    })