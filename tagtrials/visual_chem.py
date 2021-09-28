# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CSIRO
#  +Author Bo Yan
#  +Email bo.yan@csiro.au
# Licensed under the MIT License

from datetime import datetime
import csv
import io

def generate_chembl_timeline_data(trial_tags, doc, context):
    '''
    chembls = set()
    for entry in context['trial_timeline']:
        for key in entry['trials']['chembl'].keys():
            chembls.add(key)
    '''
    identifiers = doc['data']['top200_identifiers']
    chembl_keys = []
    for idf in identifiers:
        for key in idf:
            chembl_keys.append(key)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # zenodo requires every file version is different. So timestamp is added as the first line in the csv file. 
    time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    writer.writerow([f'# created at {time_str}'])

    chembl_keys.insert(0,'date')
    writer.writerow(chembl_keys)
    chembl_keys.pop(0)
    for period in context['trial_timeline']:
        data_output = [period['start'].isoformat()]
        for key in chembl_keys:
            mentions = [x for x in period['trials'] if x.get('chembl_key', None) and (key in x['chembl_key'])]
            data_output.append( len(mentions) )
        writer.writerow(data_output)
    return output

def get_clusters(pubchem_id, context):
    if pubchem_id:
        exist = [x for x in context['pubchem_cluster'] if x['pubchem_id'] == pubchem_id]
        if len(exist)>0:
            return exist[0]['clusters']
    return None

def get_tooltip(pubchem_id, compound, chembl, size):
    content = ''
    if len(pubchem_id)>0:
        content += '<div class="tipimgdiv"><img src="https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=' + pubchem_id + '&amp;t=l" /></div>'
    content += '<p><strong>' + compound + ', ' + chembl 
    if len(pubchem_id)>0:
        content += ', ' + '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/' + pubchem_id + '" >PubChem-' + pubchem_id + '</a>'
    content += '</strong></p><p>Total number of clinical trials mentioning this compound: '
    content += str(size) + '</p>'
    return content

def generate_chembl_visual_data(trial_tags, doc, context):
    identifiers = doc['data']['top200_identifiers']
    chembl_dict_collection = context['chembl_dict_collection']
    pubchem_mapping = context['pubchem_mapping']
    unknown = {'name' : 'unknown', 'children' :[]}
    jobj = {'name': 'statistics', 'children' :[unknown]}
    
    for idf in identifiers:
        for key in idf:
            record = chembl_dict_collection.find_one({'key': key})
            if not record:
                print(f'ERROR: could not find the CHEMBL-ID {key} in the collection chembl_dict in the mongodb')
            else:
                compound = record['words'][0]
                pubchem_id = ""
                if key in pubchem_mapping.keys():
                    pubchem_id = pubchem_mapping[key]
                clusters = get_clusters(pubchem_id, context)
                size = idf[key]['trials']
                leaf = {'chembl':key, 'name':compound, 'size': size} 
                if len(pubchem_id)>0:
                    leaf['pubchem'] = pubchem_id
                leaf['tooltip'] = get_tooltip(pubchem_id, compound, key, size)
                if clusters:
                    for cltr in clusters:
                        l1obj = None
                        exist = [x for x in jobj["children"] if x['name'] == cltr]
                        if len(exist) > 0:
                            l1obj = exist[0]
                        else:
                            l1obj = {"name": cltr, "children": []}
                            jobj["children"].append(l1obj)
                        l1obj["children"].append(leaf)        
                else:
                    unknown["children"].append(leaf)                

    jobj['timestamp']= datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    return jobj

def generate_pdb_visual_data(trial_tags, doc, context):
    return None    

def generate_pubchem_visual_data(trial_tags, doc, context):
    return None