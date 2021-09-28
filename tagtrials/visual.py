# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CSIRO
#  +Author Bo Yan
#  +Email bo.yan@csiro.au
# Licensed under the MIT License


import json
import datetime

from zenodo import publish_to_zenodo
from visual_protein import generate_protein_visual_data
from visual_chem import generate_chembl_visual_data, generate_pdb_visual_data, generate_pubchem_visual_data, generate_chembl_timeline_data

SHA_SEARCH_AFTER = datetime.datetime(2021, 1, 1)
APP_SECTION = 'App'
ZENODO_SECTION = 'Zenodo'

def get_zenodo_config(context):
    config = context['config']
    token = config.get(ZENODO_SECTION, 'access_token')
    base_url = config.get(ZENODO_SECTION, 'zenodo_url')
    recid = config.get(ZENODO_SECTION, 'record_id')
    return base_url, recid, token 
    
def output_data_file(filepath, content):
    full_path = '/app/' + filepath
    with open(full_path, "w") as output_file:
        output_file.write( content )

def prepare_filename_content(fname, str):
    return {
        'filename' : fname,
        'content' : bytearray(str, encoding ='utf-8')
    }

def generate_visual_data(trial_tags, context):
    config = context['config']
    doclist = context['stat_collection'].find()
    files = []
    for doc in doclist:
        doc_name = doc['name']
        if doc_name == 'protein':
            v_data = generate_protein_visual_data(trial_tags, doc, context)
            if v_data:
                pcath_file = config.get(APP_SECTION, 'protein_cath_file')
                files.append(prepare_filename_content(pcath_file, json.dumps(v_data)))
        elif doc_name == 'chembl':
            v_data = generate_chembl_visual_data(trial_tags, doc, context)
            if v_data:
                chembl_cluster = config.get(APP_SECTION, 'chembl_cluster_file')
                files.append(prepare_filename_content(chembl_cluster, json.dumps(v_data)))
            csvdata = generate_chembl_timeline_data(trial_tags, doc, context)
            if csvdata:
                timeline_file = config.get(APP_SECTION, 'chembl_timeline_file')
                files.append(prepare_filename_content(timeline_file, csvdata.getvalue()))
        elif doc_name == 'pdb':
            generate_pdb_visual_data(trial_tags, doc, context)
        elif doc_name == 'pubchem':
            generate_pubchem_visual_data(trial_tags, doc, context)
        else:
            print (f'Error: unimplemented statistics for dictionary {doc_name}')
    base_url, recid, token = get_zenodo_config(context)
    version_str = datetime.datetime.now().strftime("%Y.%m.%d")
    publish_to_zenodo(base_url, recid, token, files, version_str)