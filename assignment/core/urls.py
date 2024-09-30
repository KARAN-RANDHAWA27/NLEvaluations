from django.urls import path
from .views import (
    UserSignupView,
    SignupTemplateView,
    HomeView,
    CustomLoginView,
    LoginAPIView,
    AddAppView,
    UserHomeView,
    UserTaskUploadView,
    AdminTaskReviewView,
    LogoutAPIView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home/', HomeView.as_view(), name='home'),
    path('user/home/', UserHomeView.as_view(), name='user_home'),
    path('signup/', SignupTemplateView.as_view(), name='signup_template'),
    path('api/signup/', UserSignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('apps/', AddAppView.as_view(), name='app_create'),
    path('upload-task/', UserTaskUploadView.as_view(), name='user_task_upload'),
    path('review-tasks/', AdminTaskReviewView.as_view(), name='admin_task_review'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
]
