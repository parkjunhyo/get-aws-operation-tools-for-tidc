#! /usr/bin/env python3

import oper_config
import boto3
import json
import sys
import ipaddress
import uuid

with open("attached_virtualnetworks.db.txt","r") as fn:
    attached_virtualnetworks_db = json.loads(fn.read())

with open("credential_for_account.db.txt","r") as fn:
    credential_for_account_db = json.loads(fn.read())

# re-arrange information and insert into the dynamodb
client_dynamodb = boto3.client("dynamodb", aws_access_key_id=oper_config.dynamodb_aws_access_key_id, aws_secret_access_key=oper_config.dynamodb_aws_secret_access_key)

# delete all items in dynamodb : initialize database
response = client_dynamodb.scan(TableName=oper_config.dynamodb_tablename)
for rm_item in response['Items']:
    client_dynamodb.delete_item(
            TableName=oper_config.dynamodb_tablename,
            Key={ 'uuid' : rm_item['uuid'] }
            )

# calculating the subnet usages and write file and database, dynamodb
save_file_contents = { 'response' : [] }
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
        # re-arrange the information by the format for dynamodb
        init_temp = {}
        for subnets_contents in response['Subnets']:
            for destcidr in contents['DestinationCidrBlock']:
                if ipaddress.ip_network(subnets_contents['CidrBlock']).subnet_of(ipaddress.ip_network(destcidr)):
                    if destcidr not in init_temp.keys():
                        init_temp[destcidr] = []
                    # 
                    init_temp[destcidr].append({ "M" : {
                        "CidrBlock" : { "S" : subnets_contents['CidrBlock'] },
                        "AvailableIpAddressCount" : { "N" : str(subnets_contents['AvailableIpAddressCount']) },
                        "AvailabilityZone" : { "S" : subnets_contents['AvailabilityZone'] }
                      }
                    })
                    break
        
        # result_form_json initialized
        # OwneId should use mark '#' to export to CSV file
        dynamodb_form = {
                "uuid" : { "S" : str(uuid.uuid4()) },
                "OwnerId" : { "S" : "#"+contents['ResourceOwnerId'] },
                "VpcId" : { "S" : contents['ResourceId'] },
                "DestinationCidrBlockUsages" : { "L" : [] }
                }
       
        for destcidr in contents['DestinationCidrBlock']:
            if destcidr in init_temp.keys():
                # calculating percentage for used
                allocated_totalsize=2**(int(32)-int(destcidr.split('/')[1]))
                left_sum = int(0)
                for cidrblocks in init_temp[destcidr]:
                    left_sum = left_sum + int(cidrblocks['M']['AvailableIpAddressCount']['N'])
                usaged_percentage = round(((allocated_totalsize-left_sum)/allocated_totalsize)*100)
                #
                subnetusages_values = { "L" : init_temp[destcidr] }
                cidrblockusagepercentage_value = { "N" : str(usaged_percentage) }
            else:
                #
                subnetusages_values = { "L" : [] }
                cidrblockusagepercentage_value = { "N" : "0" }
      
            dynamodb_form['DestinationCidrBlockUsages']['L'].append(
                    { "M" : {
                        "DestinationCidrBlock": { "S" : destcidr },
                        "SubnetUsages": subnetusages_values,
                        "CidrBlockUsagePercentage": cidrblockusagepercentage_value
                        }
                    })
        client_dynamodb.put_item(TableName=oper_config.dynamodb_tablename, Item=dynamodb_form)
        save_file_contents['response'].append(dynamodb_form)

# now, there are  types of dictionary,
# save_file_contents : subnet usage status
with open('subnet_usages_status.db.txt','w') as fn:
    fn.write(json.dumps(save_file_contents))
