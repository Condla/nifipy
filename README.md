# nifipy

A Python Wrapper for the Nifi REST API

At the moment, only basic functionality is provided:
* Start/stop/disable/enable/restart a processor based on its processor id.
* Enable/Disable/restart a controller service based on its controller id.
* Listing controller service of root process group.

Feel free to add more functionality from the API

## Prerequisites

* A Nifi instance is up and running. https://nifi.apache.org/
* No authentication is required to access Nifi-API

## Installation

```
git clone https://www.github.com/condla/nifipy
cd nifipy
pip install -e nifipy .
```

The module depends on the requests module as well as on the plac module.

## Usage

* Set environment variable NIFI_URL or specify it using the `-nifiurl` flag.

```
usage: nifipy [-h] [-v] [-nifiurl http://condla4.field.hortonworks.com:9090]
              component action [component_id]

positional arguments:
  component
  action
  component_id          [None]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         prints more info
  -nifiurl http://condla4.field.hortonworks.com:9090
                        NIFI_URL
```

## Command Line Examples

* Lists controller services of root process group:

```
# This command retreives a JSON with minimal information about the controller servicices as JSON: id, name and revision version
nifipy controller-service list

# To get the full JSON set the -v (verbose) flag:
nifipy controller-service list -v
```

* Restarts controller service with specific ID:
```
nifipy controller-service restart f8a5b234-015c-1000-0000-00000b5bbbf6
```

* Get information about a single controller-service:
```
nifipy controller-service get f8a5b234-015c-1000-0000-00000b5bbbf6
```


## Python API Examples

This is great to use in Python programs, but also great for interactive usage with tools like IPython.

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
