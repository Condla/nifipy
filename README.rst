# nifipy

A Python Wrapper for the Nifi REST API

At the moment, only basic functionality is provided:
* Start/stop/disable/enable a processor based on its processor id.
* Enable/Disable a controller service based on its controller id.

Feel free to add more functionality from the API

## Prerequisites

Python module: requests

```
pip install requests
```

## Examples

* Get all controller services of root process group:
```
from nifipy import NifiConnection
con = NifiConnection("http://nifi.example.com:9090")
css = con.get_controller_services()
````

* Restart a specific controller service with ID 02439ee-015c-1000-ffff-ffffc7e2dd96:
```
from nifipy import NifiConnection
con = NifiConnection("http://nifi.example.com:9090")
cs = con.get_controller_service("02439ee-015c-1000-ffff-ffffc7e2dd96")
cs.restart()
```

* Stop a processor with ID 02439ee-015c-1000-ffff-ffffc7e2dd96:
```
from nifipy import NifiConnection
con = NifiConnection("http://nifi.example.com:9090")
pr = con.get_processor("02439ee-015c-1000-ffff-ffffc7e2dd96")
pr.stop()
```

* The script `restart_controller.py` requires two environment variables:
```
export URL_BASE="http://nifi.example.com:9090"
export CONTROLLER_ID="02439ee-015c-1000-ffff-ffffc7e2dd96"
./restart_controller.py
````` ```````
