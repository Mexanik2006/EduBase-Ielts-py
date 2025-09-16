from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:exam_id>/', views.submit_attempt, name='submit_attempt'),
    path('review/<int:attempt_id>/', views.review_attempt, name='review_attempt'),
    path('my-attempts/', views.my_attempts, name='my_attempts'),
    path('pending-reviews/', views.pending_reviews, name='pending_reviews'),
]
