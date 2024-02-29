from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact',views.contact,name='contact'),
    path('team',views.team,name='team'),
    path('brands',views.brands,name='brands'),
    path('about',views.about,name='about')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)