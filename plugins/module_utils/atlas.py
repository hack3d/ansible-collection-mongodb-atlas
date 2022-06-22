# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import urllib
from collections import defaultdict

from ansible.module_utils.urls import fetch_url

try:
    from urllib import quote
except ImportError:
    # noinspection PyCompatibility, PyUnresolvedReferences
    from urllib.parse import (
        quote,
    )  # pylint: disable=locally-disabled, import-error, no-name-in-module


class AtlasAPIObject:
    module = None

    def __init__(
        self, module, groupId, path, data, object_name=None, data_is_array=False
    ):
        self.module = module
        self.path = path
        self.data = data
        self.groupId = groupId
        self.object_name = object_name
        self.data_is_array = data_is_array

        self.module.params["url_username"] = self.module.params["apiUsername"]
        self.module.params["url_password"] = self.module.params["apiPassword"]

    def call_url(self, path, data="", method="GET"):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.data_is_array and data != "":
            data = "[" + data + "]"

        url = (
            "https://cloud.mongodb.com/api/atlas/v1.0/groups/"
            + self.groupId
            + path
        )
        rsp, info = fetch_url(
            module=self.module,
            url=url,
            data=data,
            headers=headers,
            method=method,
        )

        content = ""
        error = ""
        if rsp and info["status"] != 204:
            content = json.loads(rsp.read())
        if info["status"] >= 400:
            try:
                content = json.loads(info["body"])
                error = content["reason"]
                if "detail" in content:
                    error += ". Detail: " + content["detail"]
            except ValueError:
                error = info["msg"]
        if info["status"] < 0:
            error = info["msg"]
        return {"code": info["status"], "data": content, "error": error}

    def exists(self):
        additional_path = ""
        if self.path == "/databaseUsers":
            additional_path = "/admin"
    
        path = "{}{}".format(self.path, additional_path)

        if self.path == "/privateEndpoint/endpointService":
            path = "/privateEndpoint/{}/endpointService".format(self.module.params["providerName"])
        elif self.path == "/privateEndpoint/AZURE/endpointService":
            path = "/privateEndpoint/AZURE/endpointService/{}/endpoint/{}".format(self.data[self.object_name], urllib.parse.urlencode(self.data["id"]))
        else:
            if self.object_name != None:
                path = "{}/{}".format(path, quote(self.data[self.object_name], ""))

        ret = self.call_url(
            path=path
        )
        if self.path == "/privateEndpoint/AZURE/endpointService":
            raise Exception("Status: {}, Path: {}".format(ret["code"], path))
        if ret["code"] == 200:
            return True
        return False

    def create(self):
        if self.path == "/privateEndpoint/AZURE/endpointService":
            self.path = "{}/{}/endpoint".format(self.path, self.data[self.object_name])
            self.data.pop(self.object_name, None)

        ret = self.call_url(
            path=self.path,
            data=self.module.jsonify(self.data),
            method="POST",
        )
        return ret

    def delete(self):
        additional_path = ""
        if self.path == "/databaseUsers":
            additional_path = "/admin"
        ret = self.call_url(
            path=self.path
            + additional_path
            + "/"
            + quote(self.data[self.object_name], ""),
            method="DELETE",
        )
        return ret

    def modify(self):
        additional_path = ""
        if self.path == "/databaseUsers":
            additional_path = "/admin"
        
        ret = self.call_url(
            path=self.path
            + additional_path
            + "/"
            + quote(self.data[self.object_name], ""),
            data=self.module.jsonify(self.data),
            method="PATCH",
        )
        return ret

    def diff(self):
        additional_path = ""
        if self.path == "/databaseUsers":
            additional_path = "/admin"

        path = "{}{}".format(self.path, additional_path)

        if self.path == "/privateEndpoint/endpointService":
            path = "/privateEndpoint/{}/endpointService".format(self.module.params["providerName"])
        else:
            if self.object_name != None:
                path = "{}/{}".format(path, quote(self.data[self.object_name], ""))
        
        ret = self.call_url(
            path=path,
            method="GET",
        )

        data_from_atlas = json.loads(self.module.jsonify(ret["data"]))
        data_from_task = json.loads(self.module.jsonify(self.data))

        diff = defaultdict(dict)
        if self.path == "/privateEndpoint/endpointService":
            for x in data_from_atlas:
                if x['regionName'] == self.module.params["region"]:
                    for key, value in x.items():
                        if key in data_from_task.keys() and value != data_from_task[key]:
                            diff["before"][key] = "{val}".format(val=value)
                            diff["after"][key] = "{val}".format(val=data_from_task[key])
        else:
            for key, value in data_from_atlas.items():
                if key in data_from_task.keys() and value != data_from_task[key]:
                    diff["before"][key] = "{val}".format(val=value)
                    diff["after"][key] = "{val}".format(val=data_from_task[key])
        return diff

    def get(self):
        additional_path = ""
        if self.path == "/databaseUsers":
            additional_path = "/admin"

        path = "{}{}".format(self.path, additional_path)

        if self.path == "/privateEndpoint/endpointService":
            path = "/privateEndpoint/{}/endpointService".format(self.module.params["providerName"])
        else:
            if self.object_name != None:
                path = "{}/{}".format(path, quote(self.data[self.object_name], ""))
        
        ret = self.call_url(
            path=path,
            method="GET",
        )

        data_from_atlas = json.loads(self.module.jsonify(ret["data"]))
        
        if self.path == "/privateEndpoint/endpointService":
            for x in data_from_atlas:
                if x['regionName'] == self.module.params["region"]:
                    return x
        return data_from_atlas

    def update(self, state):
        changed = False
        diff_result = {"before": "", "after": ""}
        if self.exists():
            diff_result.update({"before": "state: present\n"})
            if state == "absent":
                if self.module.check_mode:
                    diff_result.update({"after": "state: absent\n"})
                    self.module.exit_json(
                        changed=True,
                        object_name=self.data[self.object_name],
                        diff=diff_result,
                    )
                else:
                    try:
                        ret = self.delete()
                        if ret["code"] == 204 or ret["code"] == 202:
                            changed = True
                            diff_result.update({"after": "state: absent\n"})
                        else:
                            self.module.fail_json(
                                msg="bad return code while deleting: %d. Error message: %s"
                                % (ret["code"], ret["error"])
                            )
                    except Exception as e:
                        self.module.fail_json(
                            msg="exception when deleting: " + str(e)
                        )

            else:
                diff_result.update(self.diff())
                if self.module.check_mode:
                    if diff_result["after"] != "":
                        changed = True
                    self.module.exit_json(
                        changed=changed,
                        object_name=self.data[self.object_name],
                        data=self.data,
                        diff=diff_result,
                    )
                if diff_result["after"] != "":
                    if self.path == "/whitelist":
                        ret = self.create()
                    else:
                        ret = self.modify()
                    if ret["code"] == 200 or ret["code"] == 201:
                        changed = True
                    else:
                        self.module.fail_json(
                            msg="bad return code while modifying: %d. Error message: %s, Diff: %s"
                            % (ret["code"], ret["error"], json.dumps(diff_result))
                        )

        else:
            diff_result.update({"before": "state: absent\n"})
            if state == "present":
                if self.module.check_mode:
                    changed = True
                    diff_result.update({"after": "state: created\n"})
                else:
                    try:
                        ret = self.create()
                        if ret["code"] == 201:
                            changed = True
                            diff_result.update({"after": "state: created\n"})
                        if self.path.startswith("/privateEndpoint/AZURE/endpointService/") and ret["code"] == 409:
                            diff_result.update({"aftter": "state: created\n"})
                        if ret["code"] != 201 or (ret["code"] != 409 and self.path.startswith("/privateEndpoint/AZURE/endpointService/")):
                            self.module.fail_json(
                                msg="bad return code while creating: %d. Error message: %s, Data: %s, Path: %s"
                                % (ret["code"], ret["error"], self.data, self.path)
                            )
                    except Exception as e:
                        self.module.fail_json(
                            msg="exception while creating: " + str(e)
                        )
        return changed, diff_result
