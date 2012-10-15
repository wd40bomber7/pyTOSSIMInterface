'''
Created on Oct 14, 2012

@author: wd40bomber7
'''

import _TOSSIM
import sys
import threading
import time
import collections
from TOSSIM import *
from packet import *

topoLoaded = False
noiseLoaded = False
nodesLoaded = False
channelsLoaded = False

nodeList = []

t = Tossim([])
r = t.radio()

while True:
    cmd = sys.stdin.readline().rstrip().rsplit(" ")
    
    if cmd[0] == "Settopo":
        try:
            f = open(cmd[1], "r")
            for line in f:
                s = line.split()
                if s:
                    r.add(int(s[0]), int(s[1]), float(s[2]))
        except:
            print "_topoloaded failure"
            sys.stdout.flush()
            sys.exit(1)
        print "_topoloaded success"
        sys.stdout.flush()
        topoLoaded = True
    elif cmd[0] == "Setnoise":
        if not nodesLoaded:
            print "_exception 3"
            sys.stdout.flush()
            sys.exit(1)
        try:
            noise = open("no_noise.txt", "r")
            for line in noise:
                str1 = line.strip()
                if str1:
                    val = int(str1)
                    for i in nodeList:
                        t.getNode(i).addNoiseTraceReading(val)
        except:
            print "_noiseloaded failure"
            sys.stdout.flush()
            sys.exit(1)
        print "_noiseloaded success"
        sys.stdout.flush()
        noiseLoaded = True
    elif cmd[0] == "Nodelist":
        nodes = cmd[1].rsplit(",")
        for n in nodes:
            nodeList.append(int(n))
        nodesLoaded = True
    elif cmd[0] == "Channellist":
        channelList = cmd[1].rsplit(",")
        for channel in channelList:
            t.addChannel(channel, sys.stdout)
        channelsLoaded = True
    elif cmd[0] == "Startsimulation":
        break

if (not topoLoaded) or (not noiseLoaded) or (not nodesLoaded) or (not channelsLoaded):
    print "_exception 4"
    sys.stdout.flush()
    sys.exit(1)
    
for i in nodeList:
    t.getNode(i).createNoiseModel()

for i in nodeList:
    t.getNode(i).bootAtTime(1000 + i * 111);
    
def package(string):
    ints = []
    for c in string:
        ints.append(ord(c))
    return ints

def run(ticks):
    for i in range(ticks):
        t.runNextEvent()

def sendCMD(string):
    args = string.split(' ');
    msg.set_src(int(args[0]));
    msg.set_dest(int(args[1]));
    payload=args[2];
    for i in range(3, len(args)):
        payload= payload + ' '+ args[i]
    
    msg.setString_payload(payload)
    
    pkt.setData(msg.data)
    pkt.setDestination(int(args[1]))

    pkt.deliver(int(args[1]), t.time()+5)
    run(10);

simulationPaused = False
simulationRunning = True
    
def handleInput():
    global cmdBuffer
    global simulationPaused
    global simulationRunning
    while True:
        oCmd = sys.stdin.readline().rstrip()
        cmd = oCmd.rsplit(" ")
        if cmd[0] == "Pausesimulation":
            simulationPaused = not simulationPaused;
        elif cmd[0] == "Stopsimulation":
            simulationRunning = False
            simulationPaused = False
            return
        elif cmd[0] == "Injectpacket":
            cmdBuffer.append((int(cmd[1]),oCmd[len(cmd[0] + " " + cmd[1]):]))
        
    
cmdBuffer = collections.deque();
cmdQueueProtection = threading.RLock()
inputThread = threading.Thread(None,handleInput,None,())
inputThread.daemon = True
inputThread.start()
currentSequence = 9000


msg = pack()
msg.set_seq(9999)
msg.set_TTL(15)
msg.set_protocol(99)
pkt = t.newPacket()
pkt.setData(msg.data)
pkt.setType(msg.get_amType())


while simulationRunning:
    run(2000)
    cmdQueueProtection.acquire()
    while len(cmdBuffer) > 0:
        cmd = cmdBuffer.popleft()
        currentSequence += 1
        msg.set_seq(currentSequence)
        msg.set_protocol(cmd[0])
        sendCMD(cmd[1])
    cmdQueueProtection.release()
    while simulationPaused:
        time.sleep(.25)