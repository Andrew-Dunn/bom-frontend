from django.db.models.signals import post_delete,pre_save
from models import DataFile,Computation
import os
from django.conf import settings
from zooadapter.models import ZooAdapter

def delete_cache(sender, **kwargs):
   """ Delete local cache file when deleting a DataFile from the system. """
   try:
      os.remove(settings.CACHE_DIR + kwargs['instance'].cached_file)
   except OSError as e:
      if "No such file or directory" not in e.strerror:
         raise OSError(e.errno, e.strerror, e.filename)

def save_cache(sender, **kwargs):
   kwargs['instance'].save_cache()

post_delete.connect(delete_cache, sender=DataFile)
pre_save.connect(save_cache, sender=DataFile)
