#! /usr/bin/env bash

# Check Configuration file
if [ -f ./runcommand-config.cfg  ]
then
	source ./runcommand-config.cfg
else
	echo "[error] missing runcommand-config.cfg file!"
	exit
fi

# Veridation for credential
NTIME=$(date +"%s")
ExpTIME=$(expr $NTIME + $ExpiredTimeDurationSecond)
if [ -f $SecretCredentialFile ]
then
	ReferenceTIME=$(cat $SecretCredentialFile | grep -i "ExpectedTimeforExprie" | awk '{print $(NF-1)}')
	if [ $NTIME -le $ReferenceTIME ]
	then
		echo "[notice] $SecretCredentialFile is still valid"
		exit
	fi
fi

# Get the Credential for Network Account
aws sts assume-role --role-arn arn:aws:iam::$NetworkAccountID:role/SKTNetworkToolRole --role-session-name temprole-$NetworkAccountID --external-id $ExternalID > $TempFile

echo "# ExpectedTimeforExprie : $ExpTIME #" > $SecretCredentialFile
echo "export AWS_ACCESS_KEY_ID=$(cat $TempFile | grep -i AccessKeyId | awk -F"[\"]" '{print $4}')" >> $SecretCredentialFile
echo "export AWS_SECRET_ACCESS_KEY=$(cat $TempFile | grep -i SecretAccessKey | awk -F"[\"]" '{print $4}')" >> $SecretCredentialFile
echo "export AWS_SESSION_TOKEN=$(cat $TempFile | grep -i SessionToken | awk -F"[\"]" '{print $4}')" >> $SecretCredentialFile

if [ -f $TempFile ]
then
	rm -rf $TempFile
fi

