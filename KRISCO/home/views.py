from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

# Create your views here.
def home(request):
    slides = Slides.objects.all()
    adds = ScrollingAdd.objects.all()
    return render(request,'home.html',{'slides':slides,'adds':adds})

def contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Create a new ContactUs instance and save it to the database
        contact_entry = ContactUs(first_name=first_name, last_name=last_name, email=email, message=message)
        contact_entry.save()
        
        messages.success(request, 'Thank you for your message. We will get back to you shortly.')
    return render(request,'contact.html')   

def team(request):
    team_members = Team.objects.all()
    return render(request,'team.html',{'team_members':team_members})

def brands(request):
    brand_lists = Brand.objects.all()
    paginator = Paginator(brand_lists, 18)  # Show 20 brands per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'brands.html',{'page_obj': page_obj})


def about(request):
    return render(request,'about.html')