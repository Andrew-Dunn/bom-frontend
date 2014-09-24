from django.db.models.signals import post_delete,post_save
from models import DataFile,Computation
import os
from django.conf import settings
from zooadapter.models import ZooAdapter

def delete_cache(sender, **kwargs):
   """ Delete local cache file when deleting a DataFile from the system. """
   os.remove(settings.CACHE_DIR + kwargs['instance'].cached_file)

def schedule_computation(sender, **kwargs):
   """ Schedule a computation on the Zoo server after it's been saved. """
   sender.schedule_in_zoo()

post_delete.connect(delete_cache, sender=DataFile)
post_save.connect(schedule_computation, sender=Computation)
