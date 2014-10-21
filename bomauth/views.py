from django.template.loader import get_template
from django.contrib import messages
from django.template import RequestContext,loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from bomauth.forms import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm
from climateanalyser.models import Computation

def index(request):
   t = loader.get_template('index.html')
   context = RequestContext(request, {})
   html = t.render(context)
   return HttpResponse(html)

def register(request):
   if request.method == 'POST':
      form = UserRegisterForm(request.POST)
      userName = request.REQUEST.get('username', None)
      userPass = request.REQUEST.get('password', None)
      userMail = request.REQUEST.get('email', None)
      userFirst = request.REQUEST.get('first_name', None)
      userLast = request.REQUEST.get('last_name', None)
      if form.is_valid():
         user = User.objects.create_user(username = userName, email = userMail,
               password = userPass)
         user.last_name = userLast;
         user.first_name = userFirst;
         user.save();
	 messages.add_message(request, messages.INFO, 'User created successfully')
         return HttpResponseRedirect('/login')
      t = loader.get_template('register.html')
      context = RequestContext(request, { 'form':form })
      html = t.render(context)
      return HttpResponse(html)

   form = UserRegisterForm(request.POST)
   userName = request.REQUEST.get('username', None)
   t = loader.get_template('register.html')
   context = RequestContext(request, { 'form':form })
   html = t.render(context)
   return HttpResponse(html)

def change_password(request):
   if request.user.is_authenticated():
      t = loader.get_template('changepassword.html')
      context = RequestContext(request, { 'text':text })
      html = t.render(context)
      return HttpResponse(html)
   else:
      return HttpResponseRedirect('/login')

def profile(request):
   profile = request.user
   mycomputations = Computation.objects.filter(created_by = request.user.id)
   t = loader.get_template('profile.html')
   context = RequestContext(request, { 'profile':profile, 'mycomputations':mycomputations })
   html = t.render(context)
   return HttpResponse(html)

def update_profile(request):
   args = {}

   if request.method == 'POST':
      form = UpdateProfile(request.POST)
      form.actual_user = request.user
      if form.is_valid():
         form.save()
         return HttpResponseRedirect(reverse('update_profile_success'))
   else:
      form = UpdateProfile()

   t = loader.get_template('update_profile.html')
   context = RequestContext(request, {'form':form})
   html = t.render(context)
   return HttpResponse(html)
