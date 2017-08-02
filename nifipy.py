import requests
import sys
import time
import pprint
import json
import logging

logger = logging.getLogger(__name__)
class NifiComponent(object):
    
    def __init__(self, url_base, component_id):
        self.url_base = url_base
        self.component_id = component_id
        self.url = self.url_template.format(url_base=url_base, component_id=component_id)
    
    def get_state(self):
        response = requests.get(self.url)
        response_dict = response.json()
        return response_dict

    def get_min_state(self):
        response_dict = self.get_state()
        request_dict = {}
        request_dict["component"] = {}
        request_dict["component"]["id"] = self.component_id
        request_dict["revision"] = {"version": response_dict["revision"]["version"]}
        return request_dict

    def do(self, state):
        request_dict = self.get_min_state()
        request_dict["component"]["state"] = state
        response = requests.put(self.url, data = json.dumps(request_dict), headers={"Content-Type": "application/json"})
        logger.info(response.status_code)
        if not response.status_code == 200:
            print(response.text)

    def __str__(self):
        return "{}: {}".format(self.__class__, self.component_id)

    def __repr__(self):
        return "{}: {}".format(self.__class__, self.component_id)


class Processor(NifiComponent):
    url_template = "{url_base}/nifi-api/processors/{component_id}"

    def __init__(self, url_base, processor_id):
        NifiComponent.__init__(self, url_base, processor_id)

    def start(self):
        logger.info("starting {}".format(self))
        self.do("RUNNING")
    
    def stop(self):
        logger.info("stopping {}".format(self))
        self.do("STOPPED")
    
    def enable(self):
        logger.info("enabling {}".format(self))
        self.do("STOPPED")
    
    def disable(self):
        logger.info("disabling {}".format(self))
        self.do("DISABLED")

    def restart(self):
        self.stop()
        time.sleep(5)
        self.start()
    

class ControllerService(NifiComponent):
    url_template = "{url_base}/nifi-api/controller-services/{component_id}"

    def __init__(self, url_base, controller_id):
        NifiComponent.__init__(self, url_base, controller_id)
    

    def get_referencing_components(self):
        request_dict = self.get_state()
        referencing_component_dicts = request_dict["component"]["referencingComponents"]
        referencing_component_ids = [
                referencing_component_dict["component"]['id']
                for referencing_component_dict in referencing_component_dicts
                ]
        referencing_components = [
                Processor(self.url_base, referencing_component_id)
                for referencing_component_id in referencing_component_ids
                ]
        return referencing_components

    def stop_referencing_components(self):
        [ component.stop() for component in self.get_referencing_components() ]
    
    def start_referencing_components(self):
        [ component.start() for component in self.get_referencing_components() ]
    
    def enable(self):
        logger.info("enabling {}".format(self))
        self.do("ENABLED")
    
    def disable(self):
        logger.info("disabling {}".format(self))
        self.do("DISABLED")

    def restart(self):
        self.stop_referencing_components()
        time.sleep(5)
        self.disable()
        time.sleep(5)
        self.enable()
        time.sleep(5)
        self.start_referencing_components()

    

