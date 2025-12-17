from django.urls import path
from . import views

urlpatterns = [
    path('zone_spider_composition/', views.Zone_SpiderCompositionView.as_view(), name='zone_spider_composition'),
  
    path('zone_spider_pick_table/', views.Zone_SpiderPickTableView.as_view(), name='zone_spider_pick_table'),
    path('Zone_jig_update_batch_quantity/',views.Zone_JIGUpdateBatchQuantityAPIView.as_view(), name='Zone_jig_update_batch_quantity'),
    path('Zone_spider_jig_delete_batch/', views.Zone_JIGDeleteBatchAPIView.as_view(), name='Zone_spider_jig_delete_batch'),
    path('Zone_fetch_jig_related_data/', views.Zone_fetch_jig_related_data, name='Zone_fetch_jig_related_data'),
    path('Zone_SpiderCompletedTableView/', views.Zone_SpiderCompletedTableView.as_view(), name='Zone_SpiderCompletedTableView'),
    path('Zone_save_jig_details/', views.Zone_SpiderJigDetailsSaveAPIView.as_view(), name='Zone_save_jig_details'),
    path('Zone_update_jig_details/', views.Zone_SpiderJigDetailsUpdateAPIView.as_view(), name='Zone_update_jig_details'),
    path('Zone_validate_jig_qr/', views.Zone_SpiderJigDetailsValidateQRAPIView.as_view(), name='Zone_validate_jig_qr'),
    path('Zone_validate_spider_tray_id/', views.Zone_validate_spider_tray_id, name='Zone_validate_spider_tray_id'),
    path('Zone_spider_save_ip_pick_remark/', views.Zone_SpiderSaveIPPickRemarkAPIView.as_view(), name='Zone_spider_save_ip_pick_remark'),
    path('Zone_get_cycle_count/', views.Zone_SpiderJigCycleCountAPIView.as_view(), name='jig_Zone_get_cycle_count'),
    path('Zone_jig_tray_id_list/', views.Zone_JIGTrayIdList_Complete_APIView.as_view(), name='Zone_jig_tray_id_list'),
    path('Zone_jig_tray_validate/', views.Zone_JIGTrayValidate_Complete_APIView.as_view(), name='Zone_jig_tray_validate'),
    path('Zone_get_multi_model_distribution/', views.Zone_get_multi_model_distribution, name='Zone_get_multi_model_distribution'),

    path('Zone_spider_save_hold_unhold_reason/', views.Zone_Spider_SaveHoldUnholdReasonAPIView.as_view(), name='Zone_spider_save_hold_unhold_reason'),

]