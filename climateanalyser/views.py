from django.utils.dateformat import format
from django.template.loader import get_template
from django.shortcuts import render
from django.template import RequestContext,loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import *
from models import *
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urlparse import urlparse

ITEMS_PER_PAGE = 25

def index(request):
   """Default app page. It's just blank. """
   t = loader.get_template('index.html')
   context = RequestContext(request, {})
   html = t.render(context)
   return HttpResponse(html)

def datafiles(request): 
   """View list of DataFiles in the system."""

   page = request.GET.get('page')
   paginator = Paginator(DataFile.objects.all(), ITEMS_PER_PAGE)

   try:
      datafiles = paginator.page(page)
   except PageNotAnInteger:
      datafiles = paginator.page(1)
   except EmptyPage:
      datafiles = paginator.page(paginator.num_pages)

   page_range = range(paginator.num_pages)
   for datafile in datafiles:
      datafile.filename =  urlparse(datafile.file_url).path.split('/')[-1]

   return render(request, 'datafiles.html', 
         { 'datafiles' : datafiles, 'page_range' : page_range })

@login_required
def create_datafile(request):
   """View to create a new DataFile."""

   if request.method == 'POST':

      form = DataFileForm(request.POST)

      if form.is_valid():

         form.save()

         messages.success(request, 'Data File successfully created!')
         return HttpResponseRedirect('/datafiles')
   else:
      form = DataFileForm()

   return render(request, 'create_datafile.html', { 'form' : form })

@login_required
def create_computation(request, computation_pk=None): 
   """View to create a new Computation"""

   if computation_pk:
      # if we need to restore user submitted data to screen
      computation = Computation.objects.get(pk=computation_pk)
   else:
      computation = Computation()
   
   ComputationFormSet = inlineformset_factory(Computation, ComputationData,
         form=ComputationDataForm,extra=1)
  
   if request.method == 'POST':
      form = ComputationForm(request.POST,instance=computation)
      formset = ComputationFormSet(request.POST,instance=computation)

      if form.is_valid() and formset.is_valid():

         form.save()
         formset.save()
         computation.schedule_in_zoo()
         # redirect on success
         messages.success(request, 'Computation successfully created!')
         return HttpResponseRedirect('/computations')

   else:
      form = ComputationForm(initial={ 'created_by': request.user },
            instance=computation)
      formset = ComputationFormSet(instance=computation)

   return render(request, 'create_computation.html', 
         { 'form' : form, 'formset' : formset, })

def computation(request):
   """View a single Computation."""

   computation = Computation.objects.get(id=request.GET.get('id'))
   config = ClimateAnalyserConfig.objects.get()
   tilemill_server_address = config.get_tilemill_server_address()

   return render(request, 'computation.html', {'computation': computation,
         'tilemill_server_address' : tilemill_server_address })

def computations(request):
   """View list of Computations in the system."""

   template_params = {}
   page = request.GET.get('page')

   #Filter for current user
   if request.GET.get('show_mine'):
      computation_list = Computation.objects.filter(created_by=request.user)
      template_params['show_mine'] = True;
   else:
      computation_list = Computation.objects.all();

   computation_list = computation_list.order_by('-id')
   paginator = Paginator(computation_list, ITEMS_PER_PAGE)

   try:
      computations = paginator.page(page)
   except PageNotAnInteger:
      computations = paginator.page(1)
   except EmptyPage:
      computations = paginator.page(pagination.num_pages)

   template_params['computations'] = computations
   template_params['page_range'] = range(paginator.num_pages)

   return render(request, 'computations.html', template_params)


