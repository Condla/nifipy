# nifiapi

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

* Restart a controller service:
```
from nifiapi import ControllerService
cs = ControllerService("http://nifi.example.com:9090", "02439ee-015c-1000-ffff-ffffc7e2dd96")
cs.restart()
```

* Stop a processor:
```
from nifiapi import Processor
pr = Processor("http://nifi.example.com:9090", "ere880-ty34-1000-ffff-ffffdfk4343"")
pr.stop()
```

* The script `restart_controller.py` requires two environment variables:
```
export URL_BASE="http://nifi.example.com:9090"
export CONTROLLER_ID="02439ee-015c-1000-ffff-ffffc7e2dd96"
./restart_controller.py
```


