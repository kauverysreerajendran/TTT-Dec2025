import random
from django.http import HttpResponseServerError

class RandomServerErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 10% chance to show fake 500 error
        if random.random() < 0.1:
            return HttpResponseServerError("Simulated backend outage. Try again later.")
        return self.get_response(request)
