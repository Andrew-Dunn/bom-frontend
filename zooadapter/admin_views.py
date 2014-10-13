from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse
from zooadapter.models import ZooDashboard 

def zoo_dashboard(request):

   server_info = ZooDashboard.get_zoo_server_info()
   job_info = ZooDashboard.get_jobs_info()
   node_info = ZooDashboard.get_nodes_info()
   
   return render(request, 'admin/zoo_dashboard.html', 
         { 'server_info' : server_info,
           'job_info' : job_info,
           'node_info' : node_info })
