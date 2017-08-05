import pprint
import logging
from nifipy.components import NifiConnection
logging.basicConfig()  
logging.getLogger().setLevel(logging.DEBUG) 
requests_log = logging.getLogger("requests.packages.urllib3") 
requests_log.setLevel(logging.ERROR) 
requests_log.propagate = True 

import os
try:
    nifi_url = os.environ["NIFI_URL"]
except:
    nifi_url = None


def main(component, action, verbose: ("prints more info", "flag", "v"), component_id=None, nifiurl: ("NIFI_URL", "option")=nifi_url):
    if not nifi_url:
        raise Exception("Either specify nifiurl argument or set environment variable NIFI_URL")
    con = NifiConnection(nifiurl)
  
    if component == "controller-service":
        if action == "list":
            css = con.get_controller_services()
            if verbose: 
                pprint.pprint([cs.get_info() for cs in css])
            else:
                pprint.pprint([cs.get_min_info() for cs in css])

        if action == "get":
            if not component_id:
                raise Exception("Specify component_id when using 'get'!")
            cs= con.get_controller_service(component_id)
            if verbose: 
                pprint.pprint(cs.get_info())
            else:
                pprint.pprint(cs.get_min_info())

        if action == "enable":
            if not component_id:
                raise Exception("Specify component_id when using 'get'!")
            cs = con.get_controller_service(component_id)
            cs.enable()

        if action == "restart":
            if not component_id:
                raise Exception("Specify component_id when using 'get'!")
            cs = con.get_controller_service(component_id)
            cs.restart()

        if action == "disable":
            if not component_id:
                 raise Exception("Specify component_id when using 'get'!")
            cs = con.get_controller_service(component_id)
            cs.disable()

def __main__():
    import plac
    plac.call(main)
