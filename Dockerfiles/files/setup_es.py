#!/usr/bin/env python3

import requests
import json
from time import sleep

es_headers = {'Content-Type': 'application/json'}
kibana_headers = {'Content-Type': 'application/json', 'kbn-xsrf': 'true'}
cloudtrail_pattern = {
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

nginx_pattern = {
    "index_patterns": ["nginx-*"],
    "mappings": {
        "properties": {
            "geoip.location": {
                "type": "geo_point"
            }
        }
    }
}

def wait_for_es():
    keep_trying = True
    while keep_trying:
        try:
            requests.get('http://es03:9200/_cat/health', headers=es_headers)
            keep_trying = False
        except:
            print('[!] Elasticsearch not ready yet....waiting')
            sleep(15)

def load_index_settings():
    # Publish index mappings and settings
    print('[+] Adding Cloudtrail and Nginx index mappings and settings')
    r1 = requests.put('http://es03:9200/_template/cloudtrail', headers=es_headers, data=json.dumps(cloudtrail_pattern))
    r2 = requests.put('http://es03:9200/_template/nginx', headers=es_headers, data=json.dumps(nginx_pattern))
    print(r1)
    print(r2)

def load_exported_objects():
    print('[+] Adding exported objects')
    sleep(10)

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
