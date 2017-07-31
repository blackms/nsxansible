#!/usr/bin/env python
# coding=utf-8
#
# Copyright � 2015 VMware, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__author__ = 'arocchi'


class BaseObject(object):
    def __init__(self, current_config):
        """

        :param current_config: current_config
        :type current_config: dict
        """
        self._current_config = current_config


def get_edge(client_session, edge_name):
    """
    :param client_session: An instance of an NsxClient Session
    :type client_session: NsxClient
    :param edge_name: The name of the edge searched
    :type edge_name: str
    :return: A tuple, with the first item being the edge or dlr id as string of the first Scope found with the
             right name and the second item being a dictionary of the logical parameters as return by the NSX API
    :rtype tuple
    """
    all_edge = client_session.read_all_pages('nsxEdges', 'read')

    try:
        edge_params = [scope for scope in all_edge if scope['name'] == edge_name][0]
        edge_id = edge_params['objectId']
    except IndexError:
        return None, None

    return edge_id, edge_params


def get_current_config(client_session, edge_id):
    response = client_session.read('routingConfig', uri_parameters={'edgeId': edge_id})
    return response['body']


def update_config(client_session, current_config, edge_id):
    client_session.update('routingConfig', uri_parameters={'edgeId': edge_id},
                          request_body_dict=current_config)


def reset_config(client_session, edge_id):
    client_session.delete('routingOSPF', uri_parameters={'edgeId': edge_id})


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            edge_name=dict(required=True, type='str'),
            logging=dict(default=False, type='bool'),
            log_level=dict(default='info', choices=['debug', 'info', 'notice', 'warning', 'error', 'critical',
                                                    'alert', 'emergency'], type='str'),
        ),
        supports_check_mode=False
    )

    client_session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                               module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])

    edge_id, edge_params = get_edge(client_session, module.params['edge_name'])
    if not edge_id:
        module.fail_json(msg='could not find Edge with name {}'.format(module.params['edge_name']))

    current_config = get_current_config(client_session, edge_id)




from ansible.module_utils.basic import *
from nsxramlclient.client import NsxClient

if __name__ == '__main__':
    main()
