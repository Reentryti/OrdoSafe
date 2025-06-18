from django.utils.deprecation import MiddlewareMixin
from .models import LoginAttempt
from django.http import HttpResponseForbidden
from django.conf import settings

# Middleware to log login attempts
class LoginAttemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST' and request.path == '/account/login/':
            request.login_attempt_data = {
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'username': request.POST.get('username') or request.POST.get('email'),
            }
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

# Middleware to block access
class BlockMaliciousIPMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)

        failure_count = LoginAttempt.objects.filter(
            ip_address=ip,
            success=False,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()

        if failure_count >= settings.MAX_LOGIN_ATTEMPTS_PER_IP:
            return HttpResponseForbidden("Trop de tentatives de connexion dépassé. Veuillez réessayer plus tard.")

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')