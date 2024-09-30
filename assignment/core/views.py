from rest_framework import viewsets, generics
from .models import App, Task, User
from .serializers import AppSerializer, TaskSerializer, UserSerializer, AdminTaskReviewSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from rest_framework.views import APIView
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import logout


logger = logging.getLogger(__name__)



class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class UserSignupView(generics.CreateAPIView):
       queryset = User.objects.all()
       serializer_class = UserSerializer
       permission_classes = [AllowAny]

       def create(self, request, *args, **kwargs):
           serializer = self.get_serializer(data=request.data)
           if serializer.is_valid():
               user = serializer.save()
               return Response(serializer.data, status=status.HTTP_201_CREATED)
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupTemplateView(TemplateView):
    template_name = 'signup.html'

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apps'] = App.objects.all()
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'

class LoginAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')


        user = authenticate(request, username=username, password=password)

        if user is not None:
            
            login(request, user)

            refresh = RefreshToken.for_user(user)
            if user.is_superuser:
                redirect_url = '/api/home/'
            else:
                redirect_url = '/user/home/'

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'redirect_url': redirect_url 
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                

class AddAppView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    template_name = 'add_apps.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        serializer = AppSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        
        print("Errors: %s", serializer.errors)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserHomeView(TemplateView):
    template_name = 'user_home.html'
    permission_classes = [IsAuthenticated]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        apps = App.objects.all()
        tasks = Task.objects.filter(user=user.id)
        app_data = []
        for app in apps:
            user_task = tasks.filter(app=app).first()
            app_info = {
                'id': app.id,
                'name': app.name,
                'image': app.image.url,
                'points': app.points,
                'link': app.link,
                'screenshot': user_task.screenshot.url if user_task and user_task.screenshot else None,
                'user_task_completed': user_task.completed if user_task else 'F'
            }
            app_data.append(app_info)

        user_profile = {
            'username': user.username,
            'email': user.email,
        }
        completed_tasks = tasks.filter(completed='S')

        total_points = sum(task.app.points for task in completed_tasks)
        context['apps'] = app_data
        context['user_profile'] = user_profile
        context['total_points'] = total_points
        context['tasks'] = tasks.values('app__name', 'completed') 
        return context


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class UserTaskUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id 
        serializer = TaskSerializer(data=data)
        
        if serializer.is_valid():
            app_id = data.get('app')
            screenshot = data.get('screenshot')

            try:
                app = App.objects.get(id=app_id)
            except App.DoesNotExist:
                return Response({"success": False, "error": "App not found."}, status=status.HTTP_404_NOT_FOUND)

            task, created = Task.objects.get_or_create(user=user, app=app, defaults={'screenshot': screenshot})
            if not created:
                task.screenshot = screenshot
                task.save()

            return Response({"success": True, "message": "Task uploaded successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False,},serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class AdminTaskReviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        tasks = Task.objects.all()
        serializer = AdminTaskReviewSerializer(tasks, many=True)
        context = {
            'tasks': serializer.data
        }
        return render(request, 'admin_task_review.html', context)

    def post(self, request, *args, **kwargs):
        task_id = request.data.get('task_id')
        action = request.data.get('action') 

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'success':
            task.completed = 'S' 
        elif action == 'failure':
            task.completed = 'F'
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        task.save()
        return Response({"message": "Task status updated successfully."})

def custom_404(request, exception):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')



