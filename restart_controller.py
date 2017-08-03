#!/usr/bin/env python


if __name__ == "__main__":
    import os
    import logging
    import nifipy
    
    # configure basic logging
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger(nifipy.__name__).setLevel(logging.INFO)
    
    # read environment variables
    url_base = os.environ["URL_BASE"] 
    controller_id = os.environ["CONTROLLER_ID"]
    
    # restart controller
    con = nifipy.NifiConnection(url_base)
    cs = con.get_controller_service(controller_id)
    cs.restart()
