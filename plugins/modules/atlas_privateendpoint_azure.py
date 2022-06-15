#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "0.1",
    "status": ["previed"],
    "supported_by": "community",
}

DOCUMENTATION = """
module: atlas_privateendpoint_azure
short_description: Manage azure privateendpoint in Atlas
description:
    - The privateendpoint module provides access to your network access configuration
    - The module lets you create, edit and delete privateendpoint in azure
    - L(API Documentation, https://www.mongodb.com/docs/atlas/reference/api/private-endpoints-endpoint-create-one/)
author: "@hack3d"
extends_documentation_fragment: t_systems_mms.mongodb_atlas.atlas_global_options
options:
    privateEndpointId:
        description:
            - Unique identifier of the private endpoint you created in your Azure VNet.
        type: str
        required: True
    privateEndpointIPAddress:
        description:
            - Private IP address of the private endpoint network interface you created in your Azure VNet.
        type: str
        required: True
    endpointServiceId:
        description:
            - Id of the endpoint service
        type: str
        required: True
"""

EXAMPLES = """
    - name: Test privateendpoint
      atlas_privateendpoint_azure
        apiUsername: "API_user"
        apiPassword: "API_password_or_token"
        groupId: "GROUP_ID"
        privateEndpointId: "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/privatelink/providers/Microsoft.Network/privateEndpoints/test"
        privateEndpointIPAddress: "192.168.0.20"
        endpointServiceId: "62a8c7fc2b437441bd53ae34"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.t_systems_mms.mongodb_atlas.plugins.module_utils.atlas import (
    AtlasAPIObject,
)


def main():
    argument_spec = dict(
        state=dict(default="present", choices=["absent", "present"]),
        apiUsername=dict(required=True),
        apiPassword=dict(required=True),
        groupId=dict(required=True),
        privateEndpointId=dict(required=True),
        privateEndpointIPAddress=dict(required=True),
        endpointServiceId=dict(required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )

    data = {
        "id": module.params["privateEndpointId"],
        "privateEndpointIPAddress": module.params["privateEndpointIPAddress"],
    }

    try:
        atlas = AtlasAPIObject(
            module=module,
            path="/privateEndpoint/AZURE/endpointService/",
            object_name="endpointServiceId",
            groupId=module.params["groupId"],
            data=data,
        )
    except Exception as e:
        module.fail_json(
            msg="unable to connect to Atlas API. Exception message: %s" % e
        )
    
    changed, diff = atlas.update(module.params["state"])
    module.exit_json(
        changed=changed,
        data=atlas.data,
        diff=diff,
    )

if __name__ == "__main__":
    main()