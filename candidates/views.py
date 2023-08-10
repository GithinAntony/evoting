import base64, random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import *
from elections.models import user_registration, elections, election_candidates, election_votes, messages_contain
from django.db.models import Avg, Count
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

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

def sign_in(request):
    if request.method == 'POST':
            data_record = request.POST
            if user_registration.objects.filter(mobile_number=data_record['mobile_number'],password=encrypt_AES256(data_record['password']),user_type='candidates',otp_status='yes'):
                user_details = user_registration.objects.get(mobile_number=data_record['mobile_number'],password=encrypt_AES256(data_record['password']),user_type='candidates',otp_status='yes')
                if user_details.status == 'active':
                    request.session['is_logged_in'] = True
                    request.session['user_type'] = 'candidates'                    
                    request.session['user_id'] = user_details.unique_id   
                    request.session['first_name'] = user_details.first_name
                    request.session['last_name'] = user_details.last_name                                     
                    request.session['email_address'] = user_details.email_address
                    request.session['mobile_number'] = user_details.mobile_number
                    request.session['aadhaar_number'] = user_details.aadhaar_number
                    return redirect(reverse('candidates:dashboard'))
                else:
                    messages.error(request, 'User is suspended. Contact the admin!')
                    return redirect(reverse('candidates:sign_in'))
            else:
                messages.error(request, 'Invalid credentials!')
                return redirect(reverse('candidates:sign_in'))
    return render(request, 'candidates/login.html')

def sign_up(request):
    if request.method == 'POST':
        data_record = request.POST

        # if condition to check and remove leftover registrations
        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='candidates',otp_status='no').count() > 0:
            user_registration.objects.filter(email_address=data_record['email_address'],user_type='candidates',otp_status='no').delete()
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates',otp_status='no').count() > 0:
            user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates',otp_status='no').delete()
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates',otp_status='no').count() > 0:
            user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates',otp_status='no').delete()

        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='candidates',otp_status='yes'):
            messages.error(request, 'Email already exists! Please try again!')
            return redirect(reverse('candidates:sign_up'))
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates',otp_status='yes'):
            messages.error(request, 'Mobile number already exists! Please try again!')
            return redirect(reverse('candidates:sign_up'))
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates',otp_status='yes'):
            messages.error(request, 'Aadhaar number already exists! Please try again!')
            return redirect(reverse('candidates:sign_up'))        
        else:
            profile_photo = request.FILES['profile_photo']
            folder = 'candidates' # subfolder name
            fs = FileSystemStorage(location=f'media/{folder}')
            file_name = fs.save(profile_photo.name, profile_photo)
            signup = user_registration(
                user_type = 'candidates',
                first_name = data_record['first_name'],
                last_name = data_record['last_name'],
                mobile_number = data_record['mobile_number'],
                email_address = data_record['email_address'],
                password = encrypt_AES256(data_record['password']),
                address_line_1 = data_record['address_line_1'],
                address_line_2 = data_record['address_line_2'],
                district = data_record['district'],
                state = data_record['state'],
                pin_code = data_record['pin_code'],
                aadhaar_number = data_record['aadhaar_number'],                
                profile_photo = f'{folder}/{file_name}',
                status='pending',
            )            
            signup.save()
            last_insert_id = signup.unique_id            
            messages.success(request, 'candidates registration added! Complete otp validation..')
            return redirect(reverse('candidates:sign_up_otp', kwargs={'id': last_insert_id}))
    context = {}
    return render(request, 'candidates/registration.html', context)

def sign_up_otp(request, id):
    if request.method == 'POST':
            data_record = request.POST
            print(data_record['otp_number'])
            if data_record['otp_number'] == '123321':
                userdata = user_registration.objects.get(unique_id=id)
                userdata.otp_status = 'yes'
                userdata.save() 
                messages.error(request, 'Candidates registered successfully! Sign in here.')
                return redirect(reverse('candidates:sign_in'))                  
            else:
                messages.error(request, 'Invalid Otp! Please try again with correct otp')
                return redirect(reverse('candidates:sign_up_otp'))    
    return render(request, 'candidates/registration-otp.html')    

def signup_check_email(request):
    flag = 0
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'candidates':
        flag = True
    else:
        flag = False
    if request.method == 'POST':
        data_record = request.POST
        # Check if the email exists in the database
        if flag:
            temp_value = user_registration.objects.filter(email_address=data_record['email_a'],user_type='candidates',otp_status='yes').exclude(email_address=request.session['email_address']).exists()
        else:
            temp_value = user_registration.objects.filter(email_address=data_record['email_a'],user_type='candidates',otp_status='yes').exists()   
        if temp_value:
            response_data = {'exists': True}
        else:
            response_data = {'exists': False}
        # Return the result as a JSON response
    else:
        response_data = {'exists': True}    
    return JsonResponse(response_data)

def signup_check_mobile(request):
    flag = 0
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'candidates':
        flag = True
    else:
        flag = False    
    if request.method == 'POST':
        data_record = request.POST
        # Check if the phone number exists in the database
        if flag:
            temp_value = user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates',otp_status='yes').exclude(mobile_number=request.session['mobile_number']).exists()
        else:
            temp_value = user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates',otp_status='yes').exists()   
        if temp_value:        
            response_data = {'exists': True}
        else:
            response_data = {'exists': False}
        # Return the result as a JSON response
    else:
        response_data = {'exists': True}    
    return JsonResponse(response_data)

def signup_check_aadhaar(request):
    flag = 0
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'candidates':
        flag = True
    else:
        flag = False    
    if request.method == 'POST':
        data_record = request.POST
        # Check if the phone number exists in the database
        if flag:
            temp_value = user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates',otp_status='yes').exclude(aadhaar_number=request.session['aadhaar_number']).exists()
        else:
            temp_value = user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates',otp_status='yes').exists()   
        if temp_value:
            response_data = {'exists': True}
        else:
            response_data = {'exists': False}
        # Return the result as a JSON response
    else:
        response_data = {'exists': True}    
    return JsonResponse(response_data)

def logout(request):
    del request.session['is_logged_in']
    del request.session['first_name']
    del request.session['last_name']
    del request.session['email_address']
    del request.session['user_id']
    del request.session['mobile_number']
    del request.session['user_type']
    del request.session['aadhaar_number']
    return redirect(reverse('candidates:sign_in'))

def dashboard(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    input_str = request.session['user_type']
    output_str = input_str.replace('_', ' ').title()
    # Fetch user registration data
    voters = user_registration.objects.filter(user_type='voters').order_by('date_added').all()
    candidates = user_registration.objects.filter(user_type='candidates').order_by('date_added').all()
    election_officers = user_registration.objects.filter(user_type='election_officers').order_by('date_added').all()

    # Fetch messages data
    messages = messages_contain.objects.all()
    # Fetch election data
    elections_data = elections.objects.order_by('date_added').all()
    # Fetch election candidates data
    election_candidates_data = election_candidates.objects.all()

    graphs_total_user = user_registration.objects.filter().count()    
    p_graphs_total_user = (graphs_total_user/70) * 100


    context = {
        'voters': voters,
        'candidates': candidates,
        'election_officers': election_officers,
        'messages': messages,
        'elections_data': elections_data,
        'election_candidates_data': election_candidates_data,
        'userdata': userdata, 
        'user_type_t':output_str,
        'graphs_total_user':graphs_total_user,
        'p_graphs_total_user': round(p_graphs_total_user),
        'random_number':random.randint(1, 7),
        'random_number_2':random.randint(10, 29),
        'random_number_3':random.randint(7, 20)    
    }    
    return render(request, 'candidates/dashboard.html', context)      

def edit_profile(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    if request.method == 'POST':
        data_record = request.POST
        # update the user object with the new data from the form
        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='candidates').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Email already exists! Please try again!')
            return redirect(reverse('candidates:edit_profile'))
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='candidates').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Mobile number already exists! Please try again!')
            return redirect(reverse('candidates:edit_profile'))
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='candidates').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Aadhaar number already exists! Please try again!')
            return redirect(reverse('candidates:edit_profile'))        
        else:
            userdata.first_name = data_record['first_name']
            userdata.last_name = data_record['last_name']
            userdata.mobile_number = data_record['mobile_number']
            userdata.email_address = data_record['email_address']
            userdata.address_line_1 = data_record['address_line_1']
            userdata.address_line_2 = data_record['address_line_2']
            userdata.district = data_record['district']
            userdata.state = data_record['state']
            userdata.pin_code = data_record['pin_code']
            userdata.aadhaar_number = data_record['aadhaar_number']
            userdata.save() # save the updated user object
            messages.success(request, 'Profile updated successfully!')
            return redirect(reverse('candidates:edit_profile')) # redirect to the user detail pagee    
    context = { 'userdata': userdata }
    return render(request, 'candidates/edit-profile.html', context)

def edit_profile_pic(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    if request.method == 'POST':
        uploaded_file = request.FILES['profile_photo']
        folder = 'candidates' # subfolder name
        fs = FileSystemStorage(location=f'media/{folder}')
        file_name = fs.save(uploaded_file.name, uploaded_file)
        userdata.profile_photo = f'{folder}/{file_name}'
        userdata.save()
        messages.success(request, 'Profile picture changed successfully!')
    return redirect(reverse('candidates:edit_profile'))

def edit_profile_password(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    if request.method == 'POST':
        data_record = request.POST
        if userdata.password == data_record['old_password']:
            userdata.password = data_record['password']
            userdata.save()
            messages.success(request, 'Password updated successfully!')
        else:
            messages.error(request, 'Please enter correct previous password!') 
        return redirect(reverse('candidates:edit_profile'))

def list_voters(request):
    context = { 'list_userdata': user_registration.objects.filter(user_type='voters') }
    return render(request, 'candidates/list-voters.html', context)    

def view_voters(request, id):
    userdata = user_registration.objects.get(unique_id=id)
    userdata_images = 0
    context = { 'userdata': userdata, 'userdata_images': userdata_images }
    return render(request, 'candidates/view-voters.html', context)           
    
def list_elections(request):
    list_electiondata = elections.objects.filter(status="active")
    context = {'list_electiondata': list_electiondata}
    return render(request, 'candidates/list-elections.html', context)

def view_elections(request, id):
    election_details = elections.objects.get(unique_id=id)
    candidates_election = election_candidates.objects.filter(elections_id=id,candidates_id=request.session['user_id']).first() 
    if request.method == 'POST':
        data_record = request.POST
        if candidates_election is not None and candidates_election.count() > 0:
            messages.error(request, 'You already applied!') 
            return redirect(reverse('candidates:view_elections', kwargs={'id': id}))
        else:
            election_symbol = request.FILES['election_symbol']
            election_manifestos = request.FILES['election_manifestos']
            folder_1 = 'candidates/symbols' # subfolder name
            folder_2 = 'candidates/manifestos'
            fs1 = FileSystemStorage(location=f'media/{folder_1}')
            fs2 = FileSystemStorage(location=f'media/{folder_2}')        
            file_name_1 = fs1.save(election_symbol.name, election_symbol)
            file_name_2 = fs2.save(election_manifestos.name, election_manifestos)
            data_save = election_candidates(
                elections_id = id,
                candidates_id = request.session['user_id'],
                party_id = data_record['party'],
                position_id = data_record['position'],
                symbol = f'{folder_1}/{file_name_1}',
                symbol_name = data_record['symbol_name'],
                about_us = data_record['about_us'],
                tag_line = data_record['tag_line'],
                manifestos = f'{folder_2}/{file_name_2}',
                status='applied'
            )            
            data_save.save()            
            messages.error(request, 'You have applied successfully!') 
            return redirect(reverse('candidates:view_elections', kwargs={'id': id}))            
    context = { 'election': election_details, 'candidates_election':candidates_election }
    return render(request, 'candidates/view-elections.html', context)

def edit_elections(request, id):
    election_details = elections.objects.get(unique_id=id)
    candidates_election = election_candidates.objects.filter(elections_id=id,candidates_id=request.session['user_id']).first()    
    if request.method == 'POST':
        data_record = request.POST
        uploaded_file = request.FILES['symbol_image']
        folder = 'candidates' # subfolder name
        fs = FileSystemStorage(location=f'media/{folder}')
        file_name = fs.save(uploaded_file.name, uploaded_file)
        candidates_election.symbol = f'{folder}/{file_name}'
        candidates_election.about_us=data_record['about_us']
        candidates_election.tag_line=data_record['tag_line']
        candidates_election.manifestos=data_record['manifestos']
        candidates_election.save()
        messages.success(request, 'Candidate Profile updated successfully!')
        return redirect(reverse('candidates:view_elections', kwargs={'id': id}))    
    context = { 'election_details': election_details, 'candidates_election': candidates_election }
    return render(request, 'candidates/edit-elections.html', context)    

def delete_elections(request, id, id2):
    userdata = get_object_or_404(election_candidates, unique_id=id2)
    userdata.delete()
    messages.success(request, 'Candidancy deleted!')
    return redirect(reverse('candidates:view_elections', kwargs={'id': id}))      

def apply_election_party(request, id, party_id):

    messages.success(request, 'You have applied for the party!')
    return redirect(reverse('candidates:view_elections', kwargs={'id': id}))

def apply_election_position(request, id, position_id):
    messages.success(request, 'You have applied for the position!')
    return redirect(reverse('candidates:view_elections', kwargs={'id': id}))
