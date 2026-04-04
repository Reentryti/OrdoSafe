from audit.models import AuditLog

# Function extracting IP adress
def get_client_ip(request):
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or None

# Function to log any events
def log_security_event(user, action, request=None, **metadata):
    
    log_data = {
        'user': user,
        'action': action,
        'metadata': metadata
    }
    
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT')
        })
    
    AuditLog.objects.create(**log_data)