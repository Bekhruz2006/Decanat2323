from django.urls import path
from .views import CurriculumListView

app_name = 'curriculum'

urlpatterns = [
    path('', CurriculumListView.as_view(), name='curriculum_list'),
]