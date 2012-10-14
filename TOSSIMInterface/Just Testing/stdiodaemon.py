'''
Created on Oct 13, 2012

@author: wd40bomber7
'''

if __name__ == '__main__':
    pass

from threading import Thread;
import socket;
import sys;
import subprocess;
from Simulation import SimQueues

print "starting" #["python","randomtest.py"]
p = subprocess.Popen(["python","randomtest.py"],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
print "working"

p.stdin.write("Good thank you =)\r\n")
#p.stdin.flush();

while not p.stdout.closed:
    #print "iterating"
    read = p.stdout.readline()
    if (len(read)) == 0:
        break;
    print read.rstrip();

print "DONE"
sys.exit(0);

if len(sys.argv) != 3:
    print 'usage : stdiodaemno <port> <program to bind to>'
    sys.exit(1)

port = int(sys.argv[1])
program = sys.argv[2]



def ManageNetworkInput():
    '''
    does stuff
    '''
def ManageStdioInput():
    '''
    more stuff
    '''


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
c, addr = s.accept()     # Only one client per daemon
