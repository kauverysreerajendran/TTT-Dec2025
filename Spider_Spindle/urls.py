from django.urls import path
from . import views

urlpatterns = [
    path('spider_composition/', views.SpiderCompositionView.as_view(), name='spider_composition'),
  
    path('spider_pick_table/', views.SpiderPickTableView.as_view(), name='spider_pick_table'),
    path('jig_update_batch_quantity/',views.JIGUpdateBatchQuantityAPIView.as_view(), name='jig_update_batch_quantity'),
    path('spider_jig_delete_batch/', views.JIGDeleteBatchAPIView.as_view(), name='spider_jig_delete_batch'),
    path('fetch_jig_related_data/', views.fetch_jig_related_data, name='fetch_jig_related_data'),
    path('SpiderCompletedTableView/', views.SpiderCompletedTableView.as_view(), name='SpiderCompletedTableView'),
    path('save_jig_details/', views.SpiderJigDetailsSaveAPIView.as_view(), name='save_jig_details'),
    path('update_jig_details/', views.SpiderJigDetailsUpdateAPIView.as_view(), name='update_jig_details'),
    path('validate_jig_qr/', views.SpiderJigDetailsValidateQRAPIView.as_view(), name='validate_jig_qr'),
    path('validate_spider_tray_id/', views.validate_spider_tray_id, name='validate_spider_tray_id'),
    path('spider_save_ip_pick_remark/', views.SpiderSaveIPPickRemarkAPIView.as_view(), name='spider_save_ip_pick_remark'),
    path('get_cycle_count/', views.SpiderJigCycleCountAPIView.as_view(), name='jig_get_cycle_count'),
    path('jig_tray_id_list/', views.JIGTrayIdList_Complete_APIView.as_view(), name='jig_tray_id_list'),
    path('jig_tray_validate/', views.JIGTrayValidate_Complete_APIView.as_view(), name='jig_tray_validate'),
    path('get_multi_model_distribution/', views.get_multi_model_distribution, name='get_multi_model_distribution'),

    path('spider_save_hold_unhold_reason/', views.Spider_SaveHoldUnholdReasonAPIView.as_view(), name='spider_save_hold_unhold_reason'),

]