from django.contrib import admin
from django import forms
from django.template.loader import get_template
from django.shortcuts import render
from django.template import RequestContext,loader
from django.http import HttpResponse
from django.http import HttpResponse
from solo.admin import SingletonModelAdmin
from zooadapter.models import ZooAdapterConfig,ZooDashboard
from django.conf.urls import patterns

class AdminZooAdapterConfigForm(forms.ModelForm):

   zoo_public_key = forms.CharField(widget=forms.Textarea)
   zoo_private_key = forms.CharField(widget=forms.Textarea)

   class Meta:
      model = ZooAdapterConfig

class ZooAdapterConfigAdmin(SingletonModelAdmin):
   form = AdminZooAdapterConfigForm

admin.site.register(ZooAdapterConfig, ZooAdapterConfigAdmin)
admin.site.register(ZooDashboard, SingletonModelAdmin)
