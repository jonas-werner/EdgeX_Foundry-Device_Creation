#!/usr/bin/python

##############################################################################################################
#     ______    __          _  __        __          _                                   __            
#    / ____/___/ /___ ____ | |/ /   ____/ /__ _   __(_)_______     _____________  ____ _/ /_____  _____
#   / __/ / __  / __ `/ _ \|   /   / __  / _ \ | / / / ___/ _ \   / ___/ ___/ _ \/ __ `/ __/ __ \/ ___/
#  / /___/ /_/ / /_/ /  __/   |   / /_/ /  __/ |/ / / /__/  __/  / /__/ /  /  __/ /_/ / /_/ /_/ / /    
# /_____/\__,_/\__, /\___/_/|_|   \__,_/\___/|___/_/\___/\___/   \___/_/   \___/\__,_/\__/\____/_/     
#             /____/                                                                                   
##############################################################################################################
# Name;     egfCreateEndpoint-07.py
# Version:  0.7
# Author:   Jonas Werner
##############################################################################################################


import requests, json, sys, re, time, os, warnings, argparse
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime

warnings.filterwarnings("ignore")

# Gather information from arguments
parser=argparse.ArgumentParser(description="Python script for creating a new device from scratch in EdgeX Foundry")
parser.add_argument('-ip',help='EdgeX Foundry IP address', required=True)
parser.add_argument('-version',help='EdgeX Foundry version (delhi or edinburgh)', required=True)

args=vars(parser.parse_args())

edgex_ip=args["ip"]
edgexVer=args["version"]


# Make two calls to Core Metadata, to create the Addressable for the Device Service:
def createAddressables():
    # Create the addressable for the Device Service:
    url = 'http://%s:48081/api/v1/addressable' % edgex_ip
    payload =   {
                    "name":         "humidity and temp address 1",
                    "protocol":     "HTTP",
                    "address":      "172.17.0.1",
                    "port":         49999,
                    "path":         "/hum_and_temp_cluster-01",
                    "publisher":    "none",
                    "user":         "none",
                    "password":     "none",
                    "topic":        "none"
                }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    print("Result of create addressables: %s with message %s" % (response, response.text))
    

def createValueDescriptors():
    url = 'http://%s:48080/api/v1/valuedescriptor' % edgex_ip
    payload =   {
                    "name":         "Humidity",
                    "description":  "Ambient humidity in percent",
                    "max":          "100",
                    "min":          "0",
                    "type":         "I",
                    "uomLabel":     "count",
                    "defaultValue": "0",
                    "formatting":   "%s",
                    "labels":       [
                                    "humidity",
                                    "percent"
                                    ]
                }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    print("Result of creating value descriptor for humidity: %s with message %s" % (response, response.text))
    

    payload =   {
                    "name":         "Temperature in C",
                    "description":  "Ambient temperature in Celcius",
                    "min":          "-10",
                    "max":          "100",
                    "type":         "I",
                    "uomLabel":     "count",
                    "defaultValue": "0",
                    "formatting":   "%s",
                    "labels":       [
                                    "temp",
                                    "celcius"
                                    ]
                }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    print("Result creating value descriptor for temperature: %s with message %s" % (response, response.text))
    


def uploadDeviceProfile():
    multipart_data = MultipartEncoder(
        fields={
                # a file upload field
                'file': ('file.py', open('EdgeX_TempHumidity_MonitorProfile.yml', 'rb'), 'text/plain')
               }
        )

    url = 'http://%s:48081/api/v1/deviceprofile/uploadfile' % edgex_ip
    response = requests.post(url, data=multipart_data,
                      headers={'Content-Type': multipart_data.content_type})

    print("Result of uploading device profile: %s with message %s" % (response, response.text))


def createDeviceService():
    url = 'http://%s:48081/api/v1/deviceservice' % edgex_ip
    payload =   {
                    "name":             "sensor cluster control device service",
                    "description":      "Manage sensor clusters delivering humidity and temperature readings",
                    "labels":           [
                                        "Raspberry Pi",
                                        "Sensor cluster"
                                        ],
                    "adminState":       "unlocked",
                    "operatingState":   "enabled",
                    "addressable":  {
                        "name": "sensor cluster control"
                    }
                }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    print("Result of create device service: %s with message %s" % (response, response.text))
    


def addNewDevice(edgexVer):
    url = 'http://%s:48081/api/v1/device' % edgex_ip

    if edgexVer == "delhi":
        payload =   {
                        "name":             "Temp_and_Humidity_sensor_cluster_01",
                        "description":      "Raspberry Pi sensor cluster",
                        "adminState":       "unlocked",
                        "operatingState":   "enabled",
                        "addressable": {
                            "name": "humidity and temp address 1"
                        },
                        "labels": [
                            "Raspberry Pi",
                            "Sensor cluster"
                        ],
                        "location": "",
                        "service": {
                            "name": "sensor cluster control device service"
                        },
                        "profile": {
                            "name": "Temp and Humidity sensor cluster monitor profile - 01"
                        }
                    }

    elif edgexVer == "edinburgh": 
        payload =   {
                        "name":             "Temp_and_Humidity_sensor_cluster_01",
                        "description":      "Raspberry Pi sensor cluster",
                        "adminState":       "unlocked",
                        "operatingState":   "enabled",
                        "protocols": {
                            "example": {
                            "host": "localhost",
                            "port": "1234",
                            "unitID": "1"
                            }
                        },
                        "addressable": {
                            "name": "humidity and temp address 1"
                        },
                        "labels": [
                            "Raspberry Pi",
                            "Sensor cluster"
                        ],
                        "location": "",
                        "service": {
                            "name": "sensor cluster control device service"
                        },
                        "profile": {
                            "name": "Temp and Humidity sensor cluster monitor profile - 01"
                        }
                    }

    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    
    print("Result of creating the device: %s with message %s" % (response, response.text))



if __name__ == "__main__":
    # Sanity check
    if not edgexVer == "delhi" and not edgexVer == "edinburgh":
        print("Supported versions are either delhi or edinburgh")
        sys.exit()
    else:
        print("EdgeX Foundry version is: %s" % edgexVer)

    createAddressables()
    createValueDescriptors()
    uploadDeviceProfile()
    createDeviceService()
    addNewDevice(edgexVer)
