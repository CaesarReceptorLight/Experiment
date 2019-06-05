#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.forms import widgets
import logging


class RichTextWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Textarea(attrs={'class': 'scientifickeyboard', 'rows': 3, 'cols': 39}),
            # forms.FileInput(attrs={'class':'file_input'}),
            forms.ClearableFileInput(attrs={'class':'file_input', 'multiple': True}),
        )
        super(RichTextWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, None]
        return [None, None]
    def format_output(self, rendered_widgets):
        return u'\n'.join(rendered_widgets)


class RichTextField(forms.MultiValueField):
    def __init__(self, required=True, widget=None, label=None, initial=None, help_text=None):
        fields = (
            forms.CharField(),
            forms.FileField(),
        )
        super(RichTextField, self).__init__(fields, required,
                                           widget, label, initial, help_text)

    def compress(self, data_list):
        if data_list:
            return data_list
        return None
