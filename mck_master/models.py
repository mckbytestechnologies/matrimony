from django.db import models
from config import app_gv as gv
from django_countries.fields import CountryField
from django.conf import settings
from django_countries.fields import CountryField



# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    iso_4217_alpha = models.CharField(max_length=200)
    iso_4217_numeric = models.CharField(max_length=200)
    iso2 = models.CharField(max_length=2)
    iso3 = models.CharField(max_length=3)
    capital_city = models.CharField(max_length=200)
    telephone_calling_code = models.CharField(max_length=5)
    internet_domain_code = models.CharField(max_length=5)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'country'

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    country = models.ForeignKey(Country, related_name='country',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'state'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    state = models.ForeignKey(State, related_name='state',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'city'

class SupportPageContent(models.Model):
    support_key = models.CharField(max_length=255)
    support_value = models.CharField(max_length=255)
    support_description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    datamode = models.CharField(max_length=1, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return "{0}".format(self.support_value)

    class Meta:
        db_table = 'support_page_content'


class VersionControl(models.Model):
    app = models.CharField(choices=gv.APP_LIST, default='CUS_ANDROID_APP', max_length=100)
    version = models.CharField(max_length=10)
    released_on = models.DateTimeField(auto_now_add=True)
    datamode = models.CharField(max_length=5, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'version_control'

    def __str__(self):
        return "{0}-{1}".format(self.app, self.version)


class MasterPermission(models.Model):
    app_name = models.CharField(max_length=255, db_index=True) # App Name
    class_name = models.CharField(max_length=255, unique=True, db_index=True) # Class Name
    module_name = models.CharField(max_length=255)
    function_name = models.CharField(max_length=255) # Read, Update, delete, btn action
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    def __str__(self):
        return f"{self.class_name} - {self.function_name}"

    class Meta:
        db_table = 'master_permission'



class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'sub_category'

    def __str__(self):
        return self.name


class Banner(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'banner'

    def __str__(self):
        return self.name


class Gallery(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'gallery'

    def __str__(self):
        return self.name


class Offers(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    class Meta:
        db_table = 'offers'
    
    def __str__(self):
        return self.name


class ClientFeedback(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    feedback = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to="ddata", blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    
    def __str__(self):
        return ''
    
    class Meta:
        db_table = 'client_feedback'
        


class Profile(models.Model):
    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='profiles'
)


    # user = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    dob = models.DateField(null=True, blank=True)
    religion = models.CharField(max_length=50, blank=True)
    caste = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    location = CountryField(blank=True, null=True)
    education = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True)
    created_by = models.CharField(max_length=8)
    updated_by = models.CharField(max_length=8)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    datamode = models.CharField(max_length=20, default='A', choices=gv.DATAMODE_CHOICES)

    
    def __str__(self):
        return ''
    
    class Meta:
        db_table = 'profile'