'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

import pickle
import threading
import collections
import Messages
import re

class SimOptions(object):
    '''
    This class stores the options that control the basic paramaters of the simulation
    '''
    def __init__(self, toCopy = None):
        if toCopy is None:
            self.topoWindowMap = (0,dict()) #This stores the topo hashcode as the first paramater and the dict of NodeId, X, Y of the window positions
            self.autolearnChannels = True
            self.childPythonName = ""
            self.topoFileName = ""
            self.noiseFileName = ""
            self.channelList = list()
            self.opsPerSecond = 10000000
            self.name = ""
            self.currentStartupScript = None
        else:
            self.topoWindowMap = toCopy.topoWindowMap
            self.autolearnChannels = toCopy.autolearnChannels
            self.childPythonName = toCopy.childPythonName
            self.topoFileName = toCopy.topoFileName
            self.noiseFileName = toCopy.noiseFileName
            self.channelList = list(toCopy.channelList)
            self.opsPerSecond = toCopy.opsPerSecond
            self.name = toCopy.name
            self.currentStartupScript = toCopy.currentStartupScript

      
class SimOutput(object):
    '''
    This class stores a list of channels, nodes, and message types shown by an output window
    ''' 
    
    def __init__(self):
        self.excludedChannels = list();
        self.excludedTypes = list();
        self.excludedNodes = list();
        
        self.displayNodeId = True;
        self.displayChannel = False;
        self.displayType = True;
        
        self.name = ""
    
class NodeConnection(object):
    '''
    Represents a connection between to nodes
    '''
    
    def __init__(self,node,connectionStrength):
        self.connectTo = node;
        self.signalStrength = connectionStrength;
        
class SimNode(object):
    '''
    This class holds all information about a single node
    '''     
    
    def __init__(self,myId):
        self.connectNodes = list()  #List of node objects
        self.myId = myId;
class SimConnection(object):
    '''
    This class holds all information about a node connection
    '''     
    
    def __init__(self,fromNode,toNode):
        self.fromNode = fromNode
        self.toNode = toNode
    
class SimTopo(object):
    '''
    This class stores all information about every node in the current topo
    ''' 

    def __init__(self,topoFile=None):
        self.hashCode = 0
        self.nodeDict = dict(); #maps a node ids to node objects
        self.topoFileName = ""
        self.connectionList = list()
        
        if topoFile == None:
            return;
        
        self.topoFileName = topoFile #the topo file this object represents
        #Exceptions passed up
        topoFile = open(topoFile,'r')
        fileData = topoFile.readlines()
        topoFile.close()
        
        connectionCount = 0
        for line in fileData:
            parts = line.rstrip().rsplit(" ")
            if len(parts) <= 1:
                continue;
            fromNode = int(parts[0]);
            toNode = int(parts[1]);
            self.AddConnection(fromNode, toNode)
            connectionCount += 1
            self.hashCode += fromNode + 16*toNode
            self.hashCode += 256*256*toNode
        self.hashCode += 256*connectionCount
        
    def WriteTopoFile(self):
        fileData = list()
        for connection in self.connectionList:
            fileData.append(str(connection.fromNode) + " " + str(connection.toNode) + " -54.0\n")
        topoFile = open(self.topoFileName,'w')
        topoFile.writelines(fileData)  
        topoFile.close()
        
    def AddConnection(self,fromNode,toNode):
        for connection in self.connectionList:
            if connection.fromNode == fromNode and connection.toNode == toNode:
                return
            #elif connection.fromNode == toNode and connection.toNode == fromNode:
            #    return
            
        self.connectionList.append(SimConnection(fromNode,toNode))
        if not (fromNode in self.nodeDict):
            self.nodeDict[fromNode] = SimNode(fromNode)   
        if not (toNode in self.nodeDict):
            self.nodeDict[toNode] = SimNode(toNode)
        
        if not self.nodeDict[toNode] in self.nodeDict[fromNode].connectNodes:
            self.nodeDict[fromNode].connectNodes.append(self.nodeDict[toNode])
        if not self.nodeDict[fromNode] in self.nodeDict[toNode].connectNodes:
            self.nodeDict[toNode].connectNodes.append(self.nodeDict[fromNode])
            
    def RemoveNode(self, nodeId, redoNodes=True):
          
        self.connectionList[:] = [i for i in self.connectionList if i.fromNode != nodeId and i.toNode != nodeId]
        node = self.nodeDict[nodeId]                  
        del self.nodeDict[nodeId]
        
        toDelete = list()
        for neighbor in node.connectNodes:
            neighbor.connectNodes.remove(node)
            if len(neighbor.connectNodes) <= 0:
                toDelete.append(neighbor)
        node = None
        for neighbor in toDelete:
            if neighbor.myId in self.nodeDict:
                self.RemoveNode(neighbor.myId,False)
        
        if redoNodes:
            self.RedoNumbers()
    def __FilterConnection(self, connection):
        fromNodeId = self.connectionToRemove.fromNode
        toNodeId = self.connectionToRemove.toNode
        if connection.fromNode == fromNodeId and connection.toNode == toNodeId:
            print "dropped connection"
            return False
        elif connection.toNode == fromNodeId and connection.fromNode == toNodeId:
            print "dropped other connection"
            return False     
        return True           
    def RemoveConnection(self, fromNodeId, toNodeId):
        self.connectionToRemove = SimConnection(fromNodeId,toNodeId)
        self.connectionList = filter(self.__FilterConnection,self.connectionList)
        
        fromNode = self.nodeDict[fromNodeId]
        toNode = self.nodeDict[toNodeId]
        
        fromNode.connectNodes.remove(toNode)
        toNode.connectNodes.remove(fromNode)
        if len(fromNode.connectNodes) <= 0:
            self.RemoveNode(fromNodeId,False)
        if len(toNode.connectNodes) <= 0:
            self.RemoveNode(toNodeId,False)
        self.RedoNumbers()
        
    def AddNode(self, connectedToNode):
        
        nodeId = len(self.nodeDict)+1
        print "Using nodeid " + str(nodeId)
        self.nodeDict[nodeId] = SimNode(nodeId)
        node = self.nodeDict[nodeId]
        self.connectionList.append(SimConnection(nodeId,connectedToNode.myId))
        self.connectionList.append(SimConnection(connectedToNode.myId,nodeId))
        connectedToNode.connectNodes.append(node)
        node.connectNodes.append(connectedToNode)
        
        
    def RedoNumbers(self):
        reId = dict()
        iterator = 0
        allNodes = list()
        #Build a transformation dictionary (old node ids to new node ids)
        for nodeId in self.nodeDict:
            iterator += 1
            reId[nodeId] = iterator
            allNodes.append(self.nodeDict[nodeId])
        self.nodeDict.clear()
        for node in allNodes:
            node.myId = reId[node.myId]
            self.nodeDict[node.myId] = node
        for connection in self.connectionList:
            connection.fromNode = reId[connection.fromNode]
            connection.toNode = reId[connection.toNode]
            #print "[" + str(connection.fromNode) + "->" + str(connection.toNode) + "]"
class SimInject(object):
    '''
    An inject ready to be sent as a packet
    '''
    def __init__(self,toInject,src,dst,protocol,selected=None):
        self.isValid = False
        self.sendAtTime = 0
        self.src = src
        self.dst = dst
        self.protocol = protocol
        self.injection = toInject
        self.injection = self.injection.replace("%src%",str(src))
        self.injection = self.injection.replace("%dst%",str(dst))
        if not selected is None:
            self.injection = self.injection.replace("%sel%",str(selected))
        if not "%" in self.injection:
            self.isValid = True
        
    
class SimScript(object):
    '''
    Holds a script made to be written as injection commands at the start of the simulation
    '''
    
    def __init__(self,name):
        self.name = name
        self.script = ""
        self.injectList = list()
        #0005:15:4 5-7 Hello world!
        #0020:99:1-4 11 cmd ping %src%
        #0030:99:1 1-4 cmd kill  
    def BuildInjectList(self):
        #Try to build the list. May throw exceptions
        self.injectList = list()
        scriptIterator = iter(self.script.splitlines())
        for line in scriptIterator:
            self.__buildLine(line)
        
    def __buildLine(self,line):
        #First double check you have the minimum space count
        splitBySpaces = re.findall("\w+",line)
        if len(splitBySpaces) < 2:
            raise Exception("Incorrect number of segments. (Missing spaces)")
        #Now check for minimum colons
        splitByColon = line.split(':')
        if len(splitByColon) < 3:
            raise Exception("Incorrect number of segments[" + str(len(splitByColon)) + "]. (Missing colons)")
        
        issueAtTime = int(splitByColon[0])
        if issueAtTime < 0:
            return False
        issueOnProtocol = int(splitByColon[1])
        if issueOnProtocol < 0:
            return False
        
        #This line is a little tricky. We're looking for the first number or range of numbers which is the source
        #it usually is directly to the right of the second colon, but there may be an additional space
        #By using leftstrip we get rid of any possible spaces between that colon and the src
        #then we split by spaces so we only get the source, and finally we split by - so we can easily check
        #if we have a range or not
        filteredSrc = splitByColon[2].lstrip().split(" ")[0].split("-")
        if len(filteredSrc) == 1:
            srcCount = 1
            srcId = int(filteredSrc[0])
        else:
            a = int(filteredSrc[0])
            b = int(filteredSrc[1])
            #Calculate the base, and how many nodes there are in the range
            srcCount = max(a,b)-min(a,b)+1
            srcId = min(a,b)
        
        #Now do the same for the dst
        filteredDst = splitByColon[2].lstrip().split(" ")[1].split("-")
        if len(filteredSrc) == 1:
            dstCount = 1
            dstId = int(filteredDst[0])
        else:
            a = int(filteredDst[0])
            b = int(filteredDst[1])
            #Calculate the base, and how many nodes there are in the range
            dstCount = max(a,b)-min(a,b)+1
            dstId = min(a,b)
            
        #Finally uncover the actual injectable command/text
        injectable = " ".join(splitByColon[2].lstrip().split(" ")[2:])
        
        #Current implementation requires one source per destination in multi src, multi dst, situations
        if (srcCount > 1) and (dstCount > 1) and (dstCount != srcCount):
            raise Exception("Mismatched source to destination count")
        elif (srcCount > 1) and (dstCount > 1):
            #Map 1 -> 1 nodes
            for x in xrange(0,srcCount):
                inject = SimInject(injectable,srcId+x,dstId+x,issueOnProtocol)
                inject.sendAtTime = issueAtTime
                self.injectList.append(inject)
        elif srcCount > 1:
            for x in xrange(0,srcCount):
                inject = SimInject(injectable,srcId+x,dstId,issueOnProtocol)
                inject.sendAtTime = issueAtTime
                self.injectList.append(inject)
        elif dstCount > 1:
            for x in xrange(0,dstCount):
                inject = SimInject(injectable,srcId,dstId+x,issueOnProtocol)
                inject.sendAtTime = issueAtTime
                self.injectList.append(inject)
        else:
            #Directly one to one
            inject = SimInject(injectable,srcId,dstId,issueOnProtocol)
            inject.sendAtTime = issueAtTime
            self.injectList.append(inject)
       
class SimPresets(object):
    '''
    Used to easily pickle all current presets
    ''' 
    
    def __init__(self):
        self.outputPresets = list() #list of all saved output window presets
        self.configPresets = list() #List of all SimOptions stored presets
        self.topoHistory = list() #List of most recently opened/edited topo files
        self.startScripts = list() #List of all defined startup scripts
        
        #This is used to store the options when they are being overriden by -o
        #It should not be modified directly. Instead modify selectedOptions from the sim object
        self.lastSimulationOptions = SimOptions()
        
    def addTopo(self,topoFile):
        if topoFile in self.topoHistory:
            self.topoHistory.remove(topoFile)
        elif len(self.topoHistory) == 5:
            self.topoHistory.remove(self.topoHistory[0]);
        self.topoHistory.append(topoFile)
    
class SimQueues(object):
    '''
    The input/output queues that drive communication to the TOSSIM python script
    '''  
    
    def __init__(self):
        self.queueLock = threading.RLock() #Protects inputQueue, outputQueue, and rawMessageQueue
        self.inputQueue = collections.deque()
        self.outputQueue = collections.deque()
        self.rawMessageQueue = collections.deque()
        self.cmdQueue = collections.deque()
        self.messagesDropped = 0
    
    def LiquidateInputQueue(self):
        self.queueLock.acquire()
        liquidatedQueue = list();
        while len(self.inputQueue) > 0:
            liquidatedQueue.append(self.inputQueue.popleft())
        self.inputQueue.clear()
        self.queueLock.release();
        return liquidatedQueue
    
    def LiquidateOutputQueue(self):
        self.queueLock.acquire()
        liquidatedQueue = list()
        while len(self.outputQueue) > 0:
            liquidatedQueue.append(self.outputQueue.popleft())
        self.outputQueue.clear()
        self.queueLock.release()
        return liquidatedQueue
    
    def LiquidateRawMessageQueue(self):
        self.queueLock.acquire()
        liquidatedQueue = list();
        while len(self.rawMessageQueue) > 0:
            liquidatedQueue.append(self.rawMessageQueue.popleft())
        self.rawMessageQueue.clear()
        self.queueLock.release();
        return liquidatedQueue
    
    def LiquidateCommandQueue(self):
        self.queueLock.acquire()
        liquidatedQueue = list();
        while len(self.cmdQueue) > 0:
            liquidatedQueue.append(self.cmdQueue.popleft())
        self.cmdQueue.clear()
        self.queueLock.release();
        return liquidatedQueue
    
    def QueueInput(self, inputLine):
        self.queueLock.acquire()
        if len(self.inputQueue) >= 1000:
            self.inputQueue.popleft();
            self.messagesDropped += 1;
        self.inputQueue.append(inputLine);
        self.queueLock.release();
        
    def QueueOutput(self, outputLine):
        self.queueLock.acquire()
        if len(self.outputQueue) >= 1000:
            self.outputQueue.popleft();
            self.messagesDropped += 1;
        self.outputQueue.append(outputLine);
        self.queueLock.release();        
    
    def QueueRaw(self,rawMessageLine):
        self.queueLock.acquire()
        if len(self.rawMessageQueue) >= 1000:
            self.rawMessageQueue.popleft();
            self.messagesDropped += 1;
        self.rawMessageQueue.append(rawMessageLine);
        self.queueLock.release();    
        
    def QueueCommand(self,cmd):
        self.queueLock.acquire()
        if len(self.cmdQueue) >= 1000:
            self.cmdQueue.popleft();
            self.messagesDropped += 1;
        self.cmdQueue.append(cmd);
        self.queueLock.release();    
    
class SimState(object):
    '''
    Stores the current state of the running simulation
    '''
    
    def __init__(self):
        self.ioQueues = SimQueues()
        self.ioReadWrite = None
        self.messages = Messages.MessagePool()
        self.simIsRunning = False
        self.simIsPaused = False
        self.currentTopo = SimTopo()
        self.timeAtLastResume = 0.0 #The time in seconds since the epoch, when the last time "start" or "resume" was pressed
        self.timeBeforeLastResume = 0.0 #The total time the simulation ran before the pause button was pressed last time
        self.scriptPosition = -1.0 #The elapsed time for which all injects have been handled already
        self.currentStartupScript = None

    def AttemptTopoLoad(self, topoFile):
        try:
            self.currentTopo = SimTopo(topoFile)
            print "Loaded " + topoFile
            return True
        except:
            self.currentTopo = SimTopo()
            print "Failed to load [" + topoFile + "]"
            return False

class Sim(object):
    '''
    Stores all data about the current simulation
    ''' 
    
    def __init__(self):
        self.selectedOptions = SimOptions()
        self.savedPresets = SimPresets()
        self.simulationState = SimState()
        #other data
        self.overrideDefaultConfig = False
        self.openWindows = list()
        
    
    def EnableOverride(self):
        self.overrideDefaultConfig = True
        
    def LoadPresets(self):
        try:
            presetFile = open('presets.bin','rb')
        except:
            return #no preset file found. forget it
        
        try:
            self.savedPresets = pickle.load(presetFile)
        except:
            self.savedPresets = SimPresets()
            return #preset file corrupt
        presetFile.close()
        self.selectedOptions = SimOptions(self.savedPresets.lastSimulationOptions)
        self.simulationState.AttemptTopoLoad(self.selectedOptions.topoFileName);
        
    def SavePresets(self):
        try:
            presetFile = open('presets.bin','wb')
        except:
            print "Saving presets failed"
            return #Uhm? Error TODO:Make this error actually create a modal dialog or something
        if not self.overrideDefaultConfig:
            self.savedPresets.lastSimulationOptions = SimOptions(self.selectedOptions)
        pickle.dump(self.savedPresets,presetFile,-1)
        
        presetFile.close()
        
    def DebugPrint(self,text):
        self.simulationState.ioQueues.QueueRaw(text);