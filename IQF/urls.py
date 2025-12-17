from django.urls import path

from Brass_QC import views
from .views import * 

urlpatterns = [
    path('iqf_picktable/', IQFPickTableView.as_view(), name='iqf_picktable'),
    path('iqf_accept_table/', IQFAcceptTableView.as_view(), name='iqf_accept_table'),

    path('iqf_save_hold_unhold_reason/', IQFSaveHoldUnholdReasonAPIView.as_view(), name='iqf_save_hold_unhold_reason'),

    path('iqf_get_brass_rejection_quantities/', iqf_get_brass_rejection_quantities, name='iqf_get_brass_rejection_quantities'),

    path('iqf_complete_tray_validate/', IQFTrayValidate_Complete_APIView.as_view(), name='iqf_complete_tray_validate'),
    path('iqf_CompleteTable_tray_id_list/', IQFCompleteTableTrayIdListAPIView.as_view(), name='iqf_CompleteTable_tray_id_list'),
    path('iqf_pick_CompleteTable_tray_id_list/', IQFPickCompleteTableTrayIdListAPIView.as_view(), name='iqf_pick_CompleteTable_tray_id_list'),
    path('iqf_accept_CompleteTable_tray_id_list/', IQFAcceptCompleteTableTrayIdListAPIView.as_view(), name='iqf_accept_CompleteTable_tray_id_list'),

    path('iqf_RejectTable_tray_id_list/', IQFRejectTableTrayIdListAPIView.as_view(), name='iqf_RejectTable_tray_id_list'),

    path('iqf_save_ip_checkbox/', IQFSaveIPCheckboxView.as_view(), name='iqf_save_ip_checkbox'),
    path('iqf_save_ip_pick_remark/', IQFSaveIPPickRemarkAPIView.as_view(), name='iqf_save_ip_pick_remark'),
    path('iqf_delete_batch/', IQFDeleteBatchAPIView.as_view(), name='iqf_delete_batch'),
    path('iqf_lot_rejection/', IQFLotRejectionAPIView.as_view(), name='iqf_lot_rejection'),
    
    # Draft endpoints
    path('iqf_lot_rejection_draft/', IQFLotRejectionDraftAPIView.as_view(), name='iqf_lot_rejection_draft'),
    path('iqf_tray_rejection_draft/', IQFTrayRejectionDraftAPIView.as_view(), name='iqf_tray_rejection_draft'),
    path('iqf_clear_draft/', IQFClearDraftAPIView.as_view(), name='iqf_clear_draft'),
    path('iqf_get_draft_data/', iqf_get_draft_data, name='iqf_get_draft_data'),
    path('iqf_get_all_drafts/', iqf_get_all_drafts, name='iqf_get_all_drafts'),
    
    path('iqf_tray_rejection/', IQFTrayRejectionAPIView.as_view(), name='iqf_tray_rejection'),
    path('iqf_reject_check_tray_id/', iqf_reject_check_tray_id, name='iqf_reject_check_tray_id'),
    path('iqf_get_accepted_tray_scan_data/', iqf_get_accepted_tray_scan_data, name='iqf_get_accepted_tray_scan_data'),
    path('iqf_view_tray_list/', iqf_view_tray_list, name='iqf_view_tray_list'),
    path('iqf_check_tray_id/', iqf_check_tray_id, name='iqf_check_tray_id'),
    path('iqf_get_rejected_tray_scan_data/', iqf_get_rejected_tray_scan_data, name='iqf_get_rejected_tray_scan_data'),
    path('iqf_tray_validate/', IQFTrayValidateAPIView.as_view(), name='iqf_tray_validate'),
    path('iqf_completed_table/', IQFCompletedTableView.as_view(), name='iqf_completed_table'),
    path('iqf_rejection_table/', IQFRejectTableView.as_view(), name='iqf_rejection_table'),
    path('iqf_get_rejection_details/',iqf_get_rejection_details,name="iqf_get_rejection_details"),
    path('get_tray_capacity/', get_tray_capacity, name='get_tray_capacity'),

    path('iqf_reject_check_tray_id_simple/', iqf_reject_check_tray_id_simple, name='iqf_reject_check_tray_id_simple'),
    path('iqf_get_delink_candidates/', iqf_get_delink_candidates, name='iqf_get_delink_candidates'),
    path('iqf_get_rejected_trays/', iqf_get_rejected_trays, name='iqf_get_rejected_trays'),
    path('iqf_get_remaining_trays/', iqf_get_remaining_trays, name='iqf_get_remaining_trays'),
    path('iqf_validate_delink_tray/', iqf_validate_delink_tray, name='iqf_validate_delink_tray'),
    path('iqf_process_all_tray_data/', iqf_process_all_tray_data, name='iqf_process_all_tray_data'),
    path('iqf_save_draft_tray_ids/', iqf_save_draft_tray_ids, name='iqf_save_draft_tray_ids'),

    path('iqf_delink_selected_trays/', iqf_delink_selected_trays, name='iqf_delink_selected_trays'),

     # Optimal Distribution Draft URLs - Class-based view (recommended)
    path('optimal_distribution_draft/', IQFOptimalDistributionDraftView.as_view(), name='iqf_optimal_distribution_draft'),
    
    # OR function-based views (alternative)
    path('iqf_check_optimal_distribution_draft/', iqf_check_optimal_distribution_draft, name='iqf_check_optimal_distribution_draft'),
    path('iqf_save_optimal_distribution_draft/', iqf_save_optimal_distribution_draft, name='iqf_save_optimal_distribution_draft'),
    path('iqf_load_optimal_distribution_draft/', iqf_load_optimal_distribution_draft, name='iqf_load_optimal_distribution_draft'),

    path('iqf_tray_delink_top_tray_calc/', IQFTrayDelinkTopTrayCalcAPIView.as_view(), name='iqf_tray_delink_top_tray_calc'),
    path('iqf_validate_tray_id/', IQFValidateTrayIdAPIView.as_view(), name='iqf_validate_tray_id'),
    path('iqf_tray_delink_and_top_tray_update/', IQFTrayDelinkAndTopTrayUpdateAPIView.as_view(), name='iqf_tray_delink_and_top_tray_update'),

    # Manual Draft and Auto-Save endpoints (Following Brass QC pattern)
    path('iqf_set_manual_draft/', IQFSetManualDraftAPIView.as_view(), name='iqf_set_manual_draft'),
    path('iqf_save_rejection_draft/', IQFSaveRejectionDraftAPIView.as_view(), name='iqf_save_rejection_draft'),
    path('iqf_save_accepted_tray_draft/', IQFSaveAcceptedTrayDraftAPIView.as_view(), name='iqf_save_accepted_tray_draft'),

    # Barcode scanner API endpoint
    path('get_lot_id_for_tray/', get_lot_id_for_tray, name='get_lot_id_for_tray'),

]