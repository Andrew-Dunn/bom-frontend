from django.db import models
import datetime
import urllib

class Common():

   @staticmethod
   def prepare_config_address(address):
      """ Return address ready for use."""
      if address[:3] is not 'http':
         return 'http://' + address
      return address

   @staticmethod
   def get_http_last_modified(address):

      headers = urllib.urlopen(address).info()
      date = datetime.datetime.strptime(headers['Last-Modified'], 
            '%a, %d %b %Y %H:%M:%S GMT')

      return date


