#! /usr/bin/env bash

# Unset Environment
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

# Check Configuration file
if [ -f ./runcommand-config.cfg  ]
then
	source ./runcommand-config.cfg
else
	echo "[error] missing runcommand-config.cfg file!"
	exit
fi

# Essecial Verfication
EssFILE="$FilePrefixValidAccountfromTransitAttachment-$TransitAttachmentFile"
if [ ! -f ./$EssFILE ]
then
	echo "[error] run getAWStransitAttachment.sh"
	exit
fi

# Update NetworkAccount
if [ ! -f $SecretCredentialFile ]
then
	echo "[error] run getAccountCredentials.sh"
	exit
fi
source $SecretCredentialFile

# find out origin route table
rm -rf ./"$FilePrefixRoutefromTransit"*"$NetworkAccountID"

while read stringLine
do
	read -a strarr <<< $stringLine
	ACCNum=${strarr[0]}
	VPCResourceID=${strarr[1]}
	TGWattachID=${strarr[2]}
	RouteTableID=${strarr[4]}
        # Origin FileName
	OutFILE="$FilePrefixRoutefromTransit-$RouteTableID-$NetworkAccountID"
	returnMsg=$(aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $RouteTableID  --filters "Name=attachment.transit-gateway-attachment-id,Values=$TGWattachID")
	echo "$returnMsg," >> $OutFILE
	## in Python ==> ReadJson = json.loads("{\"result\":["+",".join(f.read()[:-1])+"]}")
	# display processing
	echo -n "!"
done < ./$EssFILE

# clear Env variable
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

