from django.urls import path
from . import views

app_name='elections'
urlpatterns = [
    path('messages-list',views.messages_list,name='messages_list'),
    path('messages-view/<int:id>/<int:init_id>/<str:page_type>',views.messages_view,name='messages_view'), 
    path('message-campaign', views.message_campaign, name='message_campaign'),
    path('list-elections', views.list_elections, name='list_elections'),
    path('add-elections', views.add_elections, name='add_elections'),
    path('delete-election/<int:id>', views.delete_election, name='delete_election'),    
    path('edit-elections/<int:id>', views.edit_elections, name='edit_elections'),  
    path('list-election-candidates/<int:id>',views.list_election_candidates, name='list_election_candidates'), 
    path('view-election-candidates/<int:id>/<int:id_2>',views.view_election_candidates, name='view_election_candidates'),   
    path('add-election-candidates/<int:id>/<int:id_2>',views.add_election_candidates, name='add_election_candidates'),
    path('election-parties/<int:id>', views.election_parties_v, name='election_parties'),  
    path('election-position/<int:id>', views.election_position_v, name='election_position'),
    path('election-parties-delete/<int:id>/<int:edit_id>', views.election_parties_delete, name='election_parties_delete'),  
    path('election-position-delete/<int:id>/<int:edit_id> ', views.election_position_delete, name='election_position_delete'),               
    path('delete-election-candidates/<int:id>/<int:id_2>',views.delete_election_candidates, name='delete_election_candidates'),            
]
