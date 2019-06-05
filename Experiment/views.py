#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Author: Sheeba Samuel, Friedrich-Schiller University, Jena
Email: caesar@uni-jena.de
Date created: 20.09.2017
'''

import logging

import subprocess
from django.http import HttpResponse
from omeroweb.webclient.decorators import login_required
from omeroweb.webclient.decorators import render_response
import omero
import Ice
import IceImport
from omeroweb.webgateway.views import jsonp
from omero.util.decorators import timeit, TimeIt

import utilities
from Experiment.controller import experimentController
from Experiment.controller import semanticSearch
from django.contrib import messages
from Experiment.forms import createform

from omero.gateway import BlitzGateway
import json
import os
import os.path
import omero.java

import urllib
import httplib2

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from cgi import escape
import datetime
from django.core.files.storage import FileSystemStorage
from omeroweb.decorators import ConnCleaningHttpResponse, parse_url
from django.conf import settings


def getDatasetIdFromRequest(kwargs):
    """ Parse request and get dataset id from request
        @param kwargs request args
    """
    split_list = kwargs['url'].rsplit('/')
    if 'dataset' in split_list:
        index = split_list.index('dataset')
        datasetId = split_list[index + 1]
        return int(datasetId)


@login_required()
@render_response()
def index(request, conn=None, **kwargs):
    """ Main Entry point for the Experiment Tab.
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/experiment_data.html'
    datasetId = getDatasetIdFromRequest(kwargs)
    context = {
        'template': template_name,
        'dataset': datasetId
    }
    exp_id = experimentController.get_experiment_id_from_dataset(conn, int(datasetId))
    if exp_id:
        rlobject_type = 'Experiment'
        model_sections = experimentController.get_sections_from_model(conn, rlobject_type)
        experiment_json = experimentController.get_json(conn, rlobject_type, exp_id)
        context['Experiments'] = experiment_json
        context['sections'] = model_sections
        context['exp_id'] = exp_id
        context['can_add'] = 0
    else:
        context['message'] = 'No Experimental data'
        context['can_add'] = 1
    return context


@login_required()
@render_response()
def delete_input_data(request, conn=None, **kwargs):
    """ Delete Experimenta data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/delete_input_data.html'
    context = {
        'template': template_name
    }
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
        context['input_id'] = input_id

    if request.method == 'GET':
        context['input_type'] = input_type
        return context

    if request.method == 'POST':
        experimentController.delete_rl_object(conn, input_type, input_id)
        context['message'] = "Deleted Successfully"
        return context


@login_required()
@render_response()
def get_exp_material_details(request, conn=None, **kwargs):
    """ Load All information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/load_input_data.html'
    context = {
        'template': template_name
    }
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))
        context['dataset'] = datasetId
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
        context['input_type'] = input_type
    if 'can_add' in request.GET:
        context['can_add'] = str(request.GET.get('can_add', None))
    return context


@login_required()
@render_response()
def list_all_input(request, conn=None, **kwargs):
    """ Get all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/list_all_input.html'
    context = {
        'template': template_name
    }
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))
        context['dataset'] = datasetId
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
        context['input_type'] = input_type

    if request.method == 'GET':
        context['experiment_materials'] = experimentController.get_all_exp_materials(conn, input_type, status=1)
        return context


@login_required()
@render_response()
def get_proposals_data(request, conn=None, **kwargs):
    """ Get all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/list_proposals.html'
    context = {
        'template': template_name
    }
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))
        context['dataset'] = datasetId
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
        context['input_id'] = input_id
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
        context['input_type'] = input_type
    if 'flag' in request.GET:
        flag = int(request.GET.get('flag', -1))
        context['flag'] = flag

    if request.method == 'GET':
        if flag == 1:
            context['proposals'] = experimentController.get_my_proposals(conn, input_type, status=2, flag=1)
        elif flag == 2:
            context['proposals'] = experimentController.get_proposals_on_mine(conn, input_type, status=2, flag=2)
        return context

    if request.method == 'POST':
        proposal_action = request.POST.get('proposal_action')
        action_id = proposal_action.split(':')[0]
        if action_id:
            experimentController.execute_proposal_action(conn, input_type, input_id, proposal_action.split(':')[0])
        return context

    context['template'] = template_name
    return context


@login_required(doConnectionCleanup=False)
def download_file(request, conn=None, **kwargs):
    """ Returns the file annotation as an http response for download """
    if 'fileId' in request.GET:
        id = request.GET.get('fileId', None)
        fileId = int(id) if id else -1

    fileService = utilities.get_receptor_light_file_service(conn)
    fileService.openFile(fileId, False)
    fileInfo = fileService.getFileInformation(fileId)
    rsp = ConnCleaningHttpResponse(
        fileService.readFileData(fileId, fileInfo.getSize().getValue()))
    rsp.conn = conn
    rsp['Content-Type'] = 'application/force-download'
    rsp['Content-Length'] = fileInfo.getSize().getValue()
    rsp['Content-Disposition'] = ('attachment; filename=%s'
                                  % (fileInfo.getName().getValue().replace(" ", "_")))
    if fileId != -1:
        fileService.closeFile(fileId)
    return rsp


@login_required()
@render_response()
def view_input_data(request, conn=None, **kwargs):
    """ View all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/view_input_data.html'
    context = {
        'template': template_name
    }
    input_data = None
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
    if input_id and input_type:
        model_sections = experimentController.get_sections_from_model(conn, input_type)
        input_data = experimentController.get_json(conn, input_type, input_id)
        context['InputData'] = input_data
        context['sections'] = model_sections
        return context


@login_required()
@render_response()
def get_search_tabs(request, conn=None, **kwargs):
    template_name = 'Experiment/Views/launch_search.html'
    context = {
        'template': template_name
    }
    return context


@login_required()
@render_response()
def search_experiment(request, conn=None, **kwargs):
    """ Search all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/search_experiment.html'
    context = {
        'template': template_name
    }
    if request.method == 'GET':
        return context

    search_results_json = []
    r = request.GET or request.POST
    search_query = r.get('search_query')
    if request.method == 'POST' and search_query:
        search_results_json = experimentController.get_search_results(conn, search_query)
        if len(search_results_json) > 0:
            context['search_results'] = search_results_json
        else:
            context['message'] = "No results found"
    context['template'] = template_name
    return context


def get_fieldsets_of_type(conn, input_type):
    fieldsets = experimentController.get_fieldsets_of_type(conn, input_type)
    return fieldsets


def execute_action_on_proposals(request, conn=None, **kwargs):
    list_all_input(request, conn=None, **kwargs)


@login_required()
@render_response()
def save_input_data(request, conn=None, **kwargs):
    """ Add new or edit information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/save_input_data.html'
    context = {
        'template': template_name
    }
    input_id = -1
    action = None
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
        context['input_id'] = input_id
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))
        context['dataset'] = datasetId
    if 'action' in request.GET:
        action = str(request.GET.get('action', None))
        context['action'] = action

    input_data = None
    if input_type and input_id:
        if 'id' in request.GET and input_id != -1:
            input_data = experimentController.get_json(conn, input_type, input_id)
        else:
            input_data = experimentController.get_metadata_json(input_type)

    fieldsets = get_fieldsets_of_type(conn, input_type)
    choices = experimentController.get_all_exp_materials_choices(conn)
    experimenter_choices = experimentController.get_all_experimenters(conn)
    rl_form = createform.initialise_fieldsets(fieldsets)
    form = rl_form(form_data=input_data, input_type=input_type, experimenter_choices=experimenter_choices)

    if request.method == 'GET':
        context['InputData'] = input_data
        context['choices'] = choices
        context['input_type'] = input_type
        context['form'] = form
        return context

    if request.method == 'POST':
        rl_form = createform.initialise_fieldsets(fieldsets)
        form = rl_form(request.POST, request.FILES, form_data=input_data, input_type=input_type,
                       experimenter_choices=experimenter_choices)
        if form.is_valid():
            if form.has_changed():
                changed_dict = {}
                if input_type == 'Experiment':
                    changed_dict['DatasetId'] = datasetId
                    form.cleaned_data['DatasetId'] = datasetId
                input_name = ''
                for key in form.changed_data:
                    if key == 'Name':
                        input_name = form.cleaned_data[key]
                    changed_dict[key] = form.cleaned_data[key]
                save_value = experimentController.save_rl_object(conn, input_type, changed_dict, form.cleaned_data, id=input_id,
                                                    input_name=input_name, files=request.FILES, action=action)
                if save_value == 1:
                    messages.success(request, 'Saved Successfully')
                else:
                    messages.error(request, "Could not save the data. Please check the data again.")
            return context


@login_required()
@render_response()
def print_input_data(request, conn=None, **kwargs):
    """ Print all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))

    if input_id and input_type:
        rlobject_name = experimentController.get_rl_object_name(conn, input_type, input_id)
        input_data = experimentController.get_json(conn, input_type, input_id)
        model_sections = experimentController.get_sections_from_model(conn, input_type)
        elements = []
        rows = list()
        model_name = ''
        stylesheet = getSampleStyleSheet()
        style = stylesheet["BodyText"]
        heading = input_type + ": " + rlobject_name
        rows.append([Paragraph(heading, get_header_style())])
        for sec in model_sections:
            for section, value in input_data.items():
                if sec == section:
                    section_header = Paragraph(sec, get_paragraph_style())
                    table_data = [section_header, '']
                    rows.append(table_data)
                    for data in value:
                        if data['isVisible'] == 'True':
                            if 'value' in data and data['value'] is not None:
                                if data['uiType'] == 'multiplefiles':
                                    filenames = []
                                    for fileId, filename in data['value'].items():
                                        filenames.append(str(filename))
                                    val = str(filenames)
                                else:
                                    val = data['value']
                            else:
                                val = str('-')
                            if 'key' in data and data['key'] == 'Name':
                                model_name = val
                            label = Paragraph(escape(data['name']), style)
                            value = Paragraph(escape(str(val)), style)
                            table_data = [label, value]
                            rows.append(table_data)

        response = HttpResponse(content_type='application/pdf')
        pdf_savetime = datetime.datetime.now()
        filename = model_name + " " + pdf_savetime.strftime("%Y-%m-%d %H:%M") + ".pdf"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        doc = SimpleDocTemplate(response, pagesize=letter)
        p = canvas.Canvas(response)
        t = Table(rows, repeatRows=0)
        t.setStyle(TableStyle(get_table_style()))
        elements.append(t)
        doc.build(elements)
        return response


def get_paragraph_style():
    paragraph_style = ParagraphStyle(
        name='Note',
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor='black'
    )
    return paragraph_style


def get_header_style():
    paragraph_style = ParagraphStyle(
        name='Note',
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor='black',
        spaceBefore=10,
        spaceAfter=20,
    )
    return paragraph_style


def get_table_style():
    padding = 4
    table_style = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        # ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]
    return table_style


@login_required()
@render_response()
def get_history_data(request, conn=None, **kwargs):
    """ Get history information related to experimental data.
        Displays all the versions of experimental data.
        Compare two versions of experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/history_data.html'
    context = {
        'template': template_name
    }
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
        context['input_id'] = input_id
    if 'dataset' in request.GET:
        datasetId = int(request.GET.get('dataset', -1))
    input_data = None
    if input_id and input_type:
        history = experimentController.get_history(conn, input_type, input_id)
    if request.method == 'GET':
        context['input_type'] = input_type
        context['history'] = history
        return context

    if request.method == 'POST':
        selected_rlobject_ids = request.POST.getlist('versions')
        model_sections = experimentController.get_sections_from_model(conn, input_type)
        compared_versions = experimentController.get_difference_of_rlobjects(conn, input_type,
                                                                             int(selected_rlobject_ids[0]),
                                                                             int(selected_rlobject_ids[1]))

        context['history'] = history
        context['input_type'] = input_type
        context['input_id'] = input_id
        context['rlobject_difference'] = compared_versions
        context['sections'] = model_sections
        return context

def get_images_from_dataset(conn, datasetId):
    dataset = conn.getObject("Dataset", datasetId)
    imageIds = []
    if dataset:
        for image in dataset.listChildren():
            imageIds.append(image.getId())
    return imageIds


@login_required()
@render_response()
def semantic_search(request, conn=None, **kwargs):
    template_name = 'Experiment/Views/launch_semantic_search.html'
    context = {
        'template': template_name
    }
    if request.method == 'GET':
        return context


@login_required()
@render_response()
def semantic_search_experiment(request, conn=None, **kwargs):
    """ Search all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/semantic_search_experiment.html'
    context = {
        'template': template_name
    }
    if request.method == 'GET':
        return context

    if request.method == 'POST':
        sparql_query_text = request.POST.get('sparql_query_text')
        query_number = request.POST.get('sparql_query')
        if sparql_query_text:
            query = sparql_query_text
        if query_number:
            query = semanticSearch.get_sparql_query(int(query_number))
        results = semanticSearch.get_sparql_query_results(query)
        semantic_search_results = results
        if len(semantic_search_results) > 0:
            context['search_results'] = semantic_search_results
            context['query'] = query
        else:
            context['message'] = "No results found"
    context['template'] = template_name
    return context


@login_required()
@render_response()
def view_script_data(request, conn=None, **kwargs):
    """ View all information related to experimental data
        @param request Request
        @param conn OMERO gateway
        @param kwargs Request Args
    """
    template_name = 'Experiment/Views/view_script_data.html'
    context = {
        'template': template_name
    }
    if 'input_type' in request.GET:
        input_type = str(request.GET.get('input_type', None))
    if 'id' in request.GET:
        id = request.GET.get('id', None)
        input_id = int(id) if id else -1
    if input_id and input_type:
        query = "SELECT DISTINCT  ?trial_id ?TrialStartTime ?TrialEndTime ?ProgrammingLanguageName ?ProgrammingLanguageVersion ?OS ?OSVersion ?ExecutionDirectory  {?trial a :Trial . ?trial prov:value ?trial_id FILTER(?trial_id='1'^^xsd:integer) .  ?trial prov:influenced ?environ . ?environ :name ?EnvironmentAttributeName . ?environ prov:value ?EnvironmentAttributeValue . ?trial prov:startedAtTime ?TrialStartTime .  ?trial prov:endedAtTime ?TrialEndTime . ?os a :OperatingSystem . ?os :name ?OS . ?os :version ?OSVersion .  ?trial prov:used ?os .  ?experimenter a :Experimenter . ?trial prov:wasStartedBy ?experimenter . ?experimenter :name ?ExperimenterName . ?pl a :ProgrammingLanguage . ?trial prov:used ?pl . ?pl :name ?ProgrammingLanguageName . ?pl :version ?ProgrammingLanguageVersion . ?trial prov:atLocation ?ExecutionDirectory }  "
        results = semanticSearch.get_sparql_query_results(query)
        context['results'] = results
        return context


def get_instances(request, conn=None, **kwargs):
    if request.is_ajax():
        q = request.GET.get('term', '')
        query = "SELECT DISTINCT ?type WHERE { ?thing a ?type . } ORDER BY ?type"
        instances = semanticSearch.get_sparql_query_results(query)
        data = semanticSearch.get_autocomplete_data(instances)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def get_properties(request, conn=None, **kwargs):
    if request.is_ajax():
        q = request.GET.get('term', '')
        class_value = request.GET.get('class_value', '')
        query = "Select DISTINCT ?property where { ?item a :" + class_value + " . ?item ?property ?obj  }"
        instances = semanticSearch.get_sparql_query_results(query)
        data = semanticSearch.get_autocomplete_data(instances)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
