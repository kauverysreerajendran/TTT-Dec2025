from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(IQFTrayId)
admin.site.register(IQF_Draft_Store)


admin.site.register(IQF_Accepted_TrayScan)
admin.site.register(IQF_Accepted_TrayID_Store)
admin.site.register(IQF_Rejection_ReasonStore)
admin.site.register(IQF_Rejected_TrayScan)
admin.site.register(IQF_Rejection_Table)
admin.site.register(IQF_OptimalDistribution_Draft)
