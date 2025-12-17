from django.db import models
from django.utils import timezone
from django.db.models import F
from django.core.exceptions import ValidationError
import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
import uuid

# JIG Usage Log Model
class JigUsageLog(models.Model):
    jig_qr_id = models.CharField(max_length=100)
    tray_id = models.CharField(max_length=100)
    tray_quantity = models.IntegerField()
    tray_capacity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    used_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, default='load')  # 'load' or 'unload'

    def __str__(self):
        return f"{self.jig_qr_id} used for tray {self.tray_id} by {self.user}"


#jig qr model
class Jig(models.Model):
    jig_qr_id = models.CharField(max_length=100, unique=True, help_text="Unique Jig QR ID")
    jig_id_tracking = models.BooleanField(default=False, help_text="Tracks if this Jig QR ID is currently in use")
    ready_for_unload = models.BooleanField(default=False, help_text="Jig QR ID is ready for unload")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.jig_qr_id
 

# Create your models here.
class JigLoadTrayId(models.Model):
    """
    BrassTrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100,  help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    batch_id = models.ForeignKey('modelmasterapp.ModelMasterCreation', on_delete=models.CASCADE, blank=True, null=True)
    recovery_batch_id = models.ForeignKey('Recovery_DP.RecoveryMasterCreation', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    top_tray = models.BooleanField(default=False)


    delink_tray = models.BooleanField(default=False, help_text="Is tray delinked")
    delink_tray_qty = models.CharField(max_length=50, null=True, blank=True, help_text="Delinked quantity")
    
    IP_tray_verified= models.BooleanField(default=False, help_text="Is tray verified in IP")
    
    rejected_tray= models.BooleanField(default=False, help_text="Is tray rejected")

    new_tray=models.BooleanField(default=True, help_text="Is tray new")
    
    # Tray configuration fields (filled by admin)
    tray_type = models.CharField(max_length=50, null=True, blank=True, help_text="Type of tray (Jumbo, Normal, etc.) - filled by admin")
    tray_capacity = models.IntegerField(null=True, blank=True, help_text="Capacity of this specific tray - filled by admin")

    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} - {self.tray_quantity}"

    @property
    def is_available_for_scanning(self):
        """
        Check if tray is available for scanning
        Available if: not scanned OR delinked (can be reused)
        """
        return not self.scanned or self.delink_tray

    @property
    def status_display(self):
        """Get human-readable status"""
        if self.delink_tray:
            return "Delinked (Reusable)"
        elif self.scanned:
            return "Already Scanned"
        elif self.batch_id:
            return "In Use"
        else:
            return "Available"

    class Meta:
        verbose_name = "Jig Load Tray ID"
        verbose_name_plural = "Jig Load Tray IDs"
        
#jig Loading master
class JigLoadingMaster(models.Model):
    model_stock_no = models.ForeignKey('modelmasterapp.ModelMaster', on_delete=models.CASCADE, help_text="Model Stock Number")
    jig_type = models.CharField(max_length=100, help_text="Jig Type")
    jig_capacity = models.IntegerField(help_text="Jig Capacity")
    forging_info = models.CharField(max_length=100, help_text="Forging Info")
    
    def __str__(self):
        return f"{self.model_stock_no} - {self.jig_type} - {self.jig_capacity}"

class BathNumbers(models.Model):
    bath_number=models.CharField(max_length=100)


class JigDetails(models.Model):
    JIG_POSITION_CHOICES = [
        ('Top', 'Top'),
        ('Middle', 'Middle'),
        ('Bottom', 'Bottom'),
    ]
    jig_qr_id = models.CharField(max_length=100)
    faulty_slots = models.IntegerField(default=0)
    jig_type = models.CharField(max_length=50)  # New field
    jig_capacity = models.IntegerField()        # New field
    bath_tub = models.CharField(max_length=100, help_text="Bath Tub", blank=True, null=True)
    plating_color = models.CharField(max_length=50)
    empty_slots = models.IntegerField(default=0)
    ep_bath_type = models.CharField(max_length=50)
    total_cases_loaded = models.IntegerField()
    # JIG Loading Module - Remaining cases
    jig_cases_remaining_count = models.IntegerField(default=0, blank=True, null=True)

    forging = models.CharField(max_length=100)
    no_of_model_cases = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    no_of_cycle = models.IntegerField(default=1)
    lot_id = models.CharField(max_length=100)
    new_lot_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    electroplating_only = models.BooleanField(default=False)
    lot_id_quantities = JSONField(blank=True, null=True)
    draft_save = models.BooleanField(default=False, help_text="Draft Save")
    delink_tray_data = models.JSONField(default=list, blank=True, null=True)  # Add this field
    half_filled_tray_data = models.JSONField(default=list, blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    bath_numbers = models.ForeignKey(
        BathNumbers,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Related Bath Numbers"
    )

    jig_position = models.CharField(
        max_length=10,
        choices=JIG_POSITION_CHOICES,
        default='Top',
        help_text="Jig position: Top, Middle, or Bottom"
    )
    remarks = models.CharField(
        max_length=50,
        blank=True,
        help_text="Remarks (max 50 words)"
    )
    pick_remarks = models.CharField(
        max_length=50,
        blank=True,
        help_text="Remarks (max 50 words)"
    )

    jig_unload_draft = models.BooleanField(default=False)
    combined_lot_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    jig_loaded_date_time = models.DateTimeField(null=True, blank=True, help_text="Last Process Date/Time")
    IP_loaded_date_time = models.DateTimeField(null=True, blank=True, help_text="Ip last Process Date/Time")
    last_process_module = models.CharField(max_length=100, blank=True, help_text="Last Process Module")
    unload_over = models.BooleanField(default=False)
    Un_loaded_date_time = models.DateTimeField(null=True, blank=True, help_text="Ip last Process Date/Time")
    jig_lot_id = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Unique Jig Lot ID")

    unload_holding_reason = models.CharField(max_length=255, null=True, blank=True, help_text="Unload Reason for holding the batch")
    unload_release_reason = models.CharField(max_length=255, null=True, blank=True, help_text="Unload Reason for releasing the batch")
    unload_hold_lot = models.BooleanField(default=False, help_text="Indicates if the lot is on hold n Unload")
    unload_release_lot = models.BooleanField(default=False)
    unloading_remarks = models.CharField(max_length=100, null=True, blank=True, help_text="JIG Pick Remarks")

    def __str__(self):
        return f"{self.jig_qr_id} - {self.jig_lot_id} - {self.no_of_cycle}"

    def save(self, *args, **kwargs):
        # ✅ Prevent moving to next cycle until fully unloaded
        # ✅ Only check cycle validation for actual cycle increments, not updates
        if hasattr(self, '_state') and self._state.adding:  # Only for new records
            if self.no_of_cycle > 1:  # means trying to move to next cycle
                if not self.unload_over:
                    raise ValidationError("Jig QR ID cannot move to next cycle until it is fully unloaded.")
        elif self.pk:  # For existing records
            try:
                old_instance = JigDetails.objects.get(pk=self.pk)
                if self.no_of_cycle > old_instance.no_of_cycle:  # Actual cycle increment
                    if not self.unload_over:
                        raise ValidationError("Jig QR ID cannot move to next cycle until it is fully unloaded.")
            except JigDetails.DoesNotExist:
                pass

        # ✅ UPDATED: Only prevent reuse for DRAFT saves when tracking is enabled
        # For final submissions (draft_save=False), allow the save to proceed and mark as ready for unload
        if self.draft_save:  # Only restrict for draft saves
            if Jig.objects.filter(jig_qr_id=self.jig_qr_id, jig_id_tracking=True).exists():
                # Check if there's already a draft for this Jig QR ID
                existing_draft = JigDetails.objects.filter(
                    jig_qr_id=self.jig_qr_id, 
                    draft_save=True
                ).exclude(pk=self.pk).first()
                
                if existing_draft:
                    raise ValidationError("This Jig QR ID is in Draft state and cannot be reused until draft is cleared or submitted.")

        # ✅ Prevent reuse if a draft exists for this Jig QR ID (but allow updating the same draft)
        if JigDetails.objects.filter(jig_qr_id=self.jig_qr_id, draft_save=True).exclude(pk=self.pk).exists():
            raise ValidationError("This Jig QR ID is in Draft state and cannot be reused until draft is cleared or submitted.")

        # auto-generate jig_lot_id if not set
        if not self.jig_lot_id:
            import uuid
            self.jig_lot_id = f"JLOT-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)





class JigAutoSave(models.Model):
    """Auto-save for jig loading modal inputs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lot_id = models.CharField(max_length=100, db_index=True)
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users
    
    # Auto-save data
    jig_qr_id = models.CharField(max_length=100, blank=True)
    faulty_slots = models.IntegerField(default=0)
    empty_slots = models.IntegerField(default=0)
    total_cases_loaded = models.IntegerField(default=0)
    delink_tray_data = models.JSONField(default=list)
    half_filled_tray_data = models.JSONField(default=list)
    lot_id_quantities = models.JSONField(default=dict)
    selected_model_nos = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'lot_id']
        indexes = [models.Index(fields=['user', 'lot_id', 'updated_at'])]
    
    def is_expired(self, hours=24):
        return timezone.now() - self.updated_at > timedelta(hours=hours)
    
    def to_dict(self):
        return {
            'jig_qr_id': self.jig_qr_id,
            'faulty_slots': self.faulty_slots,
            'empty_slots': self.empty_slots,
            'total_cases_loaded': self.total_cases_loaded,
            'delink_tray_data': self.delink_tray_data,
            'half_filled_tray_data': self.half_filled_tray_data,
            'lot_id_quantities': self.lot_id_quantities,
            'selected_model_nos': self.selected_model_nos,
        }