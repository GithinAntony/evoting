from django.urls import path
from . import views

app_name='election_officers'
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
    path('list-candidates', views.list_candidates, name='list_candidates'), 
    path('list-voters', views.list_voters, name='list_voters'), 
    path('view-candidates/<int:id>', views.view_candidates, name='view_candidates'),
    path('view-voters/<int:id>', views.view_voters, name='view_voters'),
    path('change-user-status/<int:id>', views.change_user_status, name='change_user_status'),
    path('logout', views.logout, name='logout'),   
]
