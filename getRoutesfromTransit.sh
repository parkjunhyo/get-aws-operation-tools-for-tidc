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
EssFILE=$NetAdmDIR/$FilePrefixValidAccountfromTransitAttachment-$TransitAttachmentFile

if [ ! -f $EssFILE ]
then
	echo "[error] run getAWStransitAttachment.sh"
	exit
fi

# Update NetworkAccount
if [ ! -f $SecretDIR/$SecretCredentialFile ]
then
	echo "[error] run getAccountCredentials.sh"
	exit
fi
source $SecretDIR/$SecretCredentialFile

# Create Directory for Network Account
if [ ! -d ./$NetAdmDIR ]
then
	        mkdir ./$NetAdmDIR
fi

# find out origin route table
rm -rf ./$NetAdmDIR/"$FilePrefixRoutefromTransit"*"$NetworkAccountID"

while read stringLine
do
	read -a strarr <<< $stringLine
	ACCNum=${strarr[0]}
	VPCResourceID=${strarr[1]}
	TGWattachID=${strarr[2]}
	RouteTableID=${strarr[4]}
        # Origin FileName
	OutFILE="$NetAdmDIR/$FilePrefixRoutefromTransit-$RouteTableID-$NetworkAccountID"
	returnMsg=$(aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id $RouteTableID  --filters "Name=attachment.transit-gateway-attachment-id,Values=$TGWattachID")
	if [ ${#returnMsg} -ne 0 ]
	then
		echo "$returnMsg," >> $OutFILE
	fi
	## in Python ==> ReadJson = json.loads("{\"result\":["+",".join(f.read()[:-1])+"]}")
	# display processing
	echo -n "!"
done < ./$EssFILE

# clear Env variable
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

