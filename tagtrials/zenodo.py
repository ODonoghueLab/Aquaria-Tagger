# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 CSIRO
#  +Author Bo Yan
#  +Email bo.yan@csiro.au
# Licensed under the MIT License


import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def publish_to_zenodo(zenodo_url, recid, token, files, version = None):
    ''' Publish files to zenodo repository.
    
    :param zenodo_url: "https://sandbox.zenodo.org/api" or "https://zenodo.org/api"
    :param doi: the destination record id, such as 541234
    :param token: the access token to write to zenodo repository
    :param files: a list of filename and content pair to upload.  
    :param version: the new version string, such as 1.0.1, or 2021.09.20
    '''
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    params = {'access_token': token}
    
    logger.info(f'start uploading and publishing to zenodo for record {recid}')
    logger.info(f'\tto the zenodo url {zenodo_url}')
    # first, check the status of this repository
    r = requests.get(f'{zenodo_url}/deposit/depositions/{recid}', headers=headers)
    if not r.ok:
        raise r.raise_for_status()

    rj_links = r.json()['links']
    draft_url =  rj_links.get('latest_draft', None) 
    if not draft_url:
        # switch to the latest version
        latest_url = rj_links['latest']
        latest_doi = get_doi_from_record_link(latest_url, zenodo_url)
        r = requests.get(f'{zenodo_url}/deposit/depositions/{latest_doi}', headers=headers)
        if not r.ok:
            raise r.raise_for_status()
        rj_links = r.json()['links']
        # create draft from the latest version 
        draft_url = create_new_draft(rj_links['newversion'], params)
    # switch to draft
    logger.info('\tchange to draft version')
    r = requests.get(draft_url, headers=headers)
    if not r.ok:
        raise r.raise_for_status()
    rj = r.json()
    rj_files = rj['files']
    metadata = rj['metadata']

    # delete all the old files!
    logger.info('\tdelete old files from draft')
    for f in rj_files:
        of_id = f['id']
        of_url = f'{draft_url}/files/{of_id}'
        print ( f'deleting old file: {of_url}' )
        r = requests.delete(of_url, params=params)
        if not r.ok:
            raise r.raise_for_status()

    # upload new files
    logger.info('\tupload new files')
    draft_files = f'{draft_url}/files'
    upload_url = f'{draft_files}?access_token={token}'
    for nf in files:
        data = {'name': nf['filename']}
        r = requests.post(upload_url, data=data, files={'file': nf['content']})
        if not r.ok:
            raise r.raise_for_status()
    
    # update the new version in metadata
    if version:
        metadata['version'] = version
        r = requests.put( draft_url, headers=headers, data = json.dumps({'metadata': metadata}) )
        if not r.ok:
            raise r.raise_for_status()

    # publish
    logger.info('\tstart publishing')
    r = requests.post(f'{draft_url}/actions/publish', headers=headers)
    if not r.ok:
        raise r.raise_for_status()
    logger.info('Publish successfully!')

def get_doi_from_record_link(rec_url, zenodo_url):
    # get '917028' from 'https://sandbox.zenodo.org/api/records/917028'
    return rec_url[len(zenodo_url) + len('/records/'):]

def create_new_draft(nv_url, params):
    logger.info('\tcreate a new draft version')
    r = requests.post(nv_url, params=params)
    if not r.ok:
        raise r.raise_for_status()
    return r.json()['links']['latest_draft']
