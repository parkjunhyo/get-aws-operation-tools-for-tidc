# at first get the network account credential for IAM user

run getNetworkCredential.sh

# In second, get the transit gateway attachment information

run getAWStransitAttachment.sh

# Get the Route table with attachemtn information
run getRoutesfromTransit.sh

# Get Account Credential
# This will be used find out the Virtual Interface Usage and Compare
run getAccountCredentials.sh
