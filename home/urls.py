from django.urls import path
from . import views

app_name='home'
urlpatterns = [
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('about-us',views.about_us,name='about_us'),
    path('contact-us',views.contact_us,name='contact_us'),
    path('list-elections',views.list_elections,name='list_elections'),
    path('view-elections',views.view_elections,name='view_elections'),    
    path('list-results',views.list_results,name='list_results'),
    path('view-results/<int:id>',views.view_results,name='view_results'),         
]
