#! /usr/bin/env python
#
# Mixpanel, Inc. -- http://mixpanel.com/
#
# Python API client library to consume mixpanel.com analytics data.
#
# Copyright 2010-2013 Mixpanel, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import urllib.request

try:
    import json
except ImportError:
    import simplejson as json

class Mixpanel(object):

    ENDPOINT = 'https://data.mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, api_secret):
        self.api_secret = api_secret

    def request(self, methods, params, http_method='GET', format='json'):
        """
            methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
                      will give us http://mixpanel.com/api/2.0/events/properties/values/
            params - Extra parameters associated with method
        """

        request_url = '/'.join([self.ENDPOINT, str(self.VERSION)] + methods)
        if http_method == 'GET':
            data = None
            request_url = request_url + '/?' + self.unicode_urlencode(params)
        else:
            data = self.unicode_urlencode(params)

        auth = base64.b64encode(bytes(self.api_secret, 'UTF-8')).decode("ascii")
        headers = {'Authorization': 'Basic {encoded_secret}'.format(encoded_secret=auth)}

        request = urllib.request.Request(request_url, data, headers)
        response = urllib.request.urlopen(request, timeout=120)
        str_response = response.read().decode('utf8')
        lines = str_response.splitlines(True)
        records = []
        for line in lines:
            obj = json.loads(line)
            records.append(obj)
        return records

    def unicode_urlencode(self, params):
        """
            Convert lists to JSON encoded strings, and correctly handle any
            unicode URL parameters.
        """
        if isinstance(params, dict):
            params = list(params.items())
        for i,param in enumerate(params):
            if isinstance(param[1], list):
                params.remove(param)
                params.append ((param[0], json.dumps(param[1]),))

        return urllib.parse.urlencode(
            [(k, v) for k, v in params]
        )

if __name__ == '__main__':
    encoded_secret = b'REPLACE_ME'
    api = Mixpanel(api_secret=encoded_secret)
    data = api.request(['export'], {
        'event': ['Product-Detail-View'],
        'to_date': "2016-06-16",
        'from_date': "2016-05-31"
    })
    print (json.dumps(data, indent=4))
