# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import requests_mock

import dracclient.client
from dracclient.resources import system
from dracclient.resources import uris
from dracclient.tests import base
from dracclient.tests import utils as test_utils


class ClientSystemConfigurationTestCase(base.BaseTest):

    def setUp(self):
        super(ClientSystemConfigurationTestCase, self).setUp()
        self.drac_client = dracclient.client.DRACClient(
            **test_utils.FAKE_ENDPOINT)

    @requests_mock.Mocker()
    def test_list_system_settings(self, mock_requests):
        expected_enum_attr = system.SystemEnumerableAttribute(
            name='ChassisLEDState',
            instance_id='System.Embedded.1#ChassisPwrState.1#ChassisLEDState',  # noqa
            read_only=False,
            current_value='Off',
            pending_value=None,
            fqdd='System.Embedded.1',
            group_id='ChassisPwrState.1',
            possible_values=['Unknown', 'Blinking', 'Off'])
        expected_string_attr = system.SystemStringAttribute(
            name='UserDefinedString',
            instance_id='System.Embedded.1#LCD.1#UserDefinedString',
            read_only=False,
            current_value=None,
            pending_value=None,
            fqdd='System.Embedded.1',
            group_id='LCD.1',
            min_length=0,
            max_length=62)
        expected_integer_attr = system.SystemIntegerAttribute(
            name='PowerCapValue',
            instance_id='System.Embedded.1#ServerPwr.1#PowerCapValue',
            read_only=False,
            current_value=555,
            pending_value=None,
            fqdd='System.Embedded.1',
            group_id='ServerPwr.1',
            lower_bound=302,
            upper_bound=578)

        mock_requests.post('https://1.2.3.4:443/wsman', [
            {'text': test_utils.SystemEnumerations[
                uris.DCIM_SystemEnumeration]['ok']},
            {'text': test_utils.SystemEnumerations[
                uris.DCIM_SystemString]['ok']},
            {'text': test_utils.SystemEnumerations[
                uris.DCIM_SystemInteger]['ok']}])

        system_settings = self.drac_client.list_system_settings()

        self.assertEqual(44, len(system_settings))
        # enumerable attribute
        self.assertIn('System.Embedded.1#ChassisPwrState.1#ChassisLEDState',
                      system_settings)
        self.assertEqual(expected_enum_attr, system_settings[
                         'System.Embedded.1#ChassisPwrState.1#ChassisLEDState'])  # noqa
        # string attribute
        self.assertIn('System.Embedded.1#LCD.1#UserDefinedString',
                      system_settings)
        self.assertEqual(expected_string_attr, system_settings[
                         'System.Embedded.1#LCD.1#UserDefinedString'])
        self.assertIn('System.Embedded.1#ServerPwr.1#PowerCapValue',
                      system_settings)
        self.assertEqual(expected_integer_attr,
                         system_settings['System.Embedded.1#ServerPwr.1#PowerCapValue'])  # noqa
