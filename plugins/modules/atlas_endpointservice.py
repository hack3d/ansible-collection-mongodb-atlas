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
module: atlas_endpointservice
short_description: Manage endpoint service in Atlas
description:
    - The endpointservice module provieds access to your network access configuration
    - The module lets you create, edit and delete endpoint services
    - L(API Documentation, https://www.mongodb.com/docs/atlas/reference/api/private-endpoints/)
author: "@hack3d"
extends_documentation_fragment: t_systems_mms.mongodb_atlas.atlas_global_options
options:
    providerName:
        description:
            - Name of the cloud provider for which you want to create the private endpoint service. Atlas accepts AWS, AZURE, or GCP.
        type: str
        required: True
    region:
        description:
            - Cloud provider region for which you want to create the private endpoint service.
        type: str
        required: True
"""

EXAMPLES = """
    - name: Test endpoint service
      atlas_endpointservice:
        apiUsername: "API_user"
        apiPassword: "API_password_or_token"
        groupId: "GROUP_ID"
        providerName: "AZURE"
        region: "EUROPE_WEST"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.t_systems_mms.mongodb_atlas.plugins.module_utils.atlas import (
    AtlasAPIObject,
)

def main():
    argument_spec = dict(
        state=dict(default="present", choices=["absent", "present"]),
        apiUsername=dict(required=True),
        apiPassword=dict(required=True, no_log=True),
        groupId=dict(required=True),
        providerName=dict(required=True),
        region=dict(required=True)
    )

    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )

    data = {
        "providerName": module.params["providerName"],
        "region": module.params["region"],
    }

    try:
        atlas = AtlasAPIObject(
            module=module,
            path="/privateEndpoint/endpointService",
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