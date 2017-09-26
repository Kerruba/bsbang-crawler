#!/usr/bin/env python3

import bs4
import canonicaljson
import hashlib
import json
import requests
# import uuid

# namespaceUuid = uuid.UUID('734bf6c4-c123-412e-981f-b867570a369f')
solrPath = 'http://localhost:8983/solr/bsbang-dev-core/'
solrJsonDocUpdatePath = solrPath + 'update/json/docs'

# MAIN
r = requests.get('http://localhost:8080/synbiomine/report.do?id=2026346')
soup = bs4.BeautifulSoup(r.text, 'html.parser')
tags = soup.find_all('script', type='application/ld+json')
print('Found %d ld+json sections' % len(tags))

jsonlds = []

for tag in tags:
    jsonlds.append(json.loads(tag.string))

headers = {'Content-type': 'application/json'}

for jsonld in jsonlds:
    # jsonld['id'] = str(uuid.uuid5(namespaceUuid, json.dumps(jsonld)))
    # TODO: Use solr de-dupe for this
    jsonld['id'] = hashlib.sha256(canonicaljson.encode_canonical_json(jsonld)).hexdigest()
    print(jsonld)
    r = requests.post(solrJsonDocUpdatePath + '?commit=true', json=jsonld, headers=headers)
    print(r.text)
