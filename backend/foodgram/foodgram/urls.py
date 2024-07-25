from django.contrib import admin
from django.urls import include, path
from api.views import RecipesViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('<slug:slug>', RecipesViewSet),
]
