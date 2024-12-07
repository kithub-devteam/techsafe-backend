from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/activities/', include('activities.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/forum/', include('forum.urls')),
    path('api/menus/', include('menus.urls')),
    path('api/partners/', include('partners.urls')),
    path('api/chatbot/', include('techsafechatbot.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/auth/', include('authentication.urls')),
]