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

# Generate Network Credential 
if [ ! -f ./$SecretDIR/$SecretCredentialFile ]
then
	./getNetworkCredential.sh
fi

# Switch to Network Account
source ./$SecretDIR/$SecretCredentialFile


# Create Directory for Network Account
if [ ! -d ./$NetAdmDIR ]
then
	mkdir ./$NetAdmDIR
fi

# Run GET Transit Gateway Attachment
aws ec2 describe-transit-gateway-attachments > ./$NetAdmDIR/$TransitAttachmentFile

# Run re Arrange the file
./findAccountFromTransitAttachments.py ./$NetAdmDIR/$TransitAttachmentFile $FilePrefixValidAccountfromTransitAttachment

# Unset Environment
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
