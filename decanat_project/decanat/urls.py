from django.urls import path
from .views import StudentListView, StudentDetailView

app_name = 'decanat'

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
]