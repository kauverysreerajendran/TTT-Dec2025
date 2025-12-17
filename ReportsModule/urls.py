from django.urls import path
from .views import *

urlpatterns = [
  
    path('reports/', ReportsView.as_view(), name='reports'),
    path('get_batch_details/', get_batch_details, name='get_batch_details'),
    path('get_stage_counts/', get_stage_counts, name='get_stage_counts'),

]



