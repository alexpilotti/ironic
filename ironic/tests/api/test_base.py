# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from webob import exc

from ironic.api.controllers import base as cbase
from ironic.tests.api import base


class TestBase(base.FunctionalTest):

    def test_api_setup(self):
        pass

    def test_bad_uri(self):
        response = self.get_json('/bad/path',
                                 expect_errors=True,
                                 headers={"Accept": "application/json"})
        self.assertEqual(404, response.status_int)
        self.assertEqual("application/json", response.content_type)
        self.assertTrue(response.json['error_message'])


class TestVersion(base.FunctionalTest):

    @mock.patch('ironic.api.controllers.base.Version.parse_headers')
    def test_init(self, mock_parse):
        a = mock.Mock()
        b = mock.Mock()
        mock_parse.return_value = (a, b)
        v = cbase.Version('test', 'foo', 'bar')

        mock_parse.assert_called_with('test', 'foo', 'bar')
        self.assertEqual(a, v.major)
        self.assertEqual(b, v.minor)

    @mock.patch('ironic.api.controllers.base.Version.parse_headers')
    def test_repr(self, mock_parse):
        mock_parse.return_value = (123, 456)
        v = cbase.Version('test', mock.ANY, mock.ANY)
        result = "%s" % v
        self.assertEqual('123.456', result)

    @mock.patch('ironic.api.controllers.base.Version.parse_headers')
    def test_repr_with_strings(self, mock_parse):
        mock_parse.return_value = ('abc', 'def')
        v = cbase.Version('test', mock.ANY, mock.ANY)
        result = "%s" % v
        self.assertEqual('abc.def', result)

    def test_parse_headers_ok(self):
        version = cbase.Version.parse_headers(
                {cbase.Version.string: '123.456'}, mock.ANY, mock.ANY)
        self.assertEqual((123, 456), version)

    def test_parse_headers_latest(self):
        for s in ['latest', 'LATEST']:
            version = cbase.Version.parse_headers(
                    {cbase.Version.string: s}, mock.ANY, '1.9')
            self.assertEqual((1, 9), version)

    def test_parse_headers_bad_length(self):
        self.assertRaises(exc.HTTPNotAcceptable,
                cbase.Version.parse_headers,
                {cbase.Version.string: '1'},
                mock.ANY,
                mock.ANY)
        self.assertRaises(exc.HTTPNotAcceptable,
                cbase.Version.parse_headers,
                {cbase.Version.string: '1.2.3'},
                mock.ANY,
                mock.ANY)

    def test_parse_no_header(self):
        # this asserts that the minimum version string of "1.1" is applied
        version = cbase.Version.parse_headers({}, '1.1', '1.5')
        self.assertEqual((1, 1), version)
