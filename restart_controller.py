#!/usr/bin/env python


if __name__ == "__main__":
    import os
    import nifipy
    from nifipy import ControllerService
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger(nifiapi.__name__).setLevel(logging.INFO)

    url_base = os.environ["URL_BASE"] 
    controller_id = os.environ["CONTROLLER_ID"]
    cs = ControllerService(url_base, controller_id)
    cs.restart()
