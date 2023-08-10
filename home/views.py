from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import *
from elections.models import user_registration, elections, election_candidates, election_position, election_votes
from django.db.models.functions import Concat
from django.db.models import Sum
from operator import itemgetter
from django.conf import settings



# Create your views here.
def home(request):
    _election_candidates = election_candidates.objects.filter(status='accepted').order_by('-date_added')[:10]
    context = { 'election_candidates': _election_candidates }
    return render(request, 'home/index.html',context)

def about_us(request):
    return render(request, 'home/about.html')

def contact_us(request):
    if request.method == 'POST':
        data_record = request.POST         
        data_add = Contact(
            full_name=data_record['full_name'],
            email_address=data_record['email_address'],
            message=data_record['message'],
        )            
        data_add.save()
        messages.success(request, 'Your message has been successfully submitted. We will get back to you as soon as possible.')
        return redirect(reverse('home:contact_us'))    
    return render(request, 'home/contact.html')

def list_elections(request):
    context = { 'list_electiondata': elections.objects.filter(status='ready') }
    return render(request, 'home/list-elections.html', context)

def view_elections(request):
    flag = 0
    if 'is_logged_in' in request.session and 'user_type' in request.session and request.session['user_type'] == 'voters':
        messages.success(request, 'You must be logged in as a voter to view and vote!')
        return redirect(reverse('voters:list_elections'))
    else:
        messages.success(request, 'You must be logged in as a voter to view and vote!')
        return redirect(reverse('home:list_elections'))

def list_results(request):
    context = { 'list_electiondata': elections.objects.filter(status='published') }
    return render(request, 'home/list-results.html', context)

def view_results(request, id): 
    election_t = elections.objects.get(unique_id=id)
    election_candidates_t = election_candidates.objects.filter(elections_id=id)
    election_position_t = election_position.objects.filter(elections_id=id)
    candidate_votes = election_votes.objects.values('position','candidates','candidates__candidates__profile_photo','candidates__candidates__first_name','candidates__candidates__last_name','candidates__party__party_name','candidates__party__party_image', 'candidates__position__postion_name', 'candidates__symbol', 'candidates__symbol_name').annotate(total_votes=Sum('vote')).filter(elections_id=id).all()
    if election_position_t.count() > 0:
        results = {}
        for row1 in election_position_t: 
            for row in candidate_votes:
                if row1.unique_id == row['position']:
                    if row['position'] not in results:
                        results[row['position']] = []                    
                    results[row['position']].append({ 'candidates': { 'candidate_id': row['candidates'], 'profile_photo': settings.MEDIA_URL + row['candidates__candidates__profile_photo'], 'first_name': row['candidates__candidates__first_name'], 'last_name': row['candidates__candidates__last_name'], 'party_image': settings.MEDIA_URL + row['candidates__party__party_image'], 'party_name': row['candidates__party__party_name'], 'position_name': row['candidates__position__postion_name'], 'symbol': settings.MEDIA_URL + row['candidates__symbol'], 'symbol_name': row['candidates__symbol_name'] } , 'total_votes': row['total_votes'] })

    for key, value in results.items():
        value.sort(key=itemgetter('total_votes'), reverse=True) 
    context = { 'election': election_t, 'results': results , 'userdata_position':election_position_t }
    return render(request, 'home/view-results.html', context)