from django.contrib import admin
from .models import App,Task  # Import your App model

# Register the App model with the admin site
admin.site.register(App)
admin.site.register(Task)
