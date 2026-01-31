"""
Views - VLR Website App
"""

from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from config import app_logger
from config import app_seo as seo
from squarebox.models import *
from mck_website.api import *
from mck_website.models import *
from django.urls import reverse 
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from mck_auth import build_table as bt
from mck_auth import role_validations as rv
from squarebox import api
from squarebox import forms
from squarebox import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import render
from django.core.paginator import Paginator
from datetime import date
from dateutil.relativedelta import relativedelta
from mck_master.models import Profile


LOG_NAME = "app"
logger = app_logger.createLogger(LOG_NAME)


def pki_validation_view(request):
    file_path = os.path.join(settings.BASE_DIR, "mck_website", "templates", "verify.txt")
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)



class HomePage(TemplateView):
    """
    Home Page
    """
    template_name = "home.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("home_page")

        context["property"] = Property.objects.exclude(datamode='D').order_by('-updated_on')
        context["profile"] = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        context["property_type"] = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        context["property_image"] = PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
        context["lead"] = Lead.objects.exclude(datamode='D').order_by('-updated_on')
        context["cities"] = Property.objects.exclude(datamode='D') \
                                            .values_list('city', flat=True) \
                                            .distinct() \
                                            .order_by('city')
        context["property"] = (
            Property.objects.exclude(datamode='D')
            .prefetch_related(
                Prefetch('images', queryset=PropertyImage.objects.exclude(datamode='D'))
            )
            .order_by('-updated_on')
)

        logger.info(request.GET)
        return render(request, self.template_name, context)


class PropertyPage(TemplateView):
    template_name = "property_page.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all properties excluding deleted ones
        qs = Property.objects.exclude(datamode='D')
        
        # Apply filters
        city = request.GET.get('city')
        listing_type = request.GET.get("listing_type")
        property_type = request.GET.get('property_type')
        budget = request.GET.get('budget')
        sort = request.GET.get('sort', 'newest')

        if city:
            qs = qs.filter(city__icontains=city)

        if property_type:
            qs = qs.filter(property_type__name__iexact=property_type)

        if listing_type:
            qs = qs.filter(listing_type__iexact=listing_type)

        if budget:
            if budget == "Below 100k":
                qs = qs.filter(price__lt=100000)
            elif budget == "100k - 300k":
                qs = qs.filter(price__range=(100000, 300000))
            elif budget == "Above 300k":
                qs = qs.filter(price__gt=300000)

        # Apply sorting
        if sort == 'price_low':
            qs = qs.order_by('price')
        elif sort == 'price_high':
            qs = qs.order_by('-price')
        else:  # newest
            qs = qs.order_by('-updated_on')

       

        # Pagination
        paginator = Paginator(qs, 9)  # Show 9 properties per page
        page_number = request.GET.get('page')
        properties = paginator.get_page(page_number)
        
        # Prefetch related images
        properties.object_list = properties.object_list.prefetch_related(
            Prefetch(
                'images',  
                queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on'),
                to_attr='property_images_list'  
            )
        )

        context["properties"] = properties
        context["property_types"] = PropertyType.objects.exclude(datamode='D').order_by('-updated_on')
        context["cities"] = (
            Property.objects.exclude(datamode='D')
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )

        return render(request, self.template_name, context)


class PropertyDetailPage(TemplateView):
    template_name = "resources.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        property_id = kwargs.get('pk')  # from URL
        property_obj = get_object_or_404(
            Property.objects.prefetch_related(
                Prefetch(
                    'images',
                    queryset=PropertyImage.objects.exclude(datamode='D').order_by('-updated_on')
                )
            ),
            pk=property_id
        )

        context["property"] = property_obj
        return render(request, self.template_name, context)

class PropertyCreatePage(TemplateView):
    template_name = "pages/property_create.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("property_create")
        property = Property.objects.exclude(datamode='D').order_by('-updated_on')
        context["property"] = property
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
    
class MaintenancesCreatePage(TemplateView):
    template_name = "pages/faq.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("maintenance")
        maintenance = MaintenanceRequest.objects.exclude(datamode='D').order_by('-updated_on')
        context["maintenance"] = maintenance
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PropertySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received property save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_property_save(request)
            if result:
                logger.info("Property saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save property: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in PropertySaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        

class MaintenanceSaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received Maintenance save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_maintenance_save(request)
            if result:
                logger.info("maintenance saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save maintenance: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in maintenanceSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
        
class EnquiryCreatePage(TemplateView):
    template_name = "includes/enquiry.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("lead")
        lead = Lead.objects.exclude(datamode='D').order_by('-updated_on')
        context["lead"] = lead
        property_type = request.GET.get('property_type', '')
        context["selected_property_type"] = property_type  
        logger.info(request.GET)
        return render(request, self.template_name, context)

class EnquirySaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received lead save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_enquiry_save(request)
            if result:
                logger.info("lead saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save lead: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in leadSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class AboutPage(TemplateView):
    """
    About Page
    """
    template_name = "about.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class OurServicesPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "our_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("about_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    

class PrivacyPolicyPage(TemplateView):
    """
    ourservices Page
    """
    template_name = "privacy_policy.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("privacy_policy_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class TermsPage(TemplateView):
    """
    terms Page
    """
    template_name = "terms.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("terms_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class PropertyLegalServicesPage(TemplateView):
    """
    terms Page
    """
    template_name = "property_legal_services.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("property_legal_services_page")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class SolarPage(TemplateView):
    template_name = "solar.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("solar")
        logger.info(request.GET)
        return render(request, self.template_name, context)


class FencingPage(TemplateView):
    template_name = "fencing.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("fencing")
        logger.info(request.GET)
        return render(request, self.template_name, context)
    
class LandLevellingPage(TemplateView):
    template_name = "pages/land_leveling.html"
    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwargs'] = seo.get_page_tags("land_levelling")
        logger.info(request.GET)
        return render(request, self.template_name, context)

class ProfileCreatePage(TemplateView):
    template_name = "includes/enquiry.html"

    @app_logger.functionlogs(log=LOG_NAME)
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_kwargs"] = seo.get_page_tags("profile")
        profile = Profile.objects.exclude(datamode='D').order_by('-updated_on')
        context["profile"] = profile
        # property_type = request.GET.get('property_type', '')
        # context["selected_property_type"] = property_type  
        logger.info(request.GET)
        return render(request, self.template_name, context)


class MyProfilePage( TemplateView):
    """Display and edit the logged-in user's profile"""
    template_name = "my_profile.html"
    login_url = '/login/'  # Adjust as needed
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create profile for the logged-in user
        profile_obj, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                "created_by": "USER",
                "gender": "",
                "updated_by": "USER"
            }
        )
        
        # Calculate age if DOB exists
        age = None
        if profile_obj.dob:
            today = date.today()
            age = today.year - profile_obj.dob.year - (
                (today.month, today.day) < (profile_obj.dob.month, profile_obj.dob.day)
            )
        
        context["profile"] = profile_obj
        context["age"] = age
        context["is_my_profile"] = True
        
        return render(request, self.template_name, context)


class ProfileSaveView(TemplateView):
    """API view for saving profile (AJAX)"""
    # @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            files = request.FILES
            
            # Get or create profile for logged-in user
            profile_obj, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={"created_by": request.user.username}
            )
            
            # Update fields
            profile_obj.gender = data.get("gender", profile_obj.gender)
            
            # Handle date fields
            dob_str = data.get("dob")
            if dob_str:
                try:
                    profile_obj.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    profile_obj.dob = None
            
            profile_obj.religion = data.get("religion", profile_obj.religion)
            profile_obj.caste = data.get("caste", profile_obj.caste)
            profile_obj.phone = data.get("phone", profile_obj.phone)
            profile_obj.bio = data.get("bio", profile_obj.bio)
            profile_obj.location = data.get("location", profile_obj.location)
            profile_obj.education = data.get("education", profile_obj.education)
            profile_obj.occupation = data.get("occupation", profile_obj.occupation)
            
            # Handle income
            income_str = data.get("annual_income")
            if income_str:
                try:
                    profile_obj.annual_income = float(income_str)
                except ValueError:
                    profile_obj.annual_income = None
            
            profile_obj.marital_status = data.get("marital_status", profile_obj.marital_status)
            
            # Handle profile photo
            if "profile_photo" in files:
                profile_obj.profile_photo = files["profile_photo"]
            
            profile_obj.updated_by = request.user.username
            profile_obj.save()
            
             # ✅ SEND REDIRECT URL
            return JsonResponse({
                "success": True,
                "message": "Profile saved successfully",
                "redirect_url": reverse("mck_website:home_page")
            })
            
        except Exception as e:
            logger.exception("Error saving profile")
            return JsonResponse({
                "success": False,
                "message": f"Error saving profile: {str(e)}"
            }, status=400)


class ProfilSaveView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Received profile save request")
            logger.info("POST data: %s", request.POST)
            logger.info("FILES data: %s", request.FILES)
            
            result, message = api.ajax_profile_save(request)
            if result:
                logger.info("profile saved successfully")
                return JsonResponse({"status": "success", "message": message})
            else:
                logger.error("Failed to save profile: %s", message)
                return JsonResponse({"status": "fail", "message": message}, status=400)
                
        except Exception as e:
            logger.exception("Unexpected error in profileSaveView")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class ProfileDetailPage(TemplateView):
    template_name = "resources.html"

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        profile_id = kwargs.get('pk')  # from URL
        profile_obj = get_object_or_404(
            Profile.objects.exclude(datamode='D'),
            pk=profile_id
        )

        context["profile"] = profile_obj
        return render(request, self.template_name, context)




class ProfilePage(TemplateView):
    template_name = "property_page.html"

    def get(self, request, *args, **kwargs):
        context = {}

        # Base queryset
        profiles = Profile.objects.exclude(datamode='D').select_related('user')

        # ------------------ FILTERS ------------------
        city = request.GET.get('city')  # maps to location
        gender = request.GET.get('gender')  # M / F / O
        religion = request.GET.get('religion')
        education = request.GET.get('education')
        profession = request.GET.get('profession')  # maps to occupation
        status = request.GET.get('status')  # S / M / D / W
        income = request.GET.get('income')
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        sort = request.GET.get('sort', 'newest')

        # ------------------ APPLY FILTERS ------------------
        if city:
            profiles = profiles.filter(location__icontains=city)

        if gender:
            # Map gender values from form to model values
            gender_map = {'male': 'M', 'female': 'F', 'other': 'O'}
            if gender in gender_map:
                profiles = profiles.filter(gender=gender_map[gender])

        if religion:
            profiles = profiles.filter(religion__iexact=religion)

        if education:
            profiles = profiles.filter(education__icontains=education)

        if profession:
            profiles = profiles.filter(occupation__icontains=profession)

        if status:
            profiles = profiles.filter(marital_status=status)

        # ------------------ AGE FILTER ------------------
        if age_min or age_max:
            today = date.today()
            
            if age_min and age_min.isdigit():
                # Born at most age_min years ago (minimum age)
                max_birth_date = today - relativedelta(years=int(age_min))
                profiles = profiles.filter(dob__lte=max_birth_date)

            if age_max and age_max.isdigit():
                # Born at least age_max years ago (maximum age)
                min_birth_date = today - relativedelta(years=int(age_max))
                profiles = profiles.filter(dob__gte=min_birth_date)

        # ------------------ INCOME FILTER ------------------
        if income:
            if income == "below_10":
                profiles = profiles.filter(annual_income__lt=1000000)
            elif income == "10_25":
                profiles = profiles.filter(annual_income__gte=1000000, annual_income__lte=2500000)
            elif income == "25_50":
                profiles = profiles.filter(annual_income__gte=2500000, annual_income__lte=5000000)
            elif income == "50_100":
                profiles = profiles.filter(annual_income__gte=5000000, annual_income__lte=10000000)
            elif income == "above_100":
                profiles = profiles.filter(annual_income__gt=10000000)

        # ------------------ SORTING ------------------
        if sort == "age_low":
            profiles = profiles.order_by('-dob')  # younger first
        elif sort == "age_high":
            profiles = profiles.order_by('dob')   # older first
        elif sort == "compatibility":
            # Add your compatibility logic here
            profiles = profiles.order_by('-updated_on')
        else:
            profiles = profiles.order_by('-updated_on')

        # ------------------ ANNOTATE AGE ------------------
        # Calculate age for each profile
        profiles_list = []
        today = date.today()
        for profile in profiles:
            if profile.dob:
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )
                profile.age = age
            else:
                profile.age = None
            
            # Add full name from user
            if profile.user:
                profile.name = f"{profile.user.first_name} {profile.user.last_name}"
            else:
                profile.name = ""
            
            profiles_list.append(profile)

        # ------------------ PAGINATION ------------------
        paginator = Paginator(profiles_list, 9)
        page_number = request.GET.get('page')
        profiles_page = paginator.get_page(page_number)

        context["profiles"] = profiles_page
        context["filters"] = request.GET

        return render(request, self.template_name, context)


def ajax_profile_save(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        })

    try:
        profile_obj, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"created_by": "SYSTEM"}
        )

        pDict = request.POST
        files = request.FILES

        profile_obj.gender = pDict.get("gender", "")
        profile_obj.dob = pDict.get("dob") or None
        profile_obj.religion = pDict.get("religion", "")
        profile_obj.caste = pDict.get("caste", "")
        profile_obj.phone = pDict.get("phone", "")
        profile_obj.bio = pDict.get("bio", "")
        profile_obj.location = pDict.get("location") or None
        profile_obj.education = pDict.get("education", "")
        profile_obj.occupation = pDict.get("occupation", "")
        profile_obj.annual_income = pDict.get("annual_income") or None
        profile_obj.marital_status = pDict.get("marital_status", "")

        if files.get("profile_photo"):
            profile_obj.profile_photo = files.get("profile_photo")

        profile_obj.updated_by = "SYSTEM"
        profile_obj.save()

        return JsonResponse({
            "success": True,
            "message": "Profile saved successfully"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })

