'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

import pickle
import threading
import collections
import Messages
import os
import sys

class SimOptions(object):
    '''
    This class stores the options that control the basic paramaters of the simulation
    '''
    def __init__(self, toCopy = None):
        if toCopy is None:
            self.autolearnChannels = True
            self.childPythonName = ""
            self.topoFileName = ""
            self.noiseFileName = ""
            self.channelList = list()
            self.opsPerSecond = 10000000
            self.name = ""
        else:
            self.autolearnChannels = toCopy.autolearnChannels
            self.childPythonName = toCopy.childPythonName
            self.topoFileName = toCopy.topoFileName
            self.noiseFileName = toCopy.noiseFileName
            self.channelList = list(toCopy.channelList)
            self.opsPerSecond = toCopy.opsPerSecond
            self.name = toCopy.name

      
class SimOutput(object):
    '''
    This class stores a list of channels, nodes, and message types shown by an output window
    ''' 
    
    def __init__(self):
        self.selectedChannels = list();
        self.selectedTypes = list();
        self.selectedNodes = list();
        
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
        
        for line in fileData:
            parts = line.rstrip().rsplit(" ")
            if len(parts) <= 1:
                continue;
            fromNode = int(parts[0]);
            toNode = int(parts[1]);
            self.AddConnection(fromNode, toNode)
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
        
        
class SimPresets(object):
    '''
    Used to easily pickle all current presets
    ''' 
    
    def __init__(self):
        self.outputPresets = list() #list of all saved output window presets
        self.configPresets = list() #List of all SimOptions stored presets
        self.topoHistory = list()
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

    def AttemptTopoLoad(self, topoFile):
        try:
            self.currentTopo = SimTopo(topoFile)
            return True
        except:
            self.currentTopo = SimTopo()
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