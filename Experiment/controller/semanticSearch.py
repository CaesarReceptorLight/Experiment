#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Author: Sheeba Samuel, Friedrich-Schiller University, Jena
Email: caesar@uni-jena.de
Date created: 15.08.2017
'''

import logging
import urllib
import httplib2
import subprocess
import os
import json
from SPARQLWrapper import SPARQLWrapper, N3, JSON


caesar_sparql_endpoint = SPARQLWrapper("http://localhost:8125/rdf4j-server/repositories/FederationStore_RL_OMERO")

def get_sparql_query_prefix():
    prefix = "PREFIX : <https://w3id.org/reproduceme#> " + \
             "PREFIX p-plan: <http://purl.org/net/p-plan#> " + \
             "PREFIX prov: <http://www.w3.org/ns/prov#>" +\
             "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
    return prefix

def get_sparql_query_results(sparql_query):
    prefix = get_sparql_query_prefix()
    query = prefix + sparql_query

    caesar_sparql_endpoint.setQuery(query)

    caesar_sparql_endpoint.setReturnFormat(JSON)
    results = caesar_sparql_endpoint.query().convert()
    if not results['results']['bindings']:
        return

    return results


def get_sparql_query(query_number):
    query_list = ["Select DISTINCT ?exp ?name  WHERE {?exp  a :Experiment . ?exp :name ?name }",
                  "Select ?Experiment ?Name ?AgentName ?AgentRole ?generatedTime WHERE { \
                    ?Experiment  a :Experiment ; :name ?Name . \
                    ?Experiment :status ?status FILTER(?status=1) . \
  		            ?Experiment  prov:wasAttributedTo ?Agent .   \
                    ?Agent :name ?AgentName ; rdfs:label ?AgentRole . \
                    OPTIONAL { ?Experiment prov:generatedAtTime ?generatedTime } \
                    }",
                  "Select *  WHERE {?vector a :Vector . ?vector ?p ?o}",
                  "Select *  WHERE {?vector a :Vector . ?vector prov:wasAttributedTo ?ContactPerson . ?ContactPerson :name ?ContactPersonName .  ?vector :storedAt ?VectorStorageLocation}",
                  "Select DISTINCT ?publication ?subplan ?Experiment WHERE { \
                    ?publication a :Publication . \
                    ?publication p-plan:isVariableOfPlan ?subplan . \
                    ?subplan p-plan:isSubPlanOfPlan ?exp . \
                    ?exp  a :Experiment ; :name ?Experiment ; :status ?status FILTER(?status=1) .\
                    }",
                    "SELECT DISTINCT ?Experiment ?step ?description WHERE { \
                    ?exp a :Experiment . \
                    ?exp :name ?Experiment . \
                    ?exp :status ?status FILTER(?status=1) .  \
                    ?subplan p-plan:isSubPlanOfPlan ?exp . \
                    { ?step p-plan:isStepOfPlan ?subplan } UNION {?step p-plan:isStepOfPlan ?subplan } \
                    ?step :description ?description \
                    }"
                  ]
    return query_list[query_number]


def get_autocomplete_data(instances):
    results = []
    for data in instances['results']['bindings']:
        for key, val in data.items():
            context = {}
            if val['type'] == 'uri':
                ontology_url = val['value']
                value = ontology_url.split("#")
                context['label'] = value[1]
                context['value'] = value[1]
                results.append(context)
        data = json.dumps(results)
    return data