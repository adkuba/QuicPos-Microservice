from paramiko import SSHClient
from scp import SCPClient
from os import listdir
from os.path import isfile, join
import sys

def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )

def sendFiles():

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('142.93.232.180', username='root', password='funia20Quic')
    scp = SCPClient(ssh.get_transport(), progress4=progress4)

    #send detector
    mypath = 'out/detector/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in files:
        scp.put(mypath + file, '~/out/detector/' + file)
    #varaibles
    mypath = 'out/detector/variables/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in files:
        scp.put(mypath + file, '~/out/detector/variables/' + file)


    #send recommender
    mypath = 'out/recommender/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in files:
        scp.put(mypath + file, '~/out/recommender/' + file)
    #varaibles
    mypath = 'out/recommender/variables/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in files:
        scp.put(mypath + file, '~/out/recommender/variables/' + file)

    scp.close()