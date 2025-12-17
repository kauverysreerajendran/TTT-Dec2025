from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Nickel_AuditTrayId)
admin.site.register(Nickel_Audit_Rejection_Table)
admin.site.register(Nickel_Audit_Rejection_ReasonStore)
admin.site.register(Nickel_Audit_Draft_Store)
admin.site.register(Nickel_Audit_TopTray_Draft_Store)
admin.site.register(Nickel_Audit_Rejected_TrayScan)
admin.site.register(Nickel_Audit_Accepted_TrayScan)
admin.site.register(Nickel_Audit_Accepted_TrayID_Store)

