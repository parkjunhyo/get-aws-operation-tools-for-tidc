import json
import os
import sys
import boto3
import ipaddress
import uuid


def lambda_handler(event, context):
    # get the network account sts
    client_sts = boto3.client(
        "sts",
        aws_access_key_id = os.environ['user_aws_access_key_id'],
        aws_secret_access_key = os.environ['user_aws_secret_access_key']
        )
    
    response_sts = client_sts.assume_role(
        RoleArn = os.environ['form_assume_role_sktnetworktool'].format_map({"account":os.environ['networkaccount_id']}),
        RoleSessionName = os.environ['networkaccount_id'],
        ExternalId = os.environ['network_external_id']
        )
    
    secret_for_account = { "response": {} }
    if os.environ['networkaccount_id'] not in secret_for_account["response"].keys():
        secret_for_account["response"][os.environ['networkaccount_id']] = {
            "aws_access_key_id" : response_sts['Credentials']['AccessKeyId'],
            "aws_secret_access_key" : response_sts['Credentials']['SecretAccessKey'],
            "aws_session_token" : response_sts['Credentials']['SessionToken']
        }
        
    # get virtual network list which is attached the specific transit gateway
    client_ec2 = boto3.client(
        "ec2",
        aws_access_key_id = secret_for_account["response"][os.environ['networkaccount_id']]["aws_access_key_id"],
        aws_secret_access_key = secret_for_account["response"][os.environ['networkaccount_id']]["aws_secret_access_key"],
        aws_session_token = secret_for_account["response"][os.environ['networkaccount_id']]["aws_session_token"]
        )
    response = client_ec2.describe_transit_gateway_attachments(Filters = [ { 'Name' : 'transit-gateway-id', 'Values' : [ os.environ['TransitGatewayAttachmentIds'] ]} ])
    attachment_contents = { "response" : [] }
    attached_account_contents = { "response" : [] }
    for contents in response['TransitGatewayAttachments']:
        if contents['ResourceType'] == 'vpc' and contents['State'] == 'available':
            # route table 
            if contents['Association']['State'] == 'associated':
                # find specific subnet to route for vpc next hop
                response_search_transit_route = client_ec2.search_transit_gateway_routes(
                        TransitGatewayRouteTableId = contents['Association']['TransitGatewayRouteTableId'],
                        Filters = [
                            { 'Name':'type', 'Values':['static'] },
                            { 'Name':'attachment.resource-type', 'Values':['vpc'] },
                            { 'Name':'attachment.transit-gateway-attachment-id', 'Values':[ contents['TransitGatewayAttachmentId'] ] }
                            ]
                        )
                # Routes and DestinationCidrBlock search
                block_list_contents = []
                for block_n in response_search_transit_route['Routes']:
                    if block_n['DestinationCidrBlock'] not in block_list_contents:
                        block_list_contents.append(block_n['DestinationCidrBlock'])
                # virtual network and account information
                attachment_contents["response"].append(
                        {
                            'ResourceOwnerId':contents['ResourceOwnerId'],
                            'ResourceId':contents['ResourceId'],
                            'TransitGatewayAttachmentId':contents['TransitGatewayAttachmentId'],
                            'TransitGatewayRouteTableId':contents['Association']['TransitGatewayRouteTableId'],
                            'DestinationCidrBlock':block_list_contents
                        }
                        )
                if contents['ResourceOwnerId'] not in attached_account_contents["response"]:
                    attached_account_contents["response"].append(contents['ResourceOwnerId'])
    
    # get credential for each account   
    for attached_account_id in attached_account_contents["response"]:
        if attached_account_id != os.environ['networkaccount_id']:
            try:
                response = client_sts.assume_role(
                        RoleArn = os.environ['form_assume_role_sktnetworktool'].format_map({"account":attached_account_id}),
                        RoleSessionName = attached_account_id,
                        ExternalId = os.environ['network_external_id']
                        )
            except:
                print("[error - 1] "+attached_account_id+" is not valid")
            else:
                if attached_account_id not in secret_for_account["response"].keys():
                    secret_for_account["response"][attached_account_id] = {
                            "aws_access_key_id" : response['Credentials']['AccessKeyId'],
                            "aws_secret_access_key" : response['Credentials']['SecretAccessKey'],
                            "aws_session_token" : response['Credentials']['SessionToken']
                            }
    # re-define the variable
    attached_virtualnetworks_db = attachment_contents
    credential_for_account_db = secret_for_account
    
    # re-arrange information and insert into the dynamodb
    client_dynamodb = boto3.client("dynamodb", aws_access_key_id=os.environ['dynamodb_aws_access_key_id'], aws_secret_access_key=os.environ['dynamodb_aws_secret_access_key'])
    # delete all items in dynamodb : initialize database
    response = client_dynamodb.scan(TableName=os.environ['dynamodb_tablename'])
    for rm_item in response['Items']:
        client_dynamodb.delete_item(
                TableName=os.environ['dynamodb_tablename'],
                Key={ 'uuid' : rm_item['uuid'] }
                )
    # calculating the subnet usages and write database, dynamodb
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
            print("[error - 2] "+contents['ResourceOwnerId']+" is not valid")
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
            client_dynamodb.put_item(TableName=os.environ['dynamodb_tablename'], Item=dynamodb_form)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(dynamodb_form)
    }
