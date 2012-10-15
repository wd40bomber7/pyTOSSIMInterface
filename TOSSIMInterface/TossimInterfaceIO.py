'''
Created on Oct 12, 2012

@author: wd40bomber7
'''
import Simulation
from threading import Thread;
import subprocess;
import sys;
import time;

class InterfaceIO(object):
    '''
    Handles input through bound stdio
    '''

    def __init__(self,sim,pythonToBind):
        '''
        Constructor
        '''
        self.__runInputOutput = True
        self.sim = sim;
        
        self.p = subprocess.Popen(["python",pythonToBind],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        
        self.__inputThread = Thread(None,self.__handleInput,None,())
        self.__outputThread = Thread(None,self.__handleOutput,None,())
        
        self.__inputThread.daemon = True;
        self.__outputThread.daemon = True;
        self.__inputThread.start();
        self.__outputThread.start();
        
    def StopThreads(self):
        self.__runInputOutput = False;
        self.__outputThread.join();
        
    def __handleInput(self):
        while self.__runInputOutput and (not self.p.stdout.closed):
            line = self.p.stdout.readline()
            self.sim.simulationState.ioQueues.QueueInput(line.rstrip());
    def __handleOutput(self):
        while self.__runInputOutput and (not self.p.stdin.closed):
            try:
                time.sleep(1.0/100.0); #no faster than this
                lines = self.sim.simulationState.ioQueues.LiquidateOutputQueue();
                for line in lines:
                    self.p.stdin.write(line + "\n")
                self.p.stdin.flush();
            except:
                time.sleep(1.0/10000.0)
            
    #Automatic sliding sleep time. Uses least amount of cpu time necessary
    def __processInput(self):
        sleepTime = 1.0/10.0
        while self.__runInputOutput:
            lines = self.sim.simulationState.ioQueues.LiquidateInputQueue();
            if len(lines) <= 0:
                sleepTime = min(1.0/5.0,sleepTime*1.3)
            else:
                sleepTime = max(1.0/100.0,sleepTime/1.3)
                for line in lines:
                    if line[0] != "_":
                        try:
                            self.sim.simulationState.messages.ParseAndAppend(line);
                        except:
                            print "Malformed message[" + line + "]";
                    else:
                        self.sim.simulationState.ioQueues.QueueCommand()
                    
                    
            time.sleep(sleepTime)        
            