import time
import json
import logging
import requests

LOGGER = logging.getLogger(__name__)

BASE = "Base"
PROCESSOR = "Processor"
FLOW = "Flow"
CONTROLLER_SERVICE = "Controller Service"

COMPONENT_TYPES = [
    PROCESSOR,
    CONTROLLER_SERVICE,
    FLOW
    ]

class NifiConnection(object):

    COMPONENT_ENDPOINT_TEMPLATES = {
        BASE: "{url_base}/nifi-api",
        PROCESSOR: "{url_base}/nifi-api/processors/{component_id}",
        CONTROLLER_SERVICE: "{url_base}/nifi-api/controller-services/{component_id}",
        FLOW: "{url_base}/nifi-api/flow/process-groups/{process_group}/{subpath}"
        }

    # TODO: handle authentication and security features in this class as well!

    def __init__(self, url_base):
        self.url_base = url_base
        url = self.COMPONENT_ENDPOINT_TEMPLATES[BASE].format(url_base=self.url_base)
        try:
            self._get(url)
        except:
            raise ConnectionError("Could not connect to endpoint: {}.".format(url) + \
                    "Make sure you enter 'http://', specify your hostname and the port, " + \
                    "e.g. http://myhost.example.com:9090")

    def get_processor(self, processor_id):
        return Processor(self, processor_id)

    def get_processors(self):
        LOGGER.warning("method get_processors not implemented!")

    def get_controller_service(self, controller_service_id):
        return ControllerService(self, controller_service_id)

    def get_controller_services(self, process_group = "root"):
        url_template = self.COMPONENT_ENDPOINT_TEMPLATES[FLOW]
        url = url_template.format(url_base=self.url_base,
                                  process_group=process_group,
                                  subpath="controller-services")
        response = self._get(url)
        response_json = response.json()
        controller_service_ids = [
            controller_service["component"]["id"]
            for controller_service in response_json["controllerServices"]
            ]
        controller_services = [
            ControllerService(self, controller_service_id)
            for controller_service_id in controller_service_ids
            ]
        return controller_services

    def _get(self, url):
        return requests.get(url)

    def _post(self, url, data):
        return requests.put(url, data=data, headers={"Content-Type": "application/json"})

    def get_info(self, url):
        response = self._get(url)
        return response.json()

    def get_state(self, url):
        response_dict = self.get_info(url)
        request_dict = {}
        request_dict["component"] = {
            "id": response_dict["component"]["id"],
            "state": response_dict["component"]["state"]
            }
        request_dict["revision"] = {
            "version": response_dict["revision"]["version"]
            }
        return request_dict
 
    def get_min_info(self, url):
        response_dict = self.get_info(url)
        request_dict = {}
        request_dict["component"] = {
            "id": response_dict["component"]["id"],
            "name": response_dict["component"]["name"]
            }
        request_dict["revision"] = {
            "version": response_dict["revision"]["version"]
            }
        return request_dict

    def change_state(self, url, state, forbidden_initial_state=None):
        request_dict = self.get_state(url)
        if forbidden_initial_state and \
            request_dict["component"]["state"] == forbidden_initial_state:
                LOGGER.info("Can't change from {} to {}".format(forbidden_initial_state, state) + \
                            " in this request!" + \
                            "Method does not support this!")
        else:
            request_dict["component"]["state"] = state
            response = self._post(url, data=json.dumps(request_dict))
            LOGGER.info(response.status_code)
            if not response.status_code == 200:
                print(response.text)

    def get_referencing_components(self, url):
        request_dict = self.get_info(url)
        referencing_component_dicts = request_dict["component"]["referencingComponents"]
        referencing_component_infos = [
            (referencing_component_dict["component"]['id'], referencing_component_dict["component"]["referenceType"])
            for referencing_component_dict in referencing_component_dicts
            ]
        referencing_processors = [
            Processor(self, referencing_component_info[0])
            for referencing_component_info in referencing_component_infos
            if referencing_component_info[1] == PROCESSOR]

        # TODO: implement others referencing component types
        referencing_components = referencing_processors
        return referencing_components

class NifiComponent(object):

    component_type = None

    def __init__(self, nifi_connection, component_id):
        self.component_id = component_id
        self.nifi_connection = nifi_connection
        self.url_base = self.nifi_connection.url_base
        self.template = self.nifi_connection.COMPONENT_ENDPOINT_TEMPLATES[self.component_type]
        self.url = self.template.format(url_base=self.url_base, component_id=component_id)

    def __str__(self):
        return "url: {}".format(self.url)

    def __repr__(self):
        return "url: {}".format(self.url)

    def get_info(self):
        return self.nifi_connection.get_info(self.url)

    def get_min_info(self):
        return self.nifi_connection.get_min_info(self.url)


class ProcessGroup(NifiComponent):
    component_type = "Process Group"

    def __init__(self, nifi_connection, process_group_id):
        NifiComponent.__init__(self, nifi_connection, process_group_id)


class Processor(NifiComponent):

    component_type = "Processor"

    def __init__(self, nifi_connection, processor_id):
        NifiComponent.__init__(self, nifi_connection, processor_id)

    def start(self):
        LOGGER.info("starting {}".format(self))
        self.nifi_connection.change_state(self.url, "RUNNING", "DISABLED")

    def stop(self):
        LOGGER.info("stopping {}".format(self))
        self.nifi_connection.change_state(self.url, "STOPPED", "DISABLED")

    def enable(self):
        LOGGER.info("enabling {}".format(self))
        self.nifi_connection.change_state(self.url, "STOPPED", "RUNNING")

    def disable(self):
        LOGGER.info("disabling {}".format(self))
        self.nifi_connection.change_state(self.url, "DISABLED", "RUNNING")

    def restart(self):
        self.stop()
        time.sleep(5)
        self.start()


class ControllerService(NifiComponent):

    component_type = "Controller Service"

    def __init__(self, nifi_connection, controller_service_id):
        NifiComponent.__init__(self, nifi_connection, controller_service_id)


    def get_referencing_components(self):
        return self.nifi_connection.get_referencing_components(self.url)

    def stop_referencing_components(self):
        return [component.stop() for component in self.get_referencing_components()]

    def start_referencing_components(self):
        return [component.start() for component in self.get_referencing_components()]

    def enable(self):
        LOGGER.info("enabling {}".format(self))
        self.nifi_connection.change_state(self.url, "ENABLED")

    def disable(self):
        LOGGER.info("disabling {}".format(self))
        self.nifi_connection.change_state(self.url, "DISABLED")

    def restart(self):
        LOGGER.info("restarting controller service {}".format(self))
        self.stop_referencing_components()
        time.sleep(5)
        self.disable()
        time.sleep(5)
        self.enable()
        time.sleep(5)
        self.start_referencing_components()
        LOGGER.info("restart attempt of controller service {} concluded.".format(self)) 
