from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse
#from zooadapter.models import ZooDashboard 

def update_all_cache(request):

   return render(request, 'admin/zoo_dashboard.html', 
         { 'server_info' : server_info,
           'job_info' : job_info,
           'node_info' : node_info })
