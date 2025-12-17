from django.urls import path
from . import views

urlpatterns = [
    path('jig_composition/', views.JigCompositionView.as_view(), name='jig_composition'),
    path('check_meaningful_draft/', views.CheckMeaningfulDraftView.as_view(), name='check_meaningful_draft'),
    path('clear_specific_lot_draft/', views.ClearSpecificLotDraftView.as_view(), name='clear_specific_lot_draft'),

    path('JigView/', views.JigPickTableView.as_view(), name='JigView'),
    path('jig_update_batch_quantity/',views.JIGUpdateBatchQuantityAPIView.as_view(), name='jig_update_batch_quantity'),
    path('jig_delete_batch/', views.JIGDeleteBatchAPIView.as_view(), name='jig_delete_batch'),
    path('fetch_jig_related_data/', views.fetch_jig_related_data, name='fetch_jig_related_data'),
    path('JigCompletedTable/', views.JigCompletedTable.as_view(), name='JigCompletedTable'),
    path('save_jig_details/', views.JigDetailsSaveAPIView.as_view(), name='save_jig_details'),
    path('clear_jig_draft/',views.JigDetailsClearDraftAPIView.as_view(),name='clear_jig_draft'),
    
    path('update_jig_details/', views.JigDetailsUpdateAPIView.as_view(), name='update_jig_details'),
    path('validate_jig_qr/', views.JigDetailsValidateQRAPIView.as_view(), name='validate_jig_qr'),
    path('validate_tray_id/', views.validate_tray_id, name='validate_tray_id'),
    path('jig_save_ip_pick_remark/', views.JIGSaveIPPickRemarkAPIView.as_view(), name='jig_save_ip_pick_remark'),
    path('get_cycle_count/', views.JigCycleCountAPIView.as_view(), name='jig_get_cycle_count'),
    path('jig_tray_id_list/', views.JIGTrayIdList_Complete_APIView.as_view(), name='jig_tray_id_list'),
    path('jig_tray_validate/', views.JIGTrayValidate_Complete_APIView.as_view(), name='jig_tray_validate'),
    path('get_multi_model_distribution/', views.get_multi_model_distribution, name='get_multi_model_distribution'),
    path('jig_save_hold_unhold_reason/', views.Jig_SaveHoldUnholdReasonAPIView.as_view(), name='jig_save_hold_unhold_reason'),
    # Add these to your existing URL patterns
    path('save_jig_unload_draft/',views.save_jig_unload_draft, name='save_jig_unload_draft'),
    path('get_jig_unload_drafts/', views.get_jig_unload_drafts, name='get_jig_unload_drafts'), 
    path('load_jig_unload_draft/', views.load_jig_unload_draft, name='load_jig_unload_draft'),
    path('autosave/', views.jig_autosave, name='jig_autosave'),
    path('autosave/<str:lot_id>/', views.get_jig_autosave, name='get_jig_autosave'),
    path('autosave/<str:lot_id>/clear/', views.clear_jig_autosave, name='clear_jig_autosave'),

]