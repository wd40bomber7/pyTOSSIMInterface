'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

import pickle
import threading
import collections
import Messages

class SimOptions(object):
    '''
    This class stores the options that control the basic paramaters of the simulation
    '''
    def __init__(self):
        self.autolearnChannels = True
        self.childPythonName = ""
        self.channelList = list()
        self.opsPerSecond = 10000000
        self.name = ""

      
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
    
    def __init__(self):
        self.canReceiveFromList = list() #List of node objects
        self.canSendToList = list()      #List of node objects
        self.bidirectionalList = list()  #List of node objects
        self.myId = 0;
    
    def AddNodeThatCanBeSentTo(self, node,connectionStrength):
        '''
        Adds a node that this node has a send to connection to
        '''
        
        for c in self.canReceiveFromList:
            if c.connectTo == node:
                self.canReceiveFromList.remove(c) #TODO: Add support for bidirectional connections with different connection strengths
                self.bidirectionalList.append(c)
                return

        self.canSendToList.append(NodeConnection(node,connectionStrength))
            
    def AddNodeThatCanBeReceivedFrom(self, node, connectionStrength):
        '''
        Adds a node that can hear messages sent by this node
        '''
        for c in self.canSendToList:
            if c.connectTo == node:
                self.canSendToList.remove(c) #TODO: Add support for bidirectional connections with different connection strengths
                self.bidirectionalList.append(c)
                return
            
            self.canReceiveFromList.append(NodeConnection(node,connectionStrength))
    
class SimTopo(object):
    '''
    This class stores all information about every node in the current topo
    ''' 

    def __init__(self,topoFile=None):
        
        self.nodeDict = dict(); #maps a node ids to node objects
        self.topoFileName = ""
        
        if topoFile == None:
            return;
        
        self.topoFileName = topoFile #the topo file this object represents
        #Exceptions passed up
        topoFile = open('presets.bin','r')
        fileData = topoFile.readLines()
        topoFile.close()
        
        for line in fileData:
            parts = line.rsplit(" ")
        
            fromNode = int(parts[0]);
            toNode = int(parts[1]);
            if not (fromNode in self.nodeDict):
                self.nodeDict[fromNode] = SimNode()   
            if not (toNode in self.nodeDict):
                self.nodeDict[toNode] = SimNode()
            
            self.nodeDict[fromNode].AddNodeThatCanBeSentTo(self.nodeDict[toNode],float(parts[2]));
            self.nodeDict[toNode].AddNodeThatCanBeSentTo(self.nodeDict[toNode],float(parts[2]));
        
    
class SimPresets(object):
    '''
    Used to easily pickle all current presets
    ''' 
    
    def __init__(self):
        self.topoFileNames = list() #list of recently used topo files
        self.noiseFileNames = list() #list of recently used noise files
        self.outputPresets = list() #list of all saved output window presets
        self.configPresets = list() #List of all SimOptions stored presets
        
        self.lastTopoFile = "";
        self.lastSimulationOptions = SimOptions();
    
class SimQueues(object):
    '''
    The input/output queues that drive communication to the TOSSIM python script
    '''  
    
    def __init__(self):
        self.queueLock = threading.RLock() #Protects inputQueue, outputQueue, and rawMessageQueue
        self.inputQueue = collections.deque()
        self.outputQueue = collections.deque()
        self.rawMessageQueue = collections.deque()
        
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
    
class SimState(object):
    '''
    Stores the current state of the running simulation
    '''
    
    def __init__(self):
        self.ioQueues = SimQueues()
        self.ioReadWrite = None
        self.messages = Messages.MessagePool()
        self.simIsRunning = False
        self.currentTopo = SimTopo();
    
    
class Sim(object):
    '''
    Stores all data about the current simulation
    ''' 
    
    def __init__(self):
        self.selectedOptions = SimOptions()
        self.savedPresets = SimPresets()
        self.simulationState = SimState()
        #other data
        self.openWindows = list()
    
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
        self.selectedOptions = self.savedPresets.lastSimulationOptions
        
    def SavePresets(self):
        try:
            presetFile = open('presets.bin','wb')
        except:
            return #Uhm? Error TODO:Make this error actually create a modal dialog or something
        
        self.savedPresets.lastSimulationOptions = self.selectedOptions
        pickle.dump(self.savedPresets,presetFile,-1)
        
        presetFile.close()
        
    def DebugPrint(self,text):
        self.simulationState.ioQueues.QueueRaw(text);