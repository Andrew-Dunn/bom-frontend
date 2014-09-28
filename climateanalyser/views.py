from django.utils.dateformat import format
from django.template.loader import get_template
from django.shortcuts import render
from django.template import RequestContext,loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import *
from models import *
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList

def index(request):
   """Default app page. It's just blank. """
   t = loader.get_template('index.html')
   context = RequestContext(request, {})
   html = t.render(context)
   return HttpResponse(html)

def datafiles(request): 
   """View list of DataFiles in the system."""
   return render(request, 'datafiles.html', { 'datafiles' : 
         DataFile.objects.filter() })

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

   #Filter for current user
   if request.GET.get('show_mine'):
      user = request.user
      template_params['computations'] = Computation.objects.filter(
            created_by=user)
      template_params['show_mine'] = True;
   else:
      template_params['computations'] = Computation.objects.filter()
      template_params['show_mine'] = False;

   return render(request, 'computations.html', template_params)

def load_cache(request):
   """To be used by AJAX requests to load a cached copy of a DataFile."""

   file = request.GET.get('file')

   if file:
      # print contents of file directly to the screen
      full_path = settings.CACHE_DIR + file
      response = StreamingHttpResponse(open(full_path))
      return response

   return HttpResponse('')
