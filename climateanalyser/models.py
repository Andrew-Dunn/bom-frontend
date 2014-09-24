from django.conf import settings
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
import hashlib, urllib 
from jsonfield import JSONField
from zooadapter.models import ZooAdapter
from solo.models import SingletonModel
from common.models import Common
import json

class ClimateAnalyserConfig(SingletonModel):
   """Configuration options for the app, to be modified in the backend."""

   class Meta:
      verbose_name_plural = "Config"
      verbose_name = "Config"

   tilemill_server_address = models.CharField(max_length=255)

   def get_tilemill_server_address(self):
      """ Return Tilemill server address ready for use. """
      return Common.prepare_config_address(self.tilemill_server_address)

class DataFile(models.Model):
   """A data file, which is cached on the local server."""

   # original remote url of file 
   file_url = models.CharField(max_length=1000,unique=True)
   cached_file = models.CharField(max_length=1000)
   variables = JSONField()

   def clean(self):
      #Create cached file and save data
      self._save_cache()

      self.variables = ZooAdapter.get_datafile_variables(
            self._get_opendap_addr())

      self.last_modified = datetime.now()

   def _save_cache(self):
      """ Cache the file on the OpenDAP server."""
      #file name is md5 string of url
      self.cached_file = hashlib.md5(self.file_url).hexdigest() + '.nc'
      response = urllib.urlretrieve(self.file_url, 
            settings.CACHE_DIR + self.cached_file)

   def _get_opendap_addr(self):
      """Get the address of the file on OpenDAP, after saving cache."""
      return (ZooAdapter.config.get_thredds_server_address() + 
         '/thredds/dodsC/datafiles/inputs/' + self.cached_file)
   
   def update_cache(self):
      """ Update our local cache file, ONLY if necessary."""

      dds_addr = self._get_opendap_addr() + '.dds'

      local_last_modified = Common.get_http_last_modified(dds_addr)
      remote_last_modified = Common.get_http_last_modified(self.file_url)

      # update cache if necessary
      if remote_last_modified > local_last_modified:
         self.__save_cache()

   def get_variables(self):
      return json.loads(self.variables)

   def __unicode__(self):
      return self.file_url

class Calculation(models.Model):
   """ Represents calculation to run on Computation, eg 'regress', 
   'correlate'. """
   name = models.CharField(max_length=100,unique=True)
   min_datafiles = models.IntegerField()
   max_datafiles = models.IntegerField()

   def __unicode__(self):
      return self.name.title()

class Computation(models.Model):
   """The operation performed on data files, such as correlate or regress."""

   STATUS_CHOICES = (
         ('scheduled', 'Scheduled'),
         ('running', 'Running'),
         ('successful', 'Successful'),
         ('failed', 'Failed'),
   )

   created_by = models.ForeignKey(User)
   created_date = models.DateTimeField('date created')
   completed_date = models.DateTimeField('date completed',null=True,
         blank=True)
   status = models.CharField(max_length=100,choices=STATUS_CHOICES,
         default='scheduled')
   calculation = models.ForeignKey(Calculation)
   result_wms = models.CharField(max_length=100,blank=True)
   result_nc = models.CharField(max_length=100,blank=True)
   result_opendap = models.CharField(max_length=100,blank=True)

   def clean(self):
      self.created_date = datetime.now()

   def get_computationdata(self):
      return ComputationData.objects.filter(computation=self).order_by('id')

   def schedule_in_zoo(self):
      result_links = ZooAdapter.schedule_computation(self)

      self.result_wms = result_links['wms']
      self.result_nc = result_links['nc']
      self.result_opendap = result_links['opendap']
      self.save()

class ComputationData(models.Model):
   """Link between Computation and DataFiles. Specific variables for data file
   can be selected.
   """
   datafile = models.ForeignKey(DataFile)   
   computation = models.ForeignKey(Computation)
   variables = JSONField()

   def clean(self):
      # make sure selected variables exist in datafile
      for variable in self.variables:
         if variable not in self.datafile.get_variables():
            raise ValidationError('Variable does not exist in Data File.')

