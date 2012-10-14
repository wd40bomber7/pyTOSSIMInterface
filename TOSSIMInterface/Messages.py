'''
Created on Oct 12, 2012

@author: wd40bomber7
'''

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
        __storedMessages = list();
        
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
        
        
        self.__storedMessages.append(message)
        
    def RetrieveFilteredList(self,allowedTypes,allowedChannels,allowedNodes):
        filteredList = list()
        for message in self.__storedMessages:
            if not (message.messageType in allowedTypes):
                continue
            if not (message.nodeId in allowedNodes):
                continue
            if message.ContainsChannelFromList(allowedChannels):
                filteredList.append(message);
        
        return filteredList
        