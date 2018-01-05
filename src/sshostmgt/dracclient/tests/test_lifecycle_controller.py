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
from dracclient.resources import lifecycle_controller
from dracclient.resources import uris
from dracclient.tests import base
from dracclient.tests import utils as test_utils


class ClientLifecycleControllerManagementTestCase(base.BaseTest):

    def setUp(self):
        super(ClientLifecycleControllerManagementTestCase, self).setUp()
        self.drac_client = dracclient.client.DRACClient(
            **test_utils.FAKE_ENDPOINT)

    @requests_mock.Mocker()
    def test_get_lifecycle_controller_version(self, mock_requests):
        mock_requests.post(
            'https://1.2.3.4:443/wsman',
            text=test_utils.LifecycleControllerEnumerations[
                uris.DCIM_SystemView]['ok'])

        version = self.drac_client.get_lifecycle_controller_version()

        self.assertEqual((2, 1, 0), version)


class ClientLCConfigurationTestCase(base.BaseTest):

    def setUp(self):
        super(ClientLCConfigurationTestCase, self).setUp()
        self.drac_client = dracclient.client.DRACClient(
            **test_utils.FAKE_ENDPOINT)

    @requests_mock.Mocker()
    def test_list_lifecycle_settings(self, mock_requests):
        expected_enum_attr = lifecycle_controller.LCEnumerableAttribute(
            name='Lifecycle Controller State',
            instance_id='LifecycleController.Embedded.1#LCAttributes.1#LifecycleControllerState',  # noqa
            read_only=False,
            current_value='Enabled',
            pending_value=None,
            possible_values=['Disabled', 'Enabled', 'Recovery'])
        expected_string_attr = lifecycle_controller.LCStringAttribute(
            name='SYSID',
            instance_id='LifecycleController.Embedded.1#LCAttributes.1#SystemID',  # noqa
            read_only=True,
            current_value='639',
            pending_value=None,
            min_length=0,
            max_length=3)
        mock_requests.post('https://1.2.3.4:443/wsman', [
            {'text': test_utils.LifecycleControllerEnumerations[
                uris.DCIM_LCEnumeration]['ok']},
            {'text': test_utils.LifecycleControllerEnumerations[
                uris.DCIM_LCString]['ok']}])

        lifecycle_settings = self.drac_client.list_lifecycle_settings()

        self.assertEqual(14, len(lifecycle_settings))
        # enumerable attribute
        self.assertIn(
            'LifecycleController.Embedded.1#LCAttributes.1#LifecycleControllerState',  # noqa
            lifecycle_settings)
        self.assertEqual(expected_enum_attr, lifecycle_settings[
                         'LifecycleController.Embedded.1#LCAttributes.1#LifecycleControllerState'])  # noqa
        # string attribute
        self.assertIn(
            'LifecycleController.Embedded.1#LCAttributes.1#SystemID',
            lifecycle_settings)
        self.assertEqual(expected_string_attr,
                         lifecycle_settings['LifecycleController.Embedded.1#LCAttributes.1#SystemID'])  # noqa
