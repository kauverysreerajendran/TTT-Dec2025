from django.contrib import admin
from Jig_Loading.models import *
from django.utils.html import format_html



class JigLoadingMasterAdmin(admin.ModelAdmin):
    list_display = ['get_model_stock_no', 'jig_type', 'jig_capacity', 'forging_info']
    list_filter = ['jig_type']
    search_fields = ['model_stock_no__model_no', 'model_stock_no__plating_stk_no', 'jig_type', 'forging_info']
    
    def get_model_stock_no(self, obj):
        """Display the model stock number in a readable format"""
        if obj.model_stock_no and obj.model_stock_no.model_no:
            return obj.model_stock_no.model_no
        return '-'
    get_model_stock_no.short_description = 'Model Stock No'
    get_model_stock_no.admin_order_field = 'model_stock_no__model_no'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "model_stock_no":
            # Ensure queryset shows model_no properly
            kwargs["queryset"] = db_field.remote_field.model.objects.exclude(model_no__isnull=True).exclude(model_no__exact='')
            kwargs["empty_label"] = "Select Model Number"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Jigs Table
class JigAdmin(admin.ModelAdmin):
    list_display = ['jig_qr_id', 'is_loaded', 'get_is_drafted', 'get_current_user', 'get_locked_at',  'created_at', 'updated_at']  # <-- ADD 'get_is_drafted' HERE
    list_filter = ['is_loaded', 'drafted', 'created_at', 'updated_at']
    search_fields = ['jig_qr_id', 'current_user__username', 'current_user__first_name', 'current_user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    #is_drafted
    def get_is_drafted(self, obj):
        return obj.drafted
    get_is_drafted.boolean = True
    get_is_drafted.short_description = 'Is Drafted'
    get_is_drafted.admin_order_field = 'drafted'
    
    #is_loaded
    def mark_as_unloaded(self, request, queryset):
        """Mark selected jigs as unloaded"""
        updated = queryset.update(is_loaded=False)
        self.message_user(request, f"Successfully marked {updated} jig(s) as unloaded.")
    mark_as_unloaded.short_description = "Mark selected jigs as unloaded"
    
    #current user
    def get_current_user(self, obj):
        """Display current user in a readable format"""
        if obj.current_user:
            return f"{obj.current_user.username} ({obj.current_user.get_full_name() or 'No name'})"
        return '-'
    get_current_user.short_description = 'Current User'
    get_current_user.admin_order_field = 'current_user__username'
    
    #locked at
    def get_locked_at(self, obj):
        """Display locked timestamp in a readable format"""
        if obj.locked_at:
            return obj.locked_at.strftime("%Y-%m-%d %H:%M:%S")
        return '-'
    get_locked_at.short_description = 'Locked At'
    get_locked_at.admin_order_field = 'locked_at'
    
    # Add actions for bulk operations
    actions = ['clear_user_locks', 'mark_as_unloaded']
    
    # Clear user locks action
    def clear_user_locks(self, request, queryset):
        """Clear user locks for selected jigs"""
        updated = 0
        for jig in queryset:
            jig.clear_user_lock()
            updated += 1
        self.message_user(request, f"Successfully cleared user locks for {updated} jig(s).")
    clear_user_locks.short_description = "Clear user locks for selected jigs"


# Manual Drafts Table
class JigLoadingManualDraftAdmin(admin.ModelAdmin):
    list_display = [
        'batch_id',
        'lot_id',
        'user',
        'updated_at',
        'get_jig_id',
        'get_no_of_cycle',
        'get_broken_hooks',
        'get_delink_info',
    ]
    search_fields = ['batch_id', 'lot_id', 'user__username']
    readonly_fields = ['updated_at', 'draft_data', 'get_jig_id', 'get_no_of_cycle', 'get_broken_hooks', 'get_delink_info']

    def get_jig_id(self, obj):
        return obj.draft_data.get('jig_id', '-')
    get_jig_id.short_description = 'Jig ID'

    def get_no_of_cycle(self, obj):
        return obj.draft_data.get('no_of_cycle', '-')
    get_no_of_cycle.short_description = 'No of Cycle'

    def get_broken_hooks(self, obj):
        return obj.draft_data.get('broken_buildup_hooks', '-')
    get_broken_hooks.short_description = 'Broken Hooks'

    def get_delink_info(self, obj):
        trays = obj.draft_data.get('trays', [])
        if not trays:
            return "-"
        # Show tray IDs and Plating Stk No if available
        return ", ".join([
            f"{t.get('tray_id', '')} ({obj.draft_data.get('plating_stk_no', '-')})"
            for t in trays if t.get('tray_id')
        ])
    get_delink_info.short_description = 'Delink Information (Tray IDs & Plating Stk No)'

    # Optionally, show if "Add Model" was clicked (if you store this in draft_data)
    def has_added_model(self, obj):
        return obj.draft_data.get('add_model_clicked', False)
    has_added_model.boolean = True
    has_added_model.short_description = 'Add Model Clicked'


admin.site.register(Jig, JigAdmin)
admin.site.register(JigLoadTrayId)
admin.site.register(JigLoadingMaster, JigLoadingMasterAdmin)
admin.site.register(JigDetails)
admin.site.register(BathNumbers)
admin.site.register(JigAutoSave)
admin.site.register(JigLoadingManualDraft, JigLoadingManualDraftAdmin)