#! /usr/bin/env python3

import json,io
import subprocess


return_out = subprocess.Popen("aws directconnect describe-virtual-interfaces",shell=True,stdout=subprocess.PIPE)
return_out_bytes = return_out.communicate()[0]
converted_contents = json.load(io.BytesIO(return_out_bytes.replace(b"'",b'"')))

for contents in converted_contents["virtualInterfaces"]:
    string_msg = "{}||{}||{}||{}||{}||{}||{}||{}||{}||{}||{}".format(contents["ownerAccount"],contents["virtualInterfaceType"],contents["virtualInterfaceName"],contents["vlan"],contents["asn"],contents["amazonSideAsn"],contents["authKey"],contents["amazonAddress"],contents["customerAddress"],contents["virtualGatewayId"],contents["directConnectGatewayId"])
    print(string_msg)



