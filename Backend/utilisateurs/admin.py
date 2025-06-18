from django.contrib import admin
from .models import LoginAttempt
from django.contrib.auth import get_user_model

# Register your models here.
@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'username', 'timestamp', 'success', 'failure_reason')
    list_filter = ('success', 'timestamp')
    search_fields = ('ip_address', 'username', 'user__email')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False
    
# Show Custom model view
User = get_user_model()
admin.site.register(User)