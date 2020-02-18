#!/usr/bin/env python3

import requests
import json
from time import sleep

es_headers = {'Content-Type': 'application/json'}
kibana_headers = {'Content-Type': 'application/json', 'kbn-xsrf': 'true'}
pattern = {
    "index_patterns": ["cloudtrail-*"],
    "settings" : {
        "index.mapping.total_fields.limit" : "2000"
    },
    "mappings": {
        "properties": {
            "geoip": {
                "type": "geo_point"
            },
            "apiVersion" : {
                "type" : "text"
            }
        }
    }
}

def wait_for_es():
    keep_trying = True
    while keep_trying:
        try:
            requests.get('http://elasticsearch:9200/_cat/health', headers=es_headers)
            keep_trying = False
        except:
            print('[!] Elasticsearch not ready yet....waiting')
            sleep(5)

def load_index_settings():
    # Publish index mappings and settings
    print('[+] Adding Cloudtrail index mappings and settings')
    r = requests.put('http://elasticsearch:9200/_template/cloudtrail', headers=es_headers, data=json.dumps(pattern))
    print(r)

def load_exported_objects():
    print('[+] Adding exported objects')
    sleep(5)

    # Read export.json
    with open('export.json', 'r') as f:
        export_json = json.loads(f.read())

    # Fix JSON body to expected values
    id_default_index = ""
    for o in export_json['objects']:
        if o['type'] == 'index-pattern':
            id_default_index = o['id']

    # Upload export
    r = requests.post('http://kibana:5601/api/kibana/dashboards/import', headers=kibana_headers, data=json.dumps(export_json))
    print(r)

    # Set default index pattern
    print('[+] Setting default index pattern')
    r = requests.post('http://kibana:5601/api/kibana/settings/defaultIndex', headers=kibana_headers, data=json.dumps({"value": id_default_index}))
    print(r)

if __name__ == '__main__':
    wait_for_es()
    load_index_settings()
    load_exported_objects()
