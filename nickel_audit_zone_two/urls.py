from django.urls import path

from DayPlanning import views
from .views import *

urlpatterns = [
    path('NA_Zone_Inspection/', NA_Zone_PickTableView.as_view(), name='NA_Zone_Inspection'),
    path('NA_Zone_Completed/', NA_Zone_CompletedView.as_view(), name='NA_Zone_Completed'),
    path('na_zone_save_hold_unhold_reason/', NA_Zone_SaveHoldUnholdReasonAPIView.as_view(), name='na_zone_save_hold_unhold_reason'),
    path('na_zone_get_tray_capacity_for_lot/', na_zone_get_tray_capacity_for_lot, name='na_zone_get_tray_capacity_for_lot'),
    path('na_zone_save_ip_checkbox/', NA_Zone_SaveIPCheckboxView.as_view(), name='na_zone_save_ip_checkbox'),
    path('na_zone_save_ip_pick_remark/', NA_Zone_SaveIPPickRemarkAPIView.as_view(), name='na_zone_save_ip_pick_remark'),
    path('na_zone_delete_batch/', NA_Zone_DeleteBatchAPIView.as_view(), name='na_zone_delete_batch'),
    path('na_zone_accepted_form/', NA_Zone_Accepted_form.as_view(), name='na_zone_accepted_form'),
    
    path('na_zone_batch_rejection/', NA_Zone_BatchRejectionAPIView.as_view(), name='na_zone_batch_rejection'),
    path('na_zone_tray_rejection/', NA_Zone_TrayRejectionAPIView.as_view(), name='na_zone_tray_rejection'),
    path('na_zone_reject_check_tray_id/', na_zone_reject_check_tray_id, name='na_zone_reject_check_tray_id'),
    path('na_zone_get_accepted_tray_scan_data/', na_zone_get_accepted_tray_scan_data, name='na_zone_get_accepted_tray_scan_data'),
    path('na_zone_view_tray_list/', na_zone_view_tray_list, name='na_zone_view_tray_list'),
    path('na_zone_save_accepted_tray_scan/', na_zone_save_accepted_tray_scan, name='na_zone_save_accepted_tray_scan'),
    path('na_zone_check_tray_id/', na_zone_check_tray_id, name='na_zone_check_tray_id'),
    path('na_zone_get_rejected_tray_scan_data/', na_zone_get_rejected_tray_scan_data, name='na_zone_get_rejected_tray_scan_data'),
    path('na_zone_qc_tray_validate/', NA_Zone_TrayValidateAPIView.as_view(), name='na_zone_qc_tray_validate'),
    path('na_zone_save_single_top_tray_scan/', na_zone_save_single_top_tray_scan, name='na_zone_save_single_top_tray_scan'),
    path('na_zone_reject_check_tray_id_simple/', na_zone_reject_check_tray_id_simple, name='na_zone_reject_check_tray_id_simple'),

    path('na_zone_get_delink_tray_data/', na_zone_get_delink_tray_data, name='na_zone_get_delink_tray_data'),
    path('na_zone_delink_check_tray_id/', na_zone_delink_check_tray_id, name='na_zone_delink_check_tray_id'),
    
    path('na_zone_CompleteTable_tray_id_list/', NA_Zone_TrayIdList_Complete_APIView.as_view(), name='na_zone_CompleteTable_tray_id_list'),
    path('na_zone_complete_tray_validate/', NA_Zone_TrayValidate_Complete_APIView.as_view(), name='na_zone_complete_tray_validate'),

    # Draft functionality endpoints
    path('na_zone_batch_rejection_draft/', NA_Zone_BatchRejectionDraftAPIView.as_view(), name='na_zone_batch_rejection_draft'),
    path('na_zone_tray_rejection_draft/', NA_Zone_TrayRejectionDraftAPIView.as_view(), name='na_zone_tray_rejection_draft'),
    path('na_zone_get_draft_data/', na_zone_get_draft_data, name='na_zone_get_draft_data'),
    path('na_zone_clear_draft/', NA_Zone_ClearDraftAPIView.as_view(), name='na_zone_clear_draft'),
    path('na_zone_get_all_drafts/', NA_Zone_get_all_drafts, name='na_zone_get_all_drafts'),
    path('na_zone_get_top_tray_scan_draft/', na_zone_get_top_tray_scan_draft, name='na_zone_get_top_tray_scan_draft'),

    #Pick table Vlaidation
    path('na_zone_pick_complete_tray_validate/', NA_Zone_PickTrayValidate_Complete_APIView.as_view(), name='na_zone_pick_complete_tray_validate'),
    path('na_zone_pick_CompleteTable_tray_id_list/', NA_Zone_PickTrayIdList_Complete_APIView.as_view(), name='na_zone_pick_CompleteTable_tray_id_list'),

    path('na_zone_tray_delink_top_tray_calc/', NA_Zone_TrayDelinkTopTrayCalcAPIView.as_view(), name='na_zone_tray_delink_top_tray_calc'),
    path('na_zone_validate_tray_id/',NA_Zone_ValidateTrayIdAPIView.as_view(), name='na_zone_validate_tray_id'),
    path('na_zone_tray_delink_and_top_tray_update/', NA_Zone_TrayDelinkAndTopTrayUpdateAPIView.as_view(), name='na_zone_tray_delink_and_top_tray_update'),

]