import json
import time
import uuid

import requests
from fedml.cli.scheduler.constants import Constants

from fedml.core.common.singleton import Singleton
from fedml.cli.server_deployment.server_constants import ServerConstants
from fedml.core.mlops.mlops_configs import MLOpsConfigs


class FedMLJobManager(Singleton):

    def __init__(self):
        pass

    @staticmethod
    def get_instance():
        return FedMLJobManager()

    def set_config_version(self, config_version):
        if config_version is not None:
            self.config_version = config_version

    def start_job(self, platform, project_name, application_name, device_server, device_edges,
                  user_id, user_api_key, job_name=None, no_confirmation=False):
        return self.start_job_api(platform, project_name, application_name, device_server, device_edges,
                                  user_id, user_api_key, job_name=job_name, no_confirmation=no_confirmation)

    def start_job_api(self, platform, project_name, application_name, device_server, device_edges,
                      user_id, user_api_key, job_name=None, no_confirmation=False):
        job_start_result = None
        jot_start_url = ServerConstants.get_job_start_url(self.config_version)
        job_api_headers = {'Content-Type': 'application/json', 'Connection': 'close'}
        real_job_name = job_name if job_name is not None and job_name != "" else f"FedML-CLI-Job-{str(uuid.uuid4())}"
        if device_server == "" or device_edges == "":
            device_lists = [{"account": "", "edgeIds": [], "serverId": 0}]
        else:
            device_lists = list()
            device_item = dict()
            device_item["account"] = user_id
            device_item["serverId"] = device_server
            device_item["edgeIds"] = str(device_edges).split(',')
            device_lists.append(device_item)
        job_start_json = {
            "platformType": platform,
            "applicationName": application_name,
            "applicationConfigId": 0,
            "devices": device_lists,
            "name": real_job_name,
            "projectName": project_name,
            "urls": [],
            "userId": user_id,
            "apiKey": user_api_key,
            "needConfirmation": True if user_api_key is None or user_api_key == "" else not no_confirmation
        }
        args = {"config_version": self.config_version}
        _, cert_path = MLOpsConfigs.get_instance(args).get_request_params_with_version(self.config_version)
        if cert_path is not None:
            try:
                requests.session().verify = cert_path
                response = requests.post(
                    jot_start_url, verify=True, headers=job_api_headers, json=job_start_json
                )
            except requests.exceptions.SSLError as err:
                MLOpsConfigs.install_root_ca_file()
                response = requests.post(
                    jot_start_url, verify=True, headers=job_api_headers, json=job_start_json
                )
        else:
            response = requests.post(jot_start_url, headers=job_api_headers, json=job_start_json)
        if response.status_code != 200:
            pass
        else:
            resp_data = response.json()
            if resp_data["code"] == "FAILURE":
                job_start_result = FedMLJobStartedModel({"job_name": real_job_name, "status": "FAILED",
                                                         "job_url": "",
                                                         "started_time": time.time()})
                return job_start_result
            job_start_result = FedMLJobStartedModel(resp_data["data"], job_name=job_name)
            # job_start_result = FedMLJobStartedModel({"job_name": job_name, "status": "STARTING",
            #                                         "job_url": "https://open.fedml.ai", "started_time": time.time()})

        return job_start_result

    def list_job(self, platform, project_name, job_name, user_id, user_api_key, job_id=None):
        result = self.list_job_api(platform, project_name, job_name, user_id, user_api_key, job_id=job_id)
        if result is None:
            return False

        return True

    def list_job_api(self, platform, project_name, job_name, user_id, user_api_key, job_id=None):
        job_list_result = None
        jot_list_url = ServerConstants.get_job_list_url(self.config_version)
        job_api_headers = {'Content-Type': 'application/json', 'Connection': 'close'}
        job_list_json = {
            "platformType": platform,
            "jobName": job_name,
            "projectName": project_name,
            "userId": user_id,
            "apiKey": user_api_key
        }
        if job_id is not None and job_id != "":
            job_list_json["jobId"] = job_id
        args = {"config_version": self.config_version}
        _, cert_path = MLOpsConfigs.get_instance(args).get_request_params_with_version(self.config_version)
        if cert_path is not None:
            try:
                requests.session().verify = cert_path
                response = requests.post(
                    jot_list_url, verify=True, headers=job_api_headers, json=job_list_json
                )
            except requests.exceptions.SSLError as err:
                MLOpsConfigs.install_root_ca_file()
                response = requests.post(
                    jot_list_url, verify=True, headers=job_api_headers, json=job_list_json
                )
        else:
            response = requests.post(jot_list_url, headers=job_api_headers, json=job_list_json)
        if response.status_code != 200:
            pass
        else:
            resp_data = response.json()
            if resp_data["code"] == "FAILURE":
                return None
            job_list_result = FedMLJobModelList(resp_data["data"])

        return job_list_result

    def stop_job(self, platform, project_name, job_name, user_id, user_api_key, job_id=None):
        return self.stop_job_api(platform, project_name, job_name, user_id, user_api_key, job_id=job_id)

    def stop_job_api(self, platform, project_name, job_name, user_id, user_api_key, job_id=None):
        jot_stop_url = ServerConstants.get_job_stop_url(self.config_version)
        job_api_headers = {'Content-Type': 'application/json', 'Connection': 'close'}
        job_stop_json = {
            "platformType": platform,
            "jobName": job_name,
            "projectName": project_name,
            "userId": user_id,
            "apiKey": user_api_key
        }
        if job_id is not None and job_id != "":
            job_stop_json["jobId"] = job_id
        args = {"config_version": self.config_version}
        _, cert_path = MLOpsConfigs.get_instance(args).get_request_params_with_version(self.config_version)
        if cert_path is not None:
            try:
                requests.session().verify = cert_path
                response = requests.post(
                    jot_stop_url, verify=True, headers=job_api_headers, json=job_stop_json
                )
            except requests.exceptions.SSLError as err:
                MLOpsConfigs.install_root_ca_file()
                response = requests.post(
                    jot_stop_url, verify=True, headers=job_api_headers, json=job_stop_json
                )
        else:
            response = requests.post(jot_stop_url, headers=job_api_headers, json=job_stop_json)
        if response.status_code != 200:
            return False
        else:
            resp_data = response.json()
            if resp_data["code"] == "FAILURE":
                return False

        return True


class FedMLJobStartedModel(object):
    def __init__(self, job_started_json, job_name=None):
        if isinstance(job_started_json, dict):
            self.job_id = job_started_json.get("job_id", "0")
            self.job_name = job_started_json.get("job_name", job_name)
            self.status = job_started_json.get("status", Constants.MLOPS_CLIENT_STATUS_NOT_STARTED)
            self.job_url = job_started_json.get("job_url", job_started_json)
            self.started_time = job_started_json.get("started_time", time.time())
        else:
            self.job_id = "0"
            self.job_name = job_name
            self.status = Constants.MLOPS_CLIENT_STATUS_NOT_STARTED
            self.job_url = job_started_json
            self.started_time = time.time()


class FedMLJobModelList(object):
    def __init__(self, job_list_json):
        self.total_num = job_list_json["total"]
        self.total_page = job_list_json["totalPage"]
        self.page_num = job_list_json["pageNum"]
        self.page_size = job_list_json["pageSize"]
        job_list_data = job_list_json["data"]
        self.job_list = list()
        for job_obj_json in job_list_data:
            job_obj = FedMLJobModel(job_obj_json)
            self.job_list.append(job_obj)


class FedMLJobModel(object):
    def __init__(self, job_json):
        self.job_name = job_json["job_name"]
        self.status = job_json["status"]
        self.started_time = job_json["started_time"]
        self.ended_time = job_json["ended_time"]
        self.running_time = job_json["running_time"]
        self.compute_start_time = job_json["compute_start_time"]
        self.compute_end_time = job_json["compute_end_time"]
        self.compute_duration = job_json["compute_duration"]
        self.cost = job_json["cost"]
        self.device_id = job_json["device_id"]
        self.device_info = job_json["device_info"]
        self.job_url = job_json["job_url"]

    def parse(self, job_json):
        pass
