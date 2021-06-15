#! /usr/bin/env python3

import sys,re,json,os,glob

class MainFunction:
    def run(self, argv):
        if not os.path.isfile("runcommand-config.cfg"):
            print("[error] runcommand-config.cfg is not existed")
            sys.exit
        with open("runcommand-config.cfg","r") as f:
            contentsList=f.readlines()
        # find Directory
        NetAdmDIR=""
        for msg in contentsList:
            if re.search("^NetAdmDIR=",msg):
                NetAdmDIR=re.split('=|\"',msg)[-2]
                break
        if not NetAdmDIR:
            print("[error] NetAdmDIR not in runcommand-config.cfg is not existed")
            sys.exit
        # find Pattern for route information
        FilePrefixRoutefromTransit=""
        for msg in contentsList:
            if re.search("^FilePrefixRoutefromTransit=",msg):
                FilePrefixRoutefromTransit=re.split('=|\"',msg)[-2]
                break
        if not FilePrefixRoutefromTransit:
            print("[error] FilePrefixRoutefromTransit not in runcommand-config.cfg is not existed")
            sys.exit
        # List route table information
        routeALL=[]
        for fNAME in glob.glob("{}/{}*".format(NetAdmDIR, FilePrefixRoutefromTransit)):
            with open(fNAME, "r") as f:
                ReadJson=json.loads("{} {} {}".format("{\"result\":[",",".join(f.read().split(",")[:-1]),"]}"))
                for component in ReadJson["result"]:
                    for entry in component["Routes"]:
                        routeALL.append(entry)
        # find Directory
        userDIR=""
        for msg in contentsList:
            if re.search("^userDIR=",msg):
                userDIR=re.split('=|\"',msg)[-2]
                break
        if not userDIR:
            print("[error] userDIR not in runcommand-config.cfg is not existed")
            sys.exit
        # find Pattern for Network Interface
        FilePrefixNetInterfaces=""
        for msg in contentsList:
            if re.search("^FilePrefixNetInterfaces=",msg):
                FilePrefixNetInterfaces=re.split('=|\"',msg)[-2]
                break
        if not FilePrefixNetInterfaces:
            print("[error] FilePrefixNetInterfaces not in runcommand-config.cfg is not existed")
            sys.exit
        # List Network Interface
        netInterfaceALL=[]
        for fNAME in glob.glob("{}/{}*".format(userDIR, FilePrefixNetInterfaces)):
             with open(fNAME, "r") as f:
                 ReadJson=json.loads("{} {} {}".format("{\"result\":[",",".join(f.read().split(",")[:-1]),"]}"))
                 print(ReadJson)
                 #for component in ReadJson["result"]:
                 #    print(component)

                    

if __name__=="__main__":
    if len(sys.argv) == 1:
        F = MainFunction()
        F.run(sys.argv)
    else:
        sys.exit

