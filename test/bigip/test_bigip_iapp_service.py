#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017 F5 Networks Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch, Mock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from library import bigip_iapp_service as mut
from library.bigip_iapp_service import (
    F5AnsibleModule,
    ModuleManager
)


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except:
        pass

    fixture_data[path] = data
    return data


class TestBigipIappServiceModule(unittest.TestCase):

    def test_create_service_from_file(self):
        parameters = load_fixture('load_net_route_description.json')
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            template='f5.http',
            parameters=parameters
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        obj.exists = lambda: False
        obj.create_on_device = lambda x: True
        obj.exit_json = lambda x: True
        results = obj.apply_changes()

        assert results['changed'] is True
        assert results['reject'] == 'yes'
        assert results['partition'] == 'Common'

    def test_create_route_to_pool(self):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            destination='10.10.10.10',
            pool="test-pool"
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        obj.exists = lambda: False
        obj.create_on_device = lambda x: True
        obj.exit_json = lambda x: True
        results = obj.apply_changes()

        assert results['changed'] is True
        assert results['pool'] == 'test-pool'
        assert results['partition'] == 'Common'

    def test_create_route_to_vlan(self):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            destination='10.10.10.10',
            vlan="test-vlan"
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        obj.exists = lambda: False
        obj.create_on_device = lambda x: True
        obj.exit_json = lambda x: True
        results = obj.apply_changes()

        assert results['changed'] is True
        assert results['vlan'] == '/Common/test-vlan'
        assert results['partition'] == 'Common'

    def test_update_description(self):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            description='foo description'
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        current = load_fixture('load_net_route_description.json')
        obj.exists = lambda: True
        obj.update_on_device = lambda x: True
        obj.exit_json = lambda x: True
        obj.read_current_from_device = lambda x: current
        results = obj.apply_changes()

        assert results['changed'] is True
        assert results['description'] == 'foo description'
        assert results['partition'] == 'Common'

    def test_update_description_idempotent(self):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            description='asdasd'
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        current = load_fixture('load_net_route_description.json')
        obj.exists = lambda: True
        obj.update_on_device = lambda x: True
        obj.exit_json = lambda x: True
        obj.read_current_from_device = lambda x: current
        results = obj.apply_changes()

        # There is no assert for the description, because it should
        # not have changed
        assert results['changed'] is False
        assert results['partition'] == 'Common'

    def test_delete(self):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='absent'
        ))
        mut._CONNECTION = True

        module = F5AnsibleModule()
        obj = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        obj.exists = Mock()
        obj.exists.side_effect = [True, False]
        obj.remove_from_device = lambda: True
        obj.exit_json = lambda x: True
        results = obj.apply_changes()

        assert results['changed'] is True
        assert 'description' not in results

    @patch('library.bigip_static_route.F5AnsibleModule.fail_json')
    def test_invalid_unknown_params(self, mock_module):
        set_module_args(dict(
            name='test-route',
            password='admin',
            server='localhost',
            user='admin',
            state='present',
            foo="bar"
        ))
        mut._CONNECTION = True
        module = F5AnsibleModule()
        assert module.fail_json.call_count == 1