from django.urls import path
from . import views

app_name='voters'
urlpatterns = [
    path('',views.sign_in,name='sign_in'),    
    path('sign-in',views.sign_in,name='sign_in'),
    path('sign-up',views.sign_up,name='sign_up'),
    path('sign-up-otp/<int:id>',views.sign_up_otp,name='sign_up_otp'),    
    path('signup-check-email',views.signup_check_email,name='signup_check_email'),
    path('signup-check-mobile',views.signup_check_mobile,name='signup_check_mobile'),
    path('signup-check-aadhaar',views.signup_check_aadhaar,name='signup_check_aadhaar'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('edit-profile', views.edit_profile, name='edit_profile'), 
    path('edit-profile-pic', views.edit_profile_pic, name='edit_profile_pic'),
    path('edit-profile-password', views.edit_profile_password, name='edit_profile_password'),
    path('list-elections', views.list_elections, name='list_elections'),
    path('before-elections/<int:id>', views.before_elections, name='before_elections'),
    path('before-elections-otp/<int:id>/<str:aadhaar_id>', views.before_elections_otp, name='before_elections_otp'),    
    path('view-elections/<int:id>/<str:aadhaar_id>', views.view_elections, name='view_elections'),
    path('view-elections-completed/<int:id>/<str:aadhaar_id>', views.view_elections_completed, name='view_elections_completed'),       
    path('logout', views.logout, name='logout'),   
]
