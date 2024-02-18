from django.contrib import admin
from .models import *
# Register your models here.
class StaffEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'staff_id', 'username', 'host', 'port', 'use_tls')

admin.site.register(StaffEmailConfiguration, StaffEmailConfigurationAdmin)