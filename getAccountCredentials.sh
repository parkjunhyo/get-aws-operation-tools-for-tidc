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

rFILEname="$FilePrefixValidAccountfromTransitAttachment-$TransitAttachmentFile"

for ACNum in $(cat $rFILEname | awk '{print $1}')
do
	# Verfication for credentional
	NTIME=$(date +"%s")
	ExpTIME=$(expr $NTIME + $ExpiredTimeDurationSecond)
	ACSecretCredentialFile="./secret-credential-$ACNum"
	if [ -f $ACSecretCredentialFile ]
	then
		ReferenceTIME=$(cat $ACSecretCredentialFile | grep -i "ExpectedTimeforExprie" | awk '{print $(NF-1)}')
		if [ $NTIME -le $ReferenceTIME ]
		then
			continue
		fi
	fi
	# Get Origin Result
	aws sts assume-role --role-arn arn:aws:iam::$ACNum:role/SKTNetworkToolRole --role-session-name temprole-$ACNum --external-id $ExternalID > $TempFile
	# Arrange and rewrite Result from Orign
	echo "# ExpectedTimeforExprie : $ExpTIME #" > $ACSecretCredentialFile
	echo "export AWS_ACCESS_KEY_ID=$(cat $TempFile | grep -i AccessKeyId | awk -F"[\"]" '{print $4}')" >> $ACSecretCredentialFile
	echo "export AWS_SECRET_ACCESS_KEY=$(cat $TempFile | grep -i SecretAccessKey | awk -F"[\"]" '{print $4}')" >> $ACSecretCredentialFile
	echo "export AWS_SESSION_TOKEN=$(cat $TempFile | grep -i SessionToken | awk -F"[\"]" '{print $4}')" >> $ACSecretCredentialFile
	# Delete Origin
	if [ -f $TempFile ]
	then
		rm -rf $TempFile
	fi
done
