from django.contrib import admin
from .models import *
#test

admin.site.register(PolishFinishType)
admin.site.register(TrayType)
admin.site.register(Vendor)


class ModelMasterAdmin(admin.ModelAdmin):
    list_display = [ 'model_no', 'brand', 'ep_bath_type', 'plating_stk_no']
    search_fields = ['model_no', 'brand', 'plating_stk_no']
    list_filter = ['brand', 'ep_bath_type']
    actions = ['delete_selected']   # ✅ ensure bulk delete enabled
admin.site.register(ModelMaster, ModelMasterAdmin)

admin.site.register(ModelMasterCreation)
admin.site.register(Version)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(TrayId)
admin.site.register(DraftTrayId)

admin.site.register(ModelImage)
admin.site.register(Plating_Color)
admin.site.register(TotalStockModel)
admin.site.register(DP_TrayIdRescan)

admin.site.register(TrayAutoSaveData)
admin.site.register(LookLikeModel)


@admin.register(SSOAccount)
class SSOAccountAdmin(admin.ModelAdmin):
    list_display = ('provider', 'uid', 'user', 'email', 'email_verified', 'created_at')
    search_fields = ('provider', 'uid', 'email', 'user__username')
