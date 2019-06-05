'''
Author: Sheeba Samuel, Friedrich-Schiller University, Jena
Email: caesar@uni-jena.de
Date created: 29.04.2016
'''

from django.conf.urls import *
from Experiment import views

urlpatterns = patterns('django.views.generic.simple',

                       url(r'^experiment/', views.index, name='Experiment_index'),
                       url(r'^view_input_data/$', views.view_input_data, name="view_input_data"),
                       url(r'^print_input_data/$', views.print_input_data, name="print_input_data"),
                       url(r'^get_history_data/$', views.get_history_data, name="get_history_data"),
                       url(r'^list_all_input/$', views.list_all_input, name="list_all_input"),
                       url(r'^save_input_data/$', views.save_input_data, name="save_input_data"),
                       url(r'^delete_input_data/$', views.delete_input_data, name="delete_input_data"),
                       url(r'^get_exp_material_details/$', views.get_exp_material_details, name="get_exp_material_details"),
                       url(r'^search_experiment/$', views.search_experiment, name="search_experiment"),
                       url(r'^download_file/$', views.download_file, name="download_file"),
                       url(r'^get_search_tabs/$', views.get_search_tabs, name="get_search_tabs"),
                       url(r'^get_proposals_data/$', views.get_proposals_data, name="get_proposals_data"),
                       url(r'^semantic_search/$', views.semantic_search, name="semantic_search"),
                       url(r'^semantic_search_experiment/$', views.semantic_search_experiment, name="semantic_search_experiment"),
                       url(r'^view_script_data/$', views.view_script_data, name="view_script_data"),
                       url(r'^get_instances/$', views.get_instances, name="get_instances"),
                       url(r'^get_properties/$', views.get_properties, name="get_properties"),
                       )
