"""
    views only for test purposes
"""
from django.http import JsonResponse
from simplekeys.decorators import key_required


@key_required()
def example(request):
    return JsonResponse({'response': 'OK'})


@key_required(zone='special')
def special(request):
    return JsonResponse({'response': 'special'})


def via_middleware(request):
    return JsonResponse({'response': 'OK'})


def unprotected(request):
    return JsonResponse({'response': 'OK'})
