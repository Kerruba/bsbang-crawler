import os

import bs4
import json
import requests
from requests_testadapter import Resp
from bioschemas_lib import MANDATORY_PROPERTIES, SCHEMA_INHERITANCE_GRAPH, SCHEMAS_TO_PARSE


class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        return self.build_response_from_file(request)


class BioschemasParser:
    def __init__(self):
        self.config = {
            'mandatory_properties': MANDATORY_PROPERTIES,
            'schema_inheritance_graph': SCHEMA_INHERITANCE_GRAPH,
            'schemas_to_parse': SCHEMAS_TO_PARSE
        }

    def assert_mandatory_jsonld_properties(self, schema, jsonld):
        # print('Asserting schema %s' % schema)
        """Assert that the properties we require for a schema, and its parent schemas, exists in the jsonld"""
        if schema in self.config['mandatory_properties']:
            for prop in self.config['mandatory_properties'][schema]:
                if prop not in jsonld:
                    raise KeyError('Mandatory property %s not present for type %s' % (prop, type))

        parent_schema = self.config['schema_inheritance_graph'][schema]
        if parent_schema is not None:
            self.assert_mandatory_jsonld_properties(parent_schema, jsonld)

    def parse_bioschemas_jsonld_from_url(self, url):
        print('Loading page %s' % url)
        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        r = requests_session.get(url)
        return self.parse_bioschemas_jsonld_from_html(r.text)

    def parse_bioschemas_jsonld_from_html(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        ldjson_script_sections = soup.find_all('script', type='application/ld+json')
        print('Found %d ld+json sections' % len(ldjson_script_sections))

        jsonlds = []

        for ldjson_script_section in ldjson_script_sections:
            jsonlds.append(json.loads(ldjson_script_section.string))

        final_jsonlds = []

        for jsonld in jsonlds:
            try:
                if '@type' not in jsonld:
                    print('Ignoring as no @type present')
                    continue

                schema = jsonld['@type']
                if schema not in self.config['schemas_to_parse']:
                    print('Ignoring as %s is not a schema we are configured to parse' % type)

                self.assert_mandatory_jsonld_properties(schema, jsonld)
                final_jsonlds.append(jsonld)
            except KeyError as err:
                print('Ignoring %s as %s' % (jsonld, err))
                continue

        return final_jsonlds
