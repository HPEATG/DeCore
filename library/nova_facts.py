#!/usr/bin/python

# vim: ts=4:expandtab:au BufWritePost
# (c) 2014 Patrick "CaptTofu" Galbraith <patg@patg.net> 
# Code also from rax_facts, docker_facts and the primary nova module
#
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

# This is a DOCUMENTATION stub specific to this module, it extends
# a documentation fragment located in ansible.utils.module_docs_fragments
DOCUMENTATION = '''
---
module: nova_facts
short_description: Gather facts for Nova instances and images
description:
     - Gather facts for Nova instances and images
version_added: "0.1"
options:
  id:
    description:
      - instance ID to retrieve facts for
    default: null (all instances if neither name nor id specified)
  name:
    description:
      - instance name to retrieve facts for
    default: null (all instances if neither name nor id specified)
  address:
    description
      - instance address, internal or external (floating) to retrieve
        facts for
    default: null
  images:
    description:
      - image id, name or 'all'. Off by default.
    default: null
author: Patrick Galbraith
'''

EXAMPLES = '''
- name: Gather info about instances
  hosts: localhost
  gather_facts: False
  tasks:
    - name: Get facts about instance with id 123
      local_action:
        login_username: galt
        login_password: starnesville
        login_tenant_name: galt-project1
        auth_url: https://region-b.geo-1.identity.hpcloudsvc.com:35357/v2.0/
        region_name: region-b.geo-1
        module: nova_facts
        id: f062f85b-5586-479a-b6a2-647385b04715
        key_name: test
        wait_for: 200
        security_groups: default

    - name: Get facts about instance with ip adress of 10.0.0.102
      local_action:
        module: nova_facts
        address: 10.0.0.102

- name: Gather info about all instances and images
  hosts: nova
  gather_facts: True
  tasks:
    - name: Get facts about instances
      local_action:
        module: nova_facts
        images: all

    - name: instances debug info
      debug: msg="Instance Name {{ item.key }}"
      with_dict: nova_instances

    - name: images info
      debug: msg="Image ID {{ item.key }} Name {{ item.value.nova_name }}"
      with_dict: nova_images

'''

from types import NoneType

HAS_NOVA_CLIENT = True
NON_CALLABLES = (basestring, bool, dict, int, list, NoneType)

try:
    from novaclient.v1_1 import client as nova_client
    from novaclient import exceptions
except ImportError:
    HAS_NOVA_CLIENT = False
    print("failed=True msg='novaclient is required for this module'")


class NovaFacts:

    def __init__(self, module):
        self.module = module
        self.name = module.params.get('name')
        self.id = module.params.get('id')
        self.address = module.params.get('address')
        self.images = module.params.get('images')

        self.nova = nova_client.Client(module.params['login_username'],
                                       module.params['login_password'],
                                       module.params['login_tenant_name'],
                                       module.params['auth_url'],
                                       region_name=
                                       module.params['region_name'],
                                       service_type='compute')
        try:
            self.nova.authenticate()
        except exceptions.Unauthorized, e:
            module.fail_json(msg="Invalid OpenStack Nova credentials.: %s" %
                             e.message)
        except exceptions.AuthorizationFailure, e:
            module.fail_json(msg="Unable to authorize user: %s" % e.message)

        if self.nova is None:
            module.fail_json(msg="Failed to instantiate nova client. This "
                                 "could mean that your credentials are wrong.")

    def key_cleanup(self, value):
        return 'nova_%s' % (re.sub('[^\w-]', '_', value).lower().lstrip('_'))

    def get_priv_pub(self, obj):
        priv_pub = {'ipv4_public' : None}
        private = [net['addr']
                   for net in
                   getattr(obj, 'addresses').itervalues().next()
                   if 'OS-EXT-IPS:type'
                   in net and net['OS-EXT-IPS:type'] == 'fixed']
        priv_pub['ipv4_private'] = private[0] 
        public = [net['addr']
                  for net in
                  getattr(obj, 'addresses').itervalues().next()
                  if 'OS-EXT-IPS:type'
                  in net and net['OS-EXT-IPS:type'] == 'floating']
        if public is not None and len(public) > 0:
            priv_pub['ipv4_public'] = public[0]

        return priv_pub 

    def object_to_dict(self, obj):
        instance = {}
        for key in dir(obj):
            value = getattr(obj, key)
            if key == 'manager':
                next
            if (isinstance(value, NON_CALLABLES) and not key.startswith('_')):
                key = self.key_cleanup(key)
                instance[key] = value
        instance.update(self.get_priv_pub(obj))
        return instance

    def object_list_to_dict(self, object_list, name):
        dicts = {}
        for obj in object_list:
            dictn = self.object_to_dict(obj)
            if name is not None and \
               name != dictn['nova_name']:
                    next
            else:
                dicts[dictn['nova_name']] = dictn

        return dicts

    def get_instances(self):
        instance_obj_list = []
        instances_dict = {}

        # with id, get() can be used, otherwise name will be used in
        # excluding non matches
        if (self.id is not None):
            try:
                instance_obj_list.append(self.nova.servers.get(self.id))
            except Exception, e:
                module.fail_json(msg='%s' % e.message)
        else:
            try:
                instance_obj_list = self.nova.servers.list()
            except Exception, e:
                module.fail_json(msg='%s' % e.message)

        instances_dict = self.object_list_to_dict(instance_obj_list, self.name)

        # this is specific to instances, hence not in object_list_to_dict()
        if self.address is not None:
            for iname, instance_dict in instances_dict.iteritems():
                for netname, networks in \
                        instance_dict['nova_networks'].iteritems():
                    for address in networks:
                        if self.address == address:
                            instances_dict = {iname: instances_dict[iname]}

        return instances_dict

    def get_images(self):
        images_dict = {}
        image_obj_list = []
        image_id = None
        if self.images != 'all':
            image_id = self.images
            try:
                image_obj_list.append(self.nova.images.get(image_id))
            except Exception, e:
                module.fail_json(msg='%s' % e. message)
        else:
            try:
                image_obj_list = self.nova.images.list()
            except Exception, e:
                module.fail_json(msg='%s' % e. message)

        images_dict = self.object_list_to_dict(image_obj_list, image_id)

        return images_dict

    def nova_facts(self, module):
        changed = False
        facts = {}

        # get all instances
        facts['nova_instances'] = self.get_instances()

        # if instances specified, get them too
        if self.images:
            facts['nova_images'] = self.get_images()

        module.exit_json(changed=changed, ansible_facts=facts)


def main():
    if not HAS_NOVA_CLIENT:
        module.fail_json(msg=
                         'The nova python client is required \
                         for this module')
    argument_spec = dict(
        id=dict(default=None),
        name=dict(default=None),
        address=dict(default=None),
        images=dict(default=None),
        login_username=dict(default='admin'),
        login_password=dict(required=True),
        login_tenant_name=dict(required='True'),
        auth_url=dict(default='http://127.0.0.1:35357/v2.0/'),
        region_name=dict(default=None),
        image_id=dict(default=None),
        flavor_id=dict(default=1),
        key_name=dict(default=None),
        security_groups=dict(default='default'),
        nics=dict(default=None),
        meta=dict(default=None),
        wait=dict(default='yes', choices=['yes', 'no']),
        wait_for=dict(default=180),
        state=dict(default='present', choices=['absent', 'present']),
        user_data=dict(default=None)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[['id', 'name']]
    )

    manager = NovaFacts(module)

    manager.nova_facts(module)

# import module snippets
from ansible.module_utils.basic import *

### invoke the module
main()
