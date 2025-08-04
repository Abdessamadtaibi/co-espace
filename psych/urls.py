from django.urls import path, include
from django.contrib import admin
from psychapp.accounts.views import activate_user_template_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('psychapp.urls')),
    path('activate/<uid>/<token>/', activate_user_template_view, name='activate'),
]