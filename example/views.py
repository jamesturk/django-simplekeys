from django.http import JsonResponse
from simplekeys.middleware import require_apikey


@require_apikey
def example(request):
    return JsonResponse({'response': 'OK'})
