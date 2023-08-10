from django.db import models 
from django.utils import timezone
from django.utils.timezone import now

#user registration
class user_registration(models.Model):
    USER_TYPE_CHOICES = [
        ('candidates', 'Candidates'),
        ('election_officers', 'Election Officers'),
        ('voters', 'Voters'),
    ]      
    unique_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.EmailField(max_length=255, unique=True)
    password = models.TextField(blank=False)
    mobile_number = models.PositiveIntegerField(blank=False)
    aadhaar_number = models.TextField(blank=False)
    profile_photo = models.ImageField(upload_to='users/', null=True, blank=True)
    address_line_1 = models.CharField(max_length=500, blank=False)   
    address_line_2 = models.CharField(max_length=500, null=True, blank=True)   
    district = models.CharField(max_length=100, blank=False)
    state = models.CharField(max_length=10, blank=False)    
    pin_code = models.CharField(max_length=8, blank=False)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    STATUS_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    otp_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="no")
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True) 

    class Meta:
        verbose_name = 'User Registration'
        verbose_name_plural = 'User Registrations'      

    def __str__(self):
        return self.email_address
    
class messages_index(models.Model):    
    unique_id=models.AutoField(primary_key=True, null=False) 
    recipient_user=models.ForeignKey(user_registration, on_delete=models.CASCADE, related_name='recipient_images_conn',default=0)
    sender_user=models.ForeignKey(user_registration, on_delete=models.CASCADE, related_name='sender_images_conn',default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = 'Messages Index'
        verbose_name_plural = 'Messages Indexs'     

    def __str__(self):
        return str(self.recipient_user)

class messages_contain(models.Model):   
    unique_id = models.AutoField(primary_key=True, null=False)
    msg_index = models.ForeignKey(messages_index, null=False, on_delete=models.CASCADE, related_name='msg_index_conn')
    participant_user = models.ForeignKey(user_registration, null=True, on_delete=models.SET_NULL)
    messages_text = models.TextField(default='', null=False)
    message_choices = [
        ('normal', 'Normal'),
        ('campaign', 'Campaign'),
        ('candidates_accepted', 'Candidates Accepted'),
        ('candidates_rejected', 'Candidates Rejected'),
    ]
    message_type = models.CharField(max_length=25, choices=message_choices, default="normal")  
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = 'Messages Contain'
        verbose_name_plural = 'Messages Contains'     
       
    def __str__(self):
        return self.messages_text      
    
class elections(models.Model):
    unique_id = models.AutoField(primary_key=True, null=False)
    election_officers=models.ForeignKey(user_registration, on_delete=models.CASCADE, related_name='election_officers_conn')
    title = models.CharField(max_length=500, blank=False)
    description = models.TextField(blank=False)
    logo_image = models.ImageField(upload_to='election_officers/', null=True, blank=True)    
    election_start_date_time = models.DateTimeField(blank=False,default=timezone.now)
    election_end_date_time = models.DateTimeField(blank=False,default=timezone.now)
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('ready','Ready'),
        ('completed','Completed'),
        ('pending', 'Pending'),
        ('active', 'Active'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)   

class election_parties(models.Model):
    unique_id = models.AutoField(primary_key=True, null=False)
    elections=models.ForeignKey(elections, on_delete=models.CASCADE, related_name='election_parties_conn')
    party_name=models.CharField(max_length=200, blank=False)
    party_image = models.ImageField(upload_to='election_party/', null=True, blank=True)
    tag_line=models.TextField(blank=False, default='')    
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

class election_position(models.Model):
    unique_id = models.AutoField(primary_key=True, null=False)
    elections=models.ForeignKey(elections, on_delete=models.CASCADE, related_name='election_position_conn')
    postion_name=models.CharField(max_length=200, blank=False)
    tag_line=models.TextField(blank=False, default='')    
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)                

class election_candidates(models.Model):
    unique_id = models.AutoField(primary_key=True, null=False)
    elections=models.ForeignKey(elections, on_delete=models.CASCADE)
    candidates=models.ForeignKey(user_registration, on_delete=models.CASCADE)    
    party=models.ForeignKey(election_parties, on_delete=models.CASCADE, related_name='election_candidates_party_conn')
    position=models.ForeignKey(election_position, on_delete=models.CASCADE, related_name='election_candidates_position_conn')
    symbol=models.ImageField(upload_to='candidates/', null=True, blank=True)
    symbol_name=models.CharField(max_length=200, blank=False)
    about_us=models.TextField(blank=False, default='')
    tag_line=models.TextField(blank=False, default='')
    manifestos=models.FileField(upload_to='candidates/', null=True, blank=True)
    note_eo=models.TextField(blank=True, default='')
    note_c=models.TextField(blank=True, default='')
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('active', 'Active'),
        ('rejected','Rejected'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)    

class election_votes(models.Model):
    unique_id = models.AutoField(primary_key=True, null=False)
    elections=models.ForeignKey(elections, on_delete=models.CASCADE, related_name='elections_conn')
    candidates=models.ForeignKey(election_candidates, on_delete=models.CASCADE, related_name='candidates_conn')
    position=models.ForeignKey(election_position, on_delete=models.CASCADE, related_name='position_conn')
    voters=models.ForeignKey(user_registration, on_delete=models.CASCADE, related_name='voters_conn')
    vote=models.CharField(max_length=10)    
    date_added=models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
