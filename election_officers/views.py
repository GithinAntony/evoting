from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Avg, Count
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings
from .models import *
from elections.models import user_registration, elections, election_candidates, messages_index, messages_contain
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

def sign_in(request):
    if request.method == 'POST':
            data_record = request.POST
            if user_registration.objects.filter(mobile_number=data_record['mobile_number'],password=encrypt_AES256(data_record['password']),user_type='election_officers',otp_status='yes'):
                user_details = user_registration.objects.get(mobile_number=data_record['mobile_number'],password=encrypt_AES256(data_record['password']),user_type='election_officers',otp_status='yes')
                if user_details.status == 'active':
                    request.session['is_logged_in'] = True
                    request.session['user_type'] = 'election_officers'                    
                    request.session['user_id'] = user_details.unique_id   
                    request.session['first_name'] = user_details.first_name
                    request.session['last_name'] = user_details.last_name                                     
                    request.session['email_address'] = user_details.email_address
                    request.session['mobile_number'] = user_details.mobile_number
                    request.session['aadhaar_number'] = user_details.aadhaar_number
                    return redirect(reverse('election_officers:dashboard'))
                else:
                    messages.error(request, 'User is suspended. Contact the admin!')
                    return redirect(reverse('election_officers:sign_in'))
            else:
                messages.error(request, 'Invalid credentials!')
                return redirect(reverse('election_officers:sign_in'))
    return render(request, 'election_officers/login.html')

def sign_up(request):
    if request.method == 'POST':
        data_record = request.POST
        # if condition to check and remove leftover registrations
        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='election_officers',otp_status='no').count() > 0:
            user_registration.objects.filter(email_address=data_record['email_address'],user_type='election_officers',otp_status='no').delete()
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers',otp_status='no').count() > 0:
            user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers',otp_status='no').delete()
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers',otp_status='no').count() > 0:
            user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers',otp_status='no').delete()

         # continue with registrations           
        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='election_officers'):
            messages.error(request, 'Email already exists! Please try again!')
            return redirect(reverse('election_officers:sign_up'))
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers'):
            messages.error(request, 'Mobile number already exists! Please try again!')
            return redirect(reverse('election_officers:sign_up'))
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers'):
            messages.error(request, 'Aadhaar number already exists! Please try again!')
            return redirect(reverse('election_officers:sign_up'))        
        else:
            profile_photo = request.FILES['profile_photo']
            folder = 'election_officers' # subfolder name
            fs = FileSystemStorage(location=f'media/{folder}')
            file_name = fs.save(profile_photo.name, profile_photo)
            signup = user_registration(
                user_type = 'election_officers',
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
            messages.success(request, 'Election officers registration added! Complete otp validation..')
            return redirect(reverse('election_officers:sign_up_otp', kwargs={'id': last_insert_id}))
    context = {}
    return render(request, 'election_officers/registration.html', context)

def sign_up_otp(request, id):
    if request.method == 'POST':
            data_record = request.POST
            print(data_record['otp_number'])
            if data_record['otp_number'] == '123321':
                userdata = user_registration.objects.get(unique_id=id)
                userdata.otp_status = 'yes'
                userdata.save() 
                messages.error(request, 'Election officers have been registered successfully! Please wait for approval from the administrators.')
                return redirect(reverse('election_officers:sign_in'))                  
            else:
                messages.error(request, 'Invalid Otp! Please try again with correct otp')
                return redirect(reverse('election_officers:sign_up_otp'))    
    return render(request, 'election_officers/registration-otp.html')    


def signup_check_email(request):
    flag = 0
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'election_officers':
        flag = True
    else:
        flag = False
    if request.method == 'POST':
        data_record = request.POST
        # Check if the email exists in the database
        if flag:
            temp_value = user_registration.objects.filter(email_address=data_record['email_a'],user_type='election_officers').exclude(email_address=request.session['email_address']).exists()
        else:
            temp_value = user_registration.objects.filter(email_address=data_record['email_a'],user_type='election_officers').exists()   
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
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'election_officers':
        flag = True
    else:
        flag = False    
    if request.method == 'POST':
        data_record = request.POST
        # Check if the phone number exists in the database
        if flag:
            temp_value = user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers').exclude(mobile_number=request.session['mobile_number']).exists()
        else:
            temp_value = user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers').exists()   
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
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'election_officers':
        flag = True
    else:
        flag = False    
    if request.method == 'POST':
        data_record = request.POST
        # Check if the phone number exists in the database
        if flag:
            temp_value = user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers').exclude(aadhaar_number=request.session['aadhaar_number']).exists()
        else:
            temp_value = user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers').exists()   
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
    return redirect(reverse('election_officers:sign_in'))

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
    elections_data = elections.objects.filter(election_officers_id=request.session['user_id']).order_by('date_added').all()
    elections_data_results = elections.objects.filter(election_officers_id=request.session['user_id'],status='published').order_by('date_added').all()
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
        'random_number_3':random.randint(7, 20),
        'elections_data_results':elections_data_results,
    }    
    return render(request, 'election_officers/dashboard.html', context)   

def edit_profile(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    if request.method == 'POST':
        data_record = request.POST
        # update the user object with the new data from the form
        if user_registration.objects.filter(email_address=data_record['email_address'],user_type='election_officers').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Email already exists! Please try again!')
            return redirect(reverse('election_officers:edit_profile'))
        elif user_registration.objects.filter(mobile_number=data_record['mobile_number'],user_type='election_officers').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Mobile number already exists! Please try again!')
            return redirect(reverse('election_officers:edit_profile'))
        elif user_registration.objects.filter(aadhaar_number=data_record['aadhaar_number'],user_type='election_officers').exclude(unique_id=request.session['user_id']):
            messages.error(request, 'Aadhaar number already exists! Please try again!')
            return redirect(reverse('election_officers:edit_profile'))        
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
            return redirect(reverse('election_officers:edit_profile')) # redirect to the user detail pagee    
    context = { 'userdata': userdata }
    return render(request, 'election_officers/edit-profile.html', context)

def edit_profile_pic(request):
    userdata = user_registration.objects.get(unique_id=request.session['user_id'])
    if request.method == 'POST':
        uploaded_file = request.FILES['profile_photo']
        folder = 'election_officers' # subfolder name
        fs = FileSystemStorage(location=f'media/{folder}')
        file_name = fs.save(uploaded_file.name, uploaded_file)
        userdata.profile_photo = f'{folder}/{file_name}'
        userdata.save()
        messages.success(request, 'Profile picture changed successfully!')
    return redirect(reverse('election_officers:edit_profile'))

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
        return redirect(reverse('election_officers:edit_profile'))
    
def list_candidates(request):
    context = { 'list_userdata': user_registration.objects.filter(user_type='candidates') }
    return render(request, 'election_officers/list-candidates.html', context)

def list_voters(request):
    context = { 'list_userdata': user_registration.objects.filter(user_type='voters') }
    return render(request, 'election_officers/list-voters.html', context)    

def view_candidates(request, id):
    context = { 'userdata': user_registration.objects.get(unique_id=id) }
    return render(request, 'election_officers/view-candidates.html', context)

def view_voters(request, id):
    userdata = user_registration.objects.get(unique_id=id)
    userdata_images = 0
    context = { 'userdata': userdata, 'userdata_images': userdata_images }
    return render(request, 'election_officers/view-voters.html', context)   

def change_user_status(request, id):
    userdata = user_registration.objects.get(unique_id=id)
    current_status  = userdata.status
    usertype = userdata.user_type
    status_t = 'active'
    if current_status == 'active':
        status_t = 'pending' 
    userdata.status = status_t  
    userdata.save() # save the updated user object
    messages.success(request, 'Status updated successfully!')     
    if usertype == 'voters':
        return redirect(reverse('election_officers:view_voters', kwargs={'id': id}))    
    else:            
        return redirect(reverse('election_officers:view_candidates', kwargs={'id': id}))


