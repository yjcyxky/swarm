from django.http import JsonResponse
from rest_framework import status


def custom404(request):
    return JsonResponse({
        'status_code': 404,
        'details': 'The resource was not found.',
        'status': 'Failed'
    }, status=status.HTTP_404_NOT_FOUND)
