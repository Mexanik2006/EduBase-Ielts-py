from django.urls import path
from . import views

urlpatterns = [
    path('my-groups/', views.mentor_groups, name='mentor_groups'),
    path('my-group/', views.student_group, name='student_group'),
]
