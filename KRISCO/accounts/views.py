from typing import Counter
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models import Avg, Count, Min, Sum
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import permission_required, user_passes_test
import pandas as pd
import math
# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, 'Oh No,Invalid Username or Password !')
            return redirect('login')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = request.POST['username']

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Huff ,Username already exist')
            return redirect("register")
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Come On, Email was already Taken !')
            return redirect("register")
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email)
            mydict = {'username': username}
            user.save()
            html_template = 'register_email.html'
            html_message = render_to_string(html_template, context=mydict)
            subject = 'Welcome to Service-Verse'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.send()
            return redirect("login")
    else:
        return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect("/")

