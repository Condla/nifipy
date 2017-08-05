
import logging
logging.basicConfig()  
logging.getLogger().setLevel(logging.DEBUG) 
#requests_log = logging.getLogger("requests.packages.urllib3") 
#requests_log.setLevel(logging.DEBUG) 
#requests_log.propagate = True 

import os
try:
    nifi_url = os.environ["NIFI_URL"]
except:
    nifi_url = None


def main(nifiurl=nifi_url):
    if not nifi_url:
        raise Exception("Either specify nifiurl argument or set environment variable NIFI_URL")
    from nifipy.components import NifiConnection
    con = NifiConnection(nifiurl)
    print(con)


def __main__():
    import plac
    plac.call(main)
