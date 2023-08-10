from django.urls import path
from . import views

app_name='candidates'
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
    path('list-voters', views.list_voters, name='list_voters'),
    path('view-voters/<int:id>', views.view_voters, name='view_voters'),        
    path('list-elections', views.list_elections, name='list_elections'),
    path('view-elections/<int:id>', views.view_elections, name='view_elections'),
    path('delete-elections/<int:id>/<int:id2>', views.delete_elections, name='delete_elections'),    
    path('apply-election-party/<int:id>/<int:party_id>',views.apply_election_party, name='apply_election_party'), 
    path('apply-election-position/<int:id>/<int:position_id>',views.apply_election_position, name='apply_election_position'),         
    path('edit-elections/<int:id>', views.edit_elections, name='edit_elections'),
    path('logout', views.logout, name='logout'),   
]
