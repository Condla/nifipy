import pprint
import os
import logging
from nifipy.components import NifiConnection, ProcessGroup

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.ERROR)
requests_log.propagate = True

try:
    NIFI_URL = os.environ["NIFI_URL"]
except KeyError:
    NIFI_URL = None

def print_component_json(component, verbose):
    if isinstance(component, list):
        if verbose:
            pprint.pprint([c.get_info() for c in component])
        else:
            pprint.pprint([c.get_min_info() for c in component])
    else:
        if verbose:
            pprint.pprint(component.get_info())
        else:
            pprint.pprint(component.get_min_info())


def check_component_id(component_id):
    if not component_id:
        raise Exception("Specify component_id when using 'get'!")


def main(
        component,
        action,
        verbose: ("prints more info", "flag", "v"),
        component_id=None,
        nifiurl: ("NIFI_URL", "option")=NIFI_URL):

    if not nifiurl:
        raise Exception("Either specify nifiurl argument or set environment variable NIFI_URL")
    con = NifiConnection(nifiurl)

    if component == "process-group":
        if action == "upload-template":
            pg = ProcessGroup(con, "root")

    elif component == "controller-service":
        if action == "list":
            css = con.get_controller_services()
            print_component_json(css, verbose)

        if action == "get":
            check_component_id(component_id)
            controller_service = con.get_controller_service(component_id)
            print_component_json(controller_service, verbose)

        if action == "enable":
            check_component_id(component_id)
            controller_service = con.get_controller_service(component_id)
            controller_service.enable()

        if action == "restart":
            check_component_id(component_id)
            controller_service = con.get_controller_service(component_id)
            controller_service.restart()

        if action == "disable":
            check_component_id(component_id)
            controller_service = con.get_controller_service(component_id)
            controller_service.disable()

    if component == "processor":
        if action == "get":
            check_component_id(component_id)
            processor = con.get_processor(component_id)
            print_component_json(processor, verbose)

def __main__():
    import plac
    plac.call(main)
