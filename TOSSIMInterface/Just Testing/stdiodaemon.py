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
    
    def __ini