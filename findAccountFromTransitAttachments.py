#! /usr/bin/env python3

import sys,re,json,os

class MainFunction:
    def run(self, argv):
        fName=argv[-1]
        if os.path.isfile(fName):
            with open(fName, "r") as f:
                stingtoJson = json.loads(f.read())
                rearrangeText = []
                for elementDict in stingtoJson['TransitGatewayAttachments']:
                    rearrangeText.append("{} {} {}\n".format(elementDict['ResourceOwnerId'], elementDict['ResourceId'], elementDict['State']))
                # result write in file
                foName="valid-{}".format(fName)
                with open(foName,"w") as fo:
                    fo.writelines(rearrangeText)
        else:
            print("[error] missing parameter : {} [transit-gateway-attachments] ".format(argv[0]))
            sys.exit()


if __name__=="__main__":
    if len(sys.argv) == 2:
        fName=sys.argv[-1]
        if re.search(r"transit-gateway-attachments",fName):
            F = MainFunction()
            F.run(sys.argv)
        else:
            print("[error] missing parameter : {} [transit-gateway-attachments] ".format(sys.argv[0]))
            sys.exit
    else:
        print("[error] missing parameter : {} [transit-gateway-attachments] ".format(sys.argv[0]))
        sys.exit
