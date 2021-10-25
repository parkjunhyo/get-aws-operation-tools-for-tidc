#! /usr/bin/env python3

import oper_config
import boto3
import json
import sys
import ipaddress

with open("attached_virtualnetworks.db.txt","r") as fn:
    attached_virtualnetworks_db = json.loads(fn.read())

with open("credential_for_account.db.txt","r") as fn:
    credential_for_account_db = json.loads(fn.read())

# run ec2 command 
subnet_usages_contents = { 'response' : [] }
for contents in attached_virtualnetworks_db["response"]:

    try:
        # run boto3 to findout the subnet information for specific vpc-id matched.
        client_ec2 = boto3.client(
            "ec2",
            aws_access_key_id = credential_for_account_db["response"][contents['ResourceOwnerId']]["aws_access_key_id"],
            aws_secret_access_key = credential_for_account_db["response"][contents['ResourceOwnerId']]["aws_secret_access_key"],
            aws_session_token = credential_for_account_db["response"][contents['ResourceOwnerId']]["aws_session_token"]
            )
        response = client_ec2.describe_subnets( Filters = [{ 'Name': 'vpc-id', 'Values' : [contents['ResourceId']] }] )
    except:
        with open('error.out','a') as fn:
            fn.write(str(sys.exc_info())+"\n")
    else:
        # re-arrange the information by the format
        init_temp = {}
        for subnets_contents in response['Subnets']:
            for destcidr in contents['DestinationCidrBlock']:
                if ipaddress.ip_network(subnets_contents['CidrBlock']).subnet_of(ipaddress.ip_network(destcidr)):
                    if destcidr not in init_temp.keys():
                        init_temp[destcidr] = []
                    init_temp[destcidr].append({
                                'CidrBlock':subnets_contents['CidrBlock'],
                                'AvailableIpAddressCount':subnets_contents['AvailableIpAddressCount'],
                                'AvailabilityZone':subnets_contents['AvailabilityZone']
                            })
                    break
        
        # result_form_json initialized
        result_form_json = { "OwnerId":contents['ResourceOwnerId'], "VpcId":contents['ResourceId'], "DestinationCidrBlockUsages" : [] }
        for destcidr in contents['DestinationCidrBlock']:
            if destcidr in init_temp.keys():
                result_form_json['DestinationCidrBlockUsages'].append({ 'DestinationCidrBlock' : destcidr, 'SubnetUsages' : init_temp[destcidr] })
            else:
                result_form_json['DestinationCidrBlockUsages'].append({ 'DestinationCidrBlock' : destcidr, 'SubnetUsages' : [] })
        subnet_usages_contents['response'].append(result_form_json)

# now, there are  types of dictionary,
# subnet_usages_contents : subnet usage status
with open('subnet_usages_status.db.txt','w') as fn:
    fn.write(json.dumps(subnet_usages_contents))
