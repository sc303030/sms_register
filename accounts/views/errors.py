from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse


def custom404(request, exception=None):
    return JsonResponse({
        'detail': _('Requested API URL not found')
    }, status=404, safe=False)

def custom500(request, exception=None):
    return JsonResponse({
        'detail': _('Requested API Server Error')
    }, status=500, safe=False)