from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
#Verifica a ligação à bd
class CheckDBConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            connections['default'].cursor()
        except OperationalError:
            return JsonResponse(
                {"error": "Falha de ligação, por favor tente mais tarde!"},
                status=503
            )
        return self.get_response(request)
