import requests
import sys
import time
import pprint
import json
import logging

logger = logging.getLogger(__name__)

PROCESSOR = "Processor"
ROOTGROUP = "Root"
CONTROLLER_SERVICE = "Controller Service"

component_types = [
        PROCESSOR,
        CONTROLLER_SERVICE,
        ROOTGROUP
        ]

class NifiConnection(object):
 
    COMPONENT_ENDPOINT_TEMPLATES = {
        PROCESSOR: "{url_base}/nifi-api/processors/{component_id}",
        CONTROLLER_SERVICE: "{url_base}/nifi-api/controller-services/{component_id}",
        ROOTGROUP: "{url_base}/nifi-api/flow/process-groups/root/{subpath}"
        }

    # TODO: handle authentication and security features in this class as well!

    def __init__(self, url_base):
        self.url_base = url_base

    def get_processor(self, processor_id):
        return Processor(self, processor_id)

    def get_processors(self):
        pass

    def get_controller_service(self, controller_service_id):
        return ControllerService(self, controller_service_id)

    def get_controller_services(self):
        url_template = self.COMPONENT_ENDPOINT_TEMPLATES[ROOTGROUP]
        url = url_template.format(url_base=self.url_base, subpath="controller-services")
        response = self._get(url)
        return response.json()

    def _get(self, url):
        return requests.get(url)

    def _post(self, url, data):
        return requests.put(url, data=data, headers={"Content-Type": "application/json"})
 
    def get_info(self, url):
        response = self._get(url)
        return response.json()

    def get_min_info(self, url):
        response_dict = self.get_info(url)
        request_dict = {}
        request_dict["component"] = {
                "id": response_dict["component"]["id"]
                }
        request_dict["revision"] = {
                "version": response_dict["revision"]["version"]
                }
        return request_dict

    def change_state(self, url, state):
        request_dict = self.get_min_info(url)
        request_dict["component"]["state"] = state
        response = self._post(url, data = json.dumps(request_dict))
        logger.info(response.status_code)
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
        return "{}: url: {}".format(self.__class__, self.url)

    def __repr__(self):
        return "{}: url: {}".format(self.__class__, self.url)


class ProcessGroup(NifiComponent):
    component_type = "Process Group"

    def __init__(self, nifi_connection, process_group_id):
        NifiComponent.__init__(self, nifi_connection, process_group_id)



class Processor(NifiComponent):

    component_type = "Processor"

    def __init__(self, nifi_connection, processor_id):
        NifiComponent.__init__(self, nifi_connection, processor_id)

    def start(self):
        logger.info("starting {}".format(self))
        self.nifi_connection.change_state(self.url, "RUNNING")
    
    def stop(self):
        logger.info("stopping {}".format(self))
        self.nifi_connection.change_state(self.url, "STOPPED")
    
    def enable(self):
        logger.info("enabling {}".format(self))
        self.nifi_connection.change_state(self.url, "STOPPED")
    
    def disable(self):
        logger.info("disabling {}".format(self))
        self.nifi_connection.change_state(self.url, "DISABLED")

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
        [ component.stop() for component in self.get_referencing_components() ]
    
    def start_referencing_components(self):
        [ component.start() for component in self.get_referencing_components() ]
    
    def enable(self):
        logger.info("enabling {}".format(self))
        self.nifi_connection.change_state(self.url, "ENABLED")
    
    def disable(self):
        logger.info("disabling {}".format(self))
        self.nifi_connection.change_state(self.url, "DISABLED")

    def restart(self):
        self.stop_referencing_components()
        time.sleep(5)
        self.disable()
        time.sleep(5)
        self.enable()
        time.sleep(5)
        self.start_referencing_components()
