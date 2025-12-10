from django.urls import path
from .views import ScheduleView, ScheduleChangeCreateView

app_name = 'schedule'

urlpatterns = [
    path('', ScheduleView.as_view(), name='schedule_list'),
    path('change/add/', ScheduleChangeCreateView.as_view(), name='schedule_change_create'),
]