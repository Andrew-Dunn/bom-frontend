from django.conf.urls import url
from climateanalyser import views
from climateanalyser import ajax

urlpatterns = [
   url(r'^$', views.index, name='index'),
   url(r'^datafiles/$', views.datafiles, name='datafiles'),
   url(r'^create_datafile/$', views.create_datafile, name='create_datafile'),
   url(r'^create_computation/$', views.create_computation,
         name='create_computation'),
   url(r'^computations/$', views.computations, name='computations'),
   url(r'^computation$', views.computation, name='computation'),
   url(r'^load_cache$', ajax.load_cache, name='load_cache'),
   url(r'^load_datafile_variables$', ajax.load_datafile_variables,
         name='load_datafile_variables'),
   url(r'^update_computation_status$', ajax.update_computation_status,
         name='update_computation_status'),
   url(r'^get_data_range$', ajax.get_data_range, name='get_data_range'),
   url(r'^get_data_value$', ajax.get_data_value, name='get_data_value'),
   url(r'^update_datafile_cache$', ajax.update_datafile_cache, 
         name='update_datafile_cache'),
]
