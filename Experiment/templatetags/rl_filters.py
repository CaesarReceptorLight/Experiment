#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Author: Sheeba Samuel, Friedrich-Schiller University, Jena
Email: caesar@uni-jena.de
Date created: 18.12.2017
'''
from django import template
import logging
import re

register = template.Library()


@register.filter
def display_richtext(value):
    finalrichText = value
    rl_object_pattern = "<<(.*?)>>"
    matches = re.compile(rl_object_pattern).findall(str(value))
    for match in matches:
        t=match.split(':')
        if len(t) == 3:
            if t[0] == 'File':
                file_object_pattern = "<<File:"+t[1] + ":" + re.escape(t[2]) + ">>"
                regex = re.compile(file_object_pattern)
                replc_val = '<a href="/Experiment/download_file/?fileId='+ t[1] +'">' + t[2] + '</a>'
                value = re.sub(regex, replc_val, value)
                finalrichText = value
            else:
                model_type = t[0]
                rl_object_pattern = "<<" + model_type + ":" + t[1] + ":" + re.escape(t[2]) + ">>"
                regex = re.compile(rl_object_pattern)
                if model_type.endswith('s'):
                    model_type = model_type[:-1]
                if model_type == 'RnaAmplifications' or model_type == 'RnaAmplification':
                    model_type = 'Rna'
                if model_type == 'DnaAmplifications' or model_type == 'DnaAmplification':
                    model_type = 'Dna'
                if model_type == 'Chemicals' or model_type == 'Chemical':
                    model_type = 'ChemicalSubstance'
                replc_val = '<a href="/Experiment/view_input_data/?input_type=' + model_type + '&id=' + t[1] + '"' + ' class="dialog_details view_tab">' + t[2].replace("%20", " ") + '</a><span></span>'
                value = re.sub(regex, replc_val, value)
                finalrichText = value

        else:
            finalrichText = value
    return finalrichText

@register.filter
def get_at_index(list, index):
    return list[index]