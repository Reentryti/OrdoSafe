import logging

medical_logger = logging.getLogger('medical.audit')
security_logger = logging.getLogger('security.audit')


# Medical log 
def log_medical_action(user, action, ordonnance_id=None, patient=None, details=None):
    message_parts = [
        f"USER: {user.get_full_name()} ({user.email})",
        f"ACTION: {action}",
    ]
    
    if ordonnance_id:
        message_parts.append(f"ORDONNANCE: #{ordonnance_id}")
    
    if patient:
        message_parts.append(f"PATIENT: {patient.user.get_full_name()}")
    
    if details:
        message_parts.append(f"DETAILS: {details}")
    
    medical_logger.info(" | ".join(message_parts))



# Security log
def log_security_event(user, event, ordonnance_id=None, ip_address=None, details=None):
    
    message_parts = [
        f"USER: {user.get_full_name() if user.is_authenticated else 'ANONYMOUS'} ({user.username if user.is_authenticated else 'unknown'})",
        f"EVENT: {event}",
    ]
    
    if ordonnance_id:
        message_parts.append(f"ORDONNANCE: #{ordonnance_id}")
    
    if ip_address:
        message_parts.append(f"IP: {ip_address}")
    
    if details:
        message_parts.append(f"DETAILS: {details}")
    
    security_logger.warning(" | ".join(message_parts))
