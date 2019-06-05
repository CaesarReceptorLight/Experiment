#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: Sheeba Samuel, Friedrich-Schiller University, Jena
Email: caesar@uni-jena.de
Date created: 04.08.2017
'''

from django import forms
import logging
from django.forms.extras.widgets import SelectDateWidget
from datetime import date
from datetime import datetime
from datetime import timedelta
from form_utils.forms import BetterForm, BetterModelForm
from django.forms.fields import FileField
from django.contrib import admin
from richText import RichTextField, RichTextWidget


def validate_datetime(date_value):
    try:
        if datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S"):
            return True
        else:
            return False
    except ValueError:
        return False


def initialise_fieldsets(fieldset):
    class CreateForm(BetterForm):
        class Meta:
            fieldsets = fieldset

        def __init__(self, *args, **kwargs):
            form_data = None
            if "form_data" in kwargs:
                form_data = kwargs.pop("form_data")
            if 'input_type' in kwargs:
                object_type = kwargs.pop("input_type")
            if 'experimenter_choices' in kwargs:
                experimenter_choices = kwargs.pop("experimenter_choices")
            super(CreateForm, self).__init__(*args, **kwargs)

            if form_data:
                for group, values in form_data.items():
                    for data in values:
                        if data and 'uiType' in data:
                            if data['isVisible'] == 'True':
                                if 'unit' in data and data['unit']:
                                    data['name'] = data['name'] + " (" + data['unit'] + ')'
                                if data['uiType'] == 'freeText':
                                    self.fields[data['key']] = forms.CharField(
                                        widget=forms.TextInput(attrs={'class': 'scientifickeyboard '}), required=False,
                                        initial=data[
                                            'value'] if 'value' in data else None,
                                        label=data['name'],
                                        help_text=data['help'])
                                    self.fields[data['key']].input_type = data['uiType']
                                elif data['uiType'] == 'Textarea':
                                    self.fields[data['key']] = forms.CharField(
                                        widget=forms.Textarea(attrs={'class': 'scientifickeyboard ', 'rows': 3, 'cols': 39}), required=False,
                                        initial=data[
                                            'value'] if 'value' in data else None,
                                        label=data['name'],
                                        help_text=data['help'])
                                    self.fields[data['key']].input_type = data['uiType']
                                elif data['uiType'] == 'date':
                                    if 'value' in data and data['value']:
                                        if validate_datetime(data['value']):
                                            initial_date = data['value']
                                        else:
                                            date_value = datetime.strptime(data['value'], '%Y-%m-%d')
                                            initial_date = date_value + timedelta(hours=0, minutes=0)
                                    self.fields[data['key']] = forms.DateTimeField(
                                        widget=forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
                                        label=data['name'], input_formats=['%Y-%m-%d %H:%M:%S'],
                                        initial=initial_date if 'value' in data and data['value'] else date.today,
                                        help_text=data['help'])
                                    self.fields[data['key']].input_type = data['uiType']
                                elif data['uiType'] == 'time':
                                    self.fields[data['key']] = forms.TimeField(required=False, help_text=data['help'],
                                                                               widget=forms.widgets.TimeInput(
                                                                                   attrs={'class': 'timepicker'}),
                                                                               initial=data[
                                                                                   'value'] if 'value' in data and data[
                                                                                   'value'] else datetime.now)
                                elif data['uiType'] == 'richText':
                                    self.fields[data['key']] = RichTextField(required=False, widget=RichTextWidget(),
                                                                             label=data['name'], initial=data[
                                            'value'] if 'value' in data else None, help_text=data['help'])

                                    self.fields[data['key']].input_type = data['uiType']
                                elif data['uiType'] == 'weblink':
                                    self.fields[data['key']] = forms.CharField(required=False,
                                                                               initial=data[
                                                                                   'value'] if 'value' in data else None,
                                                                               label=data['name'],
                                                                               help_text=data['help'])
                                elif data['uiType'] == 'file':
                                    self.fields[data['key']] = forms.FileField(required=False,
                                                                               label=data['name'],
                                                                               help_text=data['help'])
                                elif data['uiType'] == 'multiplefiles':
                                    self.fields[data['key']] = forms.FileField(
                                        widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                        required=False,
                                        label=data['name'],
                                        help_text=data['help'])
                                elif data['uiType'] == 'dropdown':
                                    ids = None
                                    if 'value' in data and data['value']:
                                        ids = data['value'].split(",")
                                    self.fields[data['key']] = forms.MultipleChoiceField(choices=experimenter_choices,
                                                                                         required=False,
                                                                                         initial=[key_id for key_id in
                                                                                                  ids] if ids and 'value' in data else None,
                                                                                         label=data['name'],
                                                                                         help_text=data['help'])
                                else:
                                    logging.info("Unknown datatype:(%s)", data['uiType'])

    return CreateForm
