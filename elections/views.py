from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import *
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings
import base64, random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Define the AES256 encryption and decryption functions
def encrypt_AES256(plaintext):
    key = settings.SECRET_KEY
    iv = b'1234567890123456' # Initialization vector
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

def decrypt_AES256(ciphertext):
    key = settings.SECRET_KEY
    iv = b'1234567890123456' # Initialization vector
    ciphertext = base64.b64decode(ciphertext.encode())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

def messages_list(request):
    user_messages_list = messages_index.objects.filter(sender_user_id=request.session['user_id']).all()
    user_messages_list_2 = messages_index.objects.filter(recipient_user_id=request.session['user_id']).all()
    user_messages_list_array = []
    if user_messages_list.count() > 0:
        for row in user_messages_list:
            user_messages_list_array.append({ 'messages_index': row, 'msg_type':'sender' }) 

    if user_messages_list_2.count() > 0:
        for row in user_messages_list_2:
            user_messages_list_array.append({ 'messages_index': row, 'msg_type':'recipient' }) 

    context = { 'user_messages_list_array':user_messages_list_array }
    return render(request, 'elections/list-message.html', context)     

def messages_view(request, id, init_id, page_type):
    if page_type == 'list':

        try:
            msg_index_data = messages_index.objects.get(unique_id=id)
        except messages_index.DoesNotExist:
            msg_index_data = None

        if msg_index_data is not None:         
            msg_contain = messages_contain.objects.filter(msg_index=msg_index_data)
            if msg_index_data.sender_user_id == request.session['user_id']:
                userdata = user_registration.objects.get(unique_id=msg_index_data.recipient_user_id)  
            else:
                userdata = user_registration.objects.get(unique_id=msg_index_data.sender_user_id)        
        else:
                msg_contain = ''
                userdata = ''
    else:
        
        userdata = user_registration.objects.get(unique_id=init_id)    
        try:
            msg_index_data = messages_index.objects.get(recipient_user_id=init_id, sender_user_id=request.session['user_id'])
        except messages_index.DoesNotExist:
            msg_index_data = None

        if msg_index_data is not None:         
            msg_contain = messages_contain.objects.filter(msg_index=msg_index_data)
        else:
            msg_contain = ''       

    if request.method == 'POST':
        data_record = request.POST

        if msg_index_data is not None:           
            messages_data =  messages_contain(
            msg_index = msg_index_data,
            participant_user_id = request.session['user_id'],
            messages_text = data_record['message'],
            )              
            messages_data.save()
        else: 
            messages_list_data = messages_index(
            recipient_user_id = init_id,
            sender_user_id = request.session['user_id'],
            )
            messages_list_data.save()
            latest_msg_index = messages_index.objects.latest('unique_id')

            messages_data =  messages_contain(
            msg_index = latest_msg_index,
            participant_user_id = request.session['user_id'],
            messages_text = data_record['message'],
            )              
            messages_data.save()
        return redirect(reverse('elections:messages_view', kwargs={'id': id, 'init_id':init_id, 'page_type':page_type, }))

    context = { 'userdata': userdata, 'user_messages':msg_contain }
    return render(request, 'elections/view-message.html', context)         

def message_campaign(request):
    if request.method == 'POST':
        data_record = request.POST
        list_voters = user_registration.objects.filter(user_type='voters').all()
        if list_voters.count() > 0:
            for row in list_voters:
                sender_id = row.unique_id  

                try:
                    msg_index_data = messages_index.objects.get(recipient_user_id=sender_id, sender_user_id=request.session['user_id'])
                except messages_index.DoesNotExist:
                    msg_index_data = None                    

                if msg_index_data is not None:           
                    messages_data =  messages_contain(
                    msg_index = msg_index_data,
                    participant_user_id = request.session['user_id'],
                    messages_text = data_record['message'],
                    message_type = 'campaign',
                    )              
                    messages_data.save()
                else: 
                    messages_list_data = messages_index(
                    recipient_user_id = sender_id,
                    sender_user_id = request.session['user_id'],
                    )
                    messages_list_data.save()
                    latest_msg_index = messages_index.objects.latest('unique_id')

                    messages_data =  messages_contain(
                    msg_index = latest_msg_index,
                    participant_user_id = request.session['user_id'],
                    messages_text = data_record['message'],
                    message_type = 'campaign',
                    )              
                    messages_data.save()    
    context = { 'userdata': user_registration.objects.get(unique_id=request.session['user_id']) }
    return render(request, 'elections/message-campaign.html', context)

def list_elections(request):
    context = { 'list_electiondata': elections.objects.filter(election_officers_id=request.session['user_id']) }
    return render(request, 'elections/list-elections.html', context) 

def add_elections(request):
    if request.method == 'POST':
        data_record = request.POST
        logo_image_t = request.FILES['logo_image']
        folder = 'elections' # subfolder name
        fs = FileSystemStorage(location=f'media/{folder}')
        file_name = fs.save(logo_image_t.name, logo_image_t)
        signup = elections(
            election_officers=user_registration.objects.get(unique_id=request.session['user_id']),
            title=data_record['title'],
            description=data_record['description'],
            logo_image=f'{folder}/{file_name}',
            election_start_date_time=data_record['start_date'],
            election_end_date_time=data_record['end_date'],
            #status=data_record['status'],
            status='pending',
        )            
        signup.save()
        last_insert_id = signup.unique_id
        messages.success(request, 'Successfully added the election! Please proceed to provide further details.')
        return redirect(reverse('elections:edit_elections', kwargs={'id': last_insert_id}))         
    context = {}
    return render(request, 'elections/add-elections.html', context)

def edit_elections(request, id):
    userdata = elections.objects.get(unique_id=id)
    userdata_party = election_parties.objects.filter(elections=userdata)
    userdata_position = election_position.objects.filter(elections=userdata)
    userdata_candidates = election_candidates.objects.filter(elections=userdata,status='accepted')
    userdata_voting = election_votes.objects.filter(elections=userdata)
    if request.method == 'POST':
        data_record = request.POST
#   Status working here
        status = 'pending'
        if data_record['status']=="active":
                status = 'active'
                if userdata_party.count() == 0:
                    status = 'pending'
                    messages.info(request, 'Please add atleast a party to mark this election active')
                elif userdata_position.count() == 0:
                    status = 'pending'
                    messages.info(request, 'Please add atleast a position to mark this election active')                
        elif data_record['status']=="ready":
                status = 'ready'
                if userdata_party.count() == 0:
                    status = 'pending'
                    messages.info(request, 'Please add atleast a party to mark this election completed and ready for voting')
                elif userdata_position.count() == 0:
                    status = 'pending'
                    messages.info(request, 'Please add atleast a position to mark this election completed and ready for voting')            
                elif userdata_candidates.count() == 0:
                    status = 'active' 
                    messages.info(request, 'To mark this election ready for voting, Please ensure that at least one candidate has been added and their status has been accepted by the election officials.')  
        elif data_record['status']=="completed":
                status = 'completed'
                if userdata.status == 'published':
                    messages.info(request, 'If you change the status back to "completed," the election results will not be published anymore!')
                    status = 'completed'  
                elif userdata.status == 'ready':
                    messages.info(request, 'This marks the election completed nad public wont be able to vote anymore!')
                    status = 'completed'
                else:
                    status = userdata.status
        elif data_record['status']=="published":
            status = "published"
            if userdata_party.count() == 0:
                    status = 'pending'
                    messages.info(request, 'Please add atleast a party to mark this published and ready for results')
            elif userdata_position.count() == 0:
                    status = 'pending'  
                    messages.info(request, 'Please add atleast a position to mark this published completed and ready for results')
            if userdata_candidates.count() == 0:
                    status = 'active' 
                    messages.info(request, 'Please add atleast a candidate to mark this published completed and ready for results')                      
            elif userdata_voting.count() == 0:
                    status = 'active'
                    messages.info(request, 'In order to publish the results of the election, at least one vote must be cast. As of now, since no one has voted yet, the election cannot be completed and the results cannot be published.')                
        else:
            status = 'pending'    

        userdata.election_officers = user_registration.objects.get(unique_id=request.session['user_id'])
        userdata.title = data_record['title']
        userdata.description = data_record['description']
        userdata.election_start_date_time = data_record['start_date']
        userdata.election_end_date_time = data_record['end_date']
        userdata.status = status
        userdata.save() 
        messages.success(request, 'Elections updated successfully!')
        return redirect(reverse('elections:edit_elections', kwargs={'id': id})) # redirect to the user detail pagee    
    context = { 'userdata': userdata, 'list_party': userdata_party, 'list_position': userdata_position, 'edit_id':id }
    return render(request, 'elections/edit-elections.html', context)

def election_parties_v(request, id):
    userdata = elections.objects.get(unique_id=id)
    if request.method == 'POST':
        data_record = request.POST
        logo_image_t = request.FILES['party_image']
        folder = 'election_party' # subfolder name
        fs = FileSystemStorage(location=f'media/{folder}')
        file_name = fs.save(logo_image_t.name, logo_image_t)     
        data_add = election_parties(
            elections=userdata,
            party_name=data_record['party_name'],
            party_image=f'{folder}/{file_name}',
            tag_line=data_record['tag_line'],
        )            
        data_add.save()
        messages.success(request, 'Election party added successfully!')
    return redirect(reverse('elections:edit_elections', kwargs={'id': id}))

def election_position_v(request, id):
    userdata = elections.objects.get(unique_id=id)
    if request.method == 'POST':
        data_record = request.POST         
        data_add = election_position(
            elections=userdata,
            postion_name=data_record['position_name'],
            tag_line=data_record['tag_line_2'],
        )            
        data_add.save()
        messages.success(request, 'Election position added successfully!')
    return redirect(reverse('elections:edit_elections', kwargs={'id': id}))

def election_parties_delete(request, id, edit_id):
    userdata = get_object_or_404(election_parties, unique_id=id)
    userdata.delete()
    messages.success(request, 'Party deleted successfully!')
    return redirect(reverse('elections:edit_elections', kwargs={'id': edit_id}))

def election_position_delete(request, id, edit_id):
    userdata = get_object_or_404(election_position, unique_id=id)
    userdata.delete()
    messages.success(request, 'Position deleted successfully!')
    return redirect(reverse('elections:edit_elections', kwargs={'id': edit_id}))

def list_election_candidates(request, id):
    userdata = elections.objects.get(unique_id=id)
    userdata_candidates = user_registration.objects.filter(user_type='candidates',status='active')
    userdata_candidates_election = election_candidates.objects.filter(elections_id=id)
    context = { 'userdata': userdata, 'userdata_candidates':userdata_candidates, 'userdata_candidates_election': userdata_candidates_election }
    return render(request, 'elections/list-election-candidates.html', context) 

def view_election_candidates(request, id, id_2):
    userdata = election_candidates.objects.get(unique_id=id_2)
    if request.method == 'POST':
        data_record = request.POST 
        userdata.status = data_record['candidate_status']
        userdata.note_eo = data_record['reason']                
        userdata.save()

        sender_id = userdata.candidates.unique_id 
        msg_type = 'normal'
        if data_record['candidate_status'] == 'accepted':
            msg_type = 'candidates_accepted'
        elif data_record['candidate_status'] == 'rejected':   
            msg_type = 'candidates_rejected'       
        else:
            msg_type = 'normal'          
            
        try:
            msg_index_data = messages_index.objects.get(recipient_user_id=sender_id, sender_user_id=request.session['user_id'])
        except messages_index.DoesNotExist:
            msg_index_data = None                    

        if msg_index_data is not None:           
            messages_data =  messages_contain(
            msg_index = msg_index_data,
            participant_user_id = request.session['user_id'],
            messages_text = data_record['reason'],
            message_type = msg_type,
            )              
            messages_data.save()
        else: 
            messages_list_data = messages_index(
            recipient_user_id = sender_id,
            sender_user_id = request.session['user_id'],
            )
            messages_list_data.save()
            latest_msg_index = messages_index.objects.latest('unique_id')

            messages_data =  messages_contain(
            msg_index = latest_msg_index,
            participant_user_id = request.session['user_id'],
            messages_text = data_record['reason'],
            message_type = msg_type,
            )              
            messages_data.save()

        messages.success(request, 'Candidate status updated successfully!')
        return redirect(reverse('elections:view_election_candidates', kwargs={'id': id, 'id_2':id_2 }))
    context = { 'userdata': userdata, 'id_t':id }
    return render(request, 'elections/view-election-candidates.html', context) 

def add_election_candidates(request, id, id_2):
        userdata = election_candidates(
            elections_id=id,
            candidates_id=id_2
        )            
        userdata.save()
        messages.success(request, 'Candidate added successfully!')
        return redirect(reverse('elections:edit_election_candidates', kwargs={'id': id}))        

def delete_election_candidates(request, id, id_2):
        election_candidates.objects.filter(unique_id=id_2).delete()
        messages.success(request, 'Candidate deleted successfully!')
        return redirect(reverse('elections:edit_election_candidates', kwargs={'id': id}))

def delete_election(request, id):
        userdata = elections.objects.get(unique_id=id)
        election_parties.objects.filter(elections=userdata).delete()
        election_position.objects.filter(elections=userdata).delete()
        election_candidates.objects.filter(elections=userdata).delete()
        election_votes.objects.filter(elections=userdata).delete()
        userdata.delete()         
        messages.success(request, 'Election deleted successfully!')
        return redirect(reverse('elections:list_elections'))        

 
