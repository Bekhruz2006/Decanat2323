from django.urls import path
from .views import GradesByWeekView, GradeCreateView, JournalView

app_name = 'journal'

urlpatterns = [
    path('grades/', GradesByWeekView.as_view(), name='grades_by_week'),
    path('grade/add/', GradeCreateView.as_view(), name='grade_create'),
    path('', JournalView.as_view(), name='journal'),
]