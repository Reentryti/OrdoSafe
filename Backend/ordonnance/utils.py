import logging
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings

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

#############################################
# Ordonnance access code send method function


def send_access_code(ordonnance):
    code = ordonnance.access_code

    # If patient got a email
    if ordonnance.patient_email:
        send_mail(
            subject="Votre code d'accès à l'ordonnance",
            message=f"Bonjour {ordonnance.patient_prenom},\n\n"
                    f"Code sécurisé : {code}\n"
                    f"Présentez-le au pharmacien avec votre numéro de téléphone ou email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ordonnance.patient_email],
            fail_silently=True
        )

    # If patient got a phonenumber
    if ordonnance.patient_telephone:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Code ordonnance : {code}",
            from_=settings.TWILIO_FROM_NUMBER,
            to=str(ordonnance.patient_telephone)
        )
