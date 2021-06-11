#! /usr/bin/env bash

# Check Configuration file
if [ -f ./runcommand-config.cfg  ]
then
	source ./runcommand-config.cfg
else
	echo "[error] missing runcommand-config.cfg file!"
	exit
fi

# Generate Network Credential 
if [ ! -f ./$SecretCredentialFile ]
then
	./getNetworkCredential.sh
fi

source ./$SecretCredentialFile

# Create Result File Name
TransitAttachmentFile="transit-gateway-attachments-$NetworkAccountID"
TransitAttachmentFileLocation="./$TransitAttachmentFile"

# Run GET Transit Gateway Attachment
aws ec2 describe-transit-gateway-attachments > $TransitAttachmentFile

# Run re Arrange the file
./findAccountFromTransitAttachments.py $TransitAttachmentFile

# Unset Environment
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
