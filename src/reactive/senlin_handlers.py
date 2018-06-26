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

# this is just for the reactive handlers and calls into the charm.
from __future__ import absolute_import

import charms.reactive as reactive
import charmhelpers.core.hookenv as hookenv

import charms_openstack.charm as charm

# This charm's library contains all of the handler code associated with
# senlin -- we need to import it to get the definitions for the charm.
import charm.openstack.senlin as senlin  # noqa


# Use the charms.openstack defaults for common states and hooks
charm.use_defaults(
    'charm.installed',
    'amqp.connected',
    'shared-db.connected',
    'identity-service.connected',
    'identity-service.available',  # enables SSL support
    'config.changed',
    'update-status')


# Note that because of the way reactive.when works, (which is to 'find' the
# __code__ segment of the decorated function, it's very, very difficult to add
# other kinds of decorators here.  This rules out adding other things into the
# charm args list.  It is also CPython dependent.
@reactive.when('shared-db.available')
@reactive.when('identity-service.available')
@reactive.when('amqp.available')
def render_stuff(*args):
    """Render the configuration for Senlin when all the interfaces are
    available.

    Note that the HSM interface is optional and thus is only used if it is
    available.
    """
    hookenv.log("about to call the render_configs with {}".format(args))
    with charm.provide_charm_instance() as senlin_charm:
        senlin_charm.render_with_interfaces(args)
        senlin_charm.db_sync()
        senlin_charm.assess_status()
