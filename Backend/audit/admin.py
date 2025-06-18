from django.contrib import admin
from audit.models import AuditLog

# Register your models here.

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = (
        'user__email',
        'user__first_name', 
        'user__last_name',
        'ip_address'
    )
    readonly_fields = ('action', 'user', 'timestamp', 'metadata_prettified')
    date_hierarchy = 'timestamp'

    def metadata_prettified(self, instance):
        import json
        return json.dumps(instance.metadata, indent=2)
    metadata_prettified.short_description = 'Metadata (formatted)'

    def has_add_permission(self, request):
        return False