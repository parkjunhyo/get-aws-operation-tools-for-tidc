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

# Create Directory for Network Account
if [ ! -d ./$userDIR ]
then
	mkdir ./$userDIR
fi

if [ -f $userDIR/$FilePrefixNetInterfaces ]
then
	rm -rf $userDIR/$FilePrefixNetInterfaces
fi

# Read File
rFILE=$NetAdmDIR/$FilePrefixValidAccountfromTransitAttachment-$TransitAttachmentFile
while read stringLine
do
	read -a strarr <<< $stringLine
	ACCNum=${strarr[0]}
	VPCIDnum=${strarr[1]}
	# switch account
	ENVSource=$SecretDIR/"secret-credential-"$ACCNum
	source $ENVSource
	# run Command
	returnMsg=$(aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$VPCIDnum")
	if [ ${#returnMsg} -ne 0 ]
	then
		echo "$returnMsg," >> $userDIR/$FilePrefixNetInterfaces
	fi
	# disable environment
	./disableSecret.sh
	# Display processing
	echo -n "!"
done < $rFILE

# Unset Environment
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
