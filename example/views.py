from django.http import JsonResponse
from simplekeys.middleware import require_apikey


@require_apikey()
def example(request):
    return JsonResponse({'response': 'OK'})


@require_apikey(zone='special')
def special(request):
    return JsonResponse({'response': 'special'})
