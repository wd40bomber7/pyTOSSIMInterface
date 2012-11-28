'''
Created on Oct 12, 2012

@author: wd40bomber7
'''
import threading
import collections

class MessageType(object):
    Error = 0;
    Debug = 1;

class Message(object):
    '''
    Stores a single message and the details that can be used for filtering it
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.messageText = "";
        self.nodeId = 0;
        self.channelList = []; #one message can have multiple channels
        self.messageType = MessageType.Debug;
        self.topoMessage = False;
        self.topoSlot = -1;
        
    def ContainsChannelFromList(self,channelList):
        '''
        returns true if any of the channels this was broadcasted on is on channelLis
        '''
        for channel in channelList:
            if channel in self.channelList:
                return True;
            
        return False;
        
class MessagePool(object):
    '''
    Stores up 5000 message objects. Can be filtered on demand
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.messagesLock = threading.RLock()
        self.__storedMessages = list(); #collections.deque();
        #self.__bufferSlider = 0 #Used to fool outsiders into thinking a buffer has infinite depth when it's fixed depth
    def ClearAll(self):
        self.__storedMessages = list();
    def ParseAndAppend(self, unparsedMessage):
        message = Message();
        cutup = unparsedMessage.rsplit(" ")
        if len(cutup) < 3:
            raise Exception("MalformedMessage0")
        
        if cutup[0] == "DEBUG":
            message.messageType = MessageType.Debug
        elif cutup[0] == "ERROR":
            message.messageType = MessageType.Error
        else:
            raise Exception("MalformedMessage1")
        
        try:
            message.nodeId = int(cutup[1][1:][:-2]) #Slicing is pretty cool
        except:
            raise Exception("MalformedMessage2")
        
        message.channelList = cutup[2].rsplit(",");
        if len(cutup) > 3:
            message.messageText = unparsedMessage[len(cutup[0])+len(cutup[1])+len(cutup[2])+3:]
        
        if len(message.messageText) > 1:
            if message.messageText[0] == "_":
                parts = message.messageText.split("_")
                try:
                    message.topoSlot = int(parts[1])
                    message.messageText = message.messageText[len(parts[1])+2:]
                except:
                    message.topoSlot = -1
                
        
        self.messagesLock.acquire()
        #due to buffer mechanic, it is currently infinitly large.
        #if len(self.__storedMessages) >= 2000: #current max buffer
            #self.__storedMessages.popleft();
        self.__storedMessages.append(message)
        self.messagesLock.release()
        return message
        
    def RetrieveFilteredList(self,allowedTypes,allowedChannels,allowedNodes,readPosition=0):
        filteredList = list()
        self.messagesLock.acquire()
        newReadPosition = len(self.__storedMessages)
        for i in range(readPosition,newReadPosition) :
            message = self.__storedMessages[i]
            if message.messageType in allowedTypes:
                continue
            if message.nodeId in allowedNodes:
                continue
            if not message.ContainsChannelFromList(allowedChannels):
                filteredList.append(message);

        self.messagesLock.release()
        return (newReadPosition,filteredList)
        