#! /usr/bin/env python3

import oper_config
import boto3
import json
import sys


# get network account sts and credential
client_sts = boto3.client(
        "sts",
        aws_access_key_id = oper_config.user_aws_access_key_id,
        aws_secret_access_key = oper_config.user_aws_secret_access_key
        )

# request assume-role for network admin account
response = client_sts.assume_role(
        RoleArn = oper_config.form_assume_role_sktnetworktool.format_map({"account":oper_config.networkaccount_id}),
        RoleSessionName = oper_config.networkaccount_id,
        ExternalId = oper_config.network_external_id
        )

secret_for_account = { "response": {} }
if oper_config.networkaccount_id not in secret_for_account["response"].keys():
    secret_for_account["response"][oper_config.networkaccount_id] = {
            "aws_access_key_id" : response['Credentials']['AccessKeyId'],
            "aws_secret_access_key" : response['Credentials']['SecretAccessKey'],
            "aws_session_token" : response['Credentials']['SessionToken']
            }

# obtain virtual network list which is attached the specific transit gateway
client_ec2 = boto3.client(
        "ec2",
        aws_access_key_id = secret_for_account["response"][oper_config.networkaccount_id]["aws_access_key_id"],
        aws_secret_access_key = secret_for_account["response"][oper_config.networkaccount_id]["aws_secret_access_key"],
        aws_session_token = secret_for_account["response"][oper_config.networkaccount_id]["aws_session_token"]
        )

response = client_ec2.describe_transit_gateway_attachments(
        Filters = [ { 'Name' : 'transit-gateway-id', 'Values' : [ oper_config.TransitGatewayAttachmentIds ]} ]
        )

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

# obtain credential for each account
for attached_account_id in attached_account_contents["response"]:
    if attached_account_id != oper_config.networkaccount_id:
        try:
            response = client_sts.assume_role(
                    RoleArn = oper_config.form_assume_role_sktnetworktool.format_map({"account":attached_account_id}),
                    RoleSessionName = attached_account_id,
                    ExternalId = oper_config.network_external_id
                    )
        except:
            with open('error.out','a') as fn:
                fn.write(str(sys.exc_info())+"\n")
        else:
            if attached_account_id not in secret_for_account["response"].keys():
                secret_for_account["response"][attached_account_id] = {
                        "aws_access_key_id" : response['Credentials']['AccessKeyId'],
                        "aws_secret_access_key" : response['Credentials']['SecretAccessKey'],
                        "aws_session_token" : response['Credentials']['SessionToken']
                        }

# now, there are 2 types of dictionary,
# attachment_contents : virtual network information which is attached on transit gateway
# secret_for_account : crednetial for users
with open('attached_virtualnetworks.db.txt','w') as fn:
    fn.write(json.dumps(attachment_contents))
with open('credential_for_account.db.txt','w') as fn:
    fn.write(json.dumps(secret_for_account))



