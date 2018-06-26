# Copyright 2018 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# The nova_cell_controller handlers class

# bare functions are provided to the reactive handlers to perform the functions
# needed on the class.
from __future__ import absolute_import

import collections
import subprocess

import charmhelpers.core.hookenv as hookenv

import charms_openstack.charm
import charms_openstack.adapters
import charms_openstack.ip as os_ip

PACKAGES = ['senlin-api', 'senlin-common', 'senlin-engine', 'python-pymysql']
SENLIN_DIR = '/etc/senlin/'
SENLIN_CONF = SENLIN_DIR + "senlin.conf"
SENLIN_API_PASTE_CONF = SENLIN_DIR + "api-paste.ini"

OPENSTACK_RELEASE_KEY = 'senlin.openstack-release-version'


# select the default release function
charms_openstack.charm.use_defaults('charm.default-select-release')


class NovaCellControllerCharm(charms_openstack.charm.HAOpenStackCharm):
    """NovaCellControllerCharm provides the specialisation of the OpenStackCharm
    functionality to manage a nova_cell_controller unit.
    """

    release = 'mitaka'
    name = 'senlin'
    packages = PACKAGES
    service_type = 'senlin'
    default_service = 'senlin-api'
    services = ['senlin-api', 'senlin-engine']

    # Note that the hsm interface is optional - defined in config.yaml
    required_relations = ['shared-db', 'amqp']

    restart_map = {
        SENLIN_CONF: services,
        SENLIN_API_PASTE_CONF: services,
    }

    api_ports = {
        'senlin-api': {
            os_ip.PUBLIC: 8778,
            os_ip.ADMIN: 8778,
            os_ip.INTERNAL: 8778,
        }
    }

    # Package for release version detection
    release_pkg = 'senlin'

    # Package codename map for nova-common
    package_codenames = {
        'nova-common': collections.OrderedDict([
            ('1', 'mitaka'),
            ('2', 'newton'),
            ('3', 'ocata'),
            ('4', 'pike'),
            ('5', 'queens'),
            ('6', 'rocky'),
        ]),
    }

    sync_cmd = ['senlin-manage', 'db_sync']

    ha_resources = ['vips', 'haproxy', 'dnsha']


    def get_amqp_credentials(self):
        """Provide the default amqp username and vhost as a tuple.

        :returns (username, host): two strings to send to the amqp provider.
        """
        return ('senlin', 'openstack')

    def get_database_setup(self):
        """Provide the default database credentials as a list of 3-tuples

        returns a structure of:
        [
            {'database': <database>,
             'username': <username>,
             'hostname': <hostname of this unit>
             'prefix': <the optional prefix for the database>, },
        ]

        :returns [{'database': ...}, ...]: credentials for multiple databases
        """
        return [{'username': 'senlin', 'database': 'senlin'}]


    def states_to_check(self, required_relations=None):
        """Override the default states_to_check() for the assess_status
        functionality so that, if we have to have an HSM relation, then enforce
        it on the assess_status() call.

        If param required_relations is not None then it overrides the
        instance/class variable self.required_relations.

        :param required_relations: [list of state names]
        :returns: [states{} as per parent method]
        """
        if required_relations is None:
            required_relations = self.required_relations
        return super(NovaCellControllerCharm, self).states_to_check(
            required_relations=required_relations)
