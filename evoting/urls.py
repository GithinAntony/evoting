from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin2023/', admin.site.urls),
    path('',include('home.urls',namespace='home'),),        
    path('candidates/',include('candidates.urls',namespace='candidates'),),
    path('election-officers/',include('election_officers.urls',namespace='election_officers'),),
    path('voters/',include('voters.urls',namespace='voters'),), 
    path('elections/',include('elections.urls',namespace='elections')),             
] +static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
