#! /usr/bin/env python3

import sys,re,json,os

class MainFunction:
    def run(self, argv):
        fName=argv[1]
        foPrefix=argv[2]
        if os.path.isfile(fName):
            with open(fName, "r") as f:
                stingtoJson = json.loads(f.read())
                rearrangeText = []
                for elementDict in stingtoJson['TransitGatewayAttachments']:
                    rearrangeText.append("{} {} {} {} {} {}\n".format(elementDict['ResourceOwnerId'], elementDict['ResourceId'], elementDict['TransitGatewayAttachmentId'], elementDict['State'], elementDict['Association']['TransitGatewayRouteTableId'], elementDict['Association']['State']))
                # result write in file
                splitedfNameList=fName.split("/")
                foName="{}-{}".format(foPrefix,splitedfNameList[-1])
                splitedfNameList[-1]=foName
                foNameLocation="/".join(splitedfNameList)
                with open(foNameLocation,"w") as fo:
                    fo.writelines(rearrangeText)
        else:
            print("[error] missing parameter : {} [transit-gateway-attachments] ".format(argv[0]))
            sys.exit()


if __name__=="__main__":
    if len(sys.argv) == 3:
        fName=sys.argv[1]
        if re.search(r"transit-gateway-attachments",fName):
            F = MainFunction()
            F.run(sys.argv)
        else:
            print("[error] missing parameter : {} [transit-gateway-attachments][prefix-forReturn] ".format(sys.argv[0]))
            sys.exit
    else:
        print("[error] missing parameter : {} [transit-gateway-attachments][prefix-forReturn] ".format(sys.argv[0]))
        sys.exit

