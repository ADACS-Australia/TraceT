#!/usr/bin/python

"""Handler daemon, runs continuously and accepts VO-Events in XML format via Pyro from the push_voevent.py
   script (called by the COMET event broker, possibly multiple times in parallel). XML packets are serialised
   in a queue and processed one by one by passing them to one or more plugins, defined in the 'handlers' module.
"""

import ConfigParser
import logging
import socket
import threading
import time
import traceback
import Queue

import Pyro4

from mwa_trigger import fermi_swift

EVENTHANDLERS = [fermi_swift.processevent]    # One or more handler functions - all will be called in turn on each XML event.

Pyro4.config.COMMTIMEOUT = 10.0
Pyro4.config.THREADPOOL_SIZE_MIN = 8
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

REFERENCEIP = '8.8.8.8'  # A host guaranteed to be visible on the network interface that we want the Pyro server to bind to
EXITING = None
PYRO_DAEMON = None

CPPATH = ['/usr/local/etc/trigger.conf', './trigger.conf']   # Path list to look for configuration file


############### set up the logging
class MWALogFormatter(object):
  def format(self,record):
    return "%s: %s" % (time.ctime(), record.getMessage())


LOGLEVEL_CONSOLE = logging.DEBUG      # Logging level for console messages (INFO, DEBUG, ERROR, CRITICAL, etc)
LOGLEVEL_LOGFILE = logging.DEBUG      # Logging level for logfile
LOGFILE = "/var/log/voevents.log"

formatter = MWALogFormatter()

filehandler = logging.FileHandler(LOGFILE)
filehandler.setLevel(LOGLEVEL_LOGFILE)
filehandler.setFormatter(formatter)

consolehandler = logging.StreamHandler()
consolehandler.setLevel(LOGLEVEL_CONSOLE)
consolehandler.setFormatter(formatter)

DEFAULTLOGGER = logging.getLogger('voevent')
DEFAULTLOGGER.addHandler(consolehandler)
DEFAULTLOGGER.addHandler(filehandler)
##############

############## Point to a running Pyro nameserver #####################
# If not on site, start one before running this code, using pyro_nameserver.py
CP = ConfigParser.SafeConfigParser()
CP.read(CPPATH)

if CP.has_option(section='pyro', option='ns_host'):
  Pyro4.config.NS_HOST = CP.get(section='default', option='ns_host')
else:
  Pyro4.config.NS_HOST = 'localhost'

if CP.has_option(section='pyro', option='ns_port'):
  Pyro4.config.NS_PORT = int(CP.get(section='default', option='ns_port'))
else:
  Pyro4.config.NS_PORT = 9090

if Pyro4.config.NS_HOST in ['helios', 'mwa-db']:
  Pyro4.config.SERIALIZER = 'pickle'   # We must be on site, where we have an ancient Pyro4 install and nameserver running


############### Main event handler - receives VOEvent objects by RPC and queues them for processing #################

class VOEventHandler(object):
  """Implements Pyro4 methods that can be called remotely via RPC, to process VO event XML strings.
  """
  def __init__(self, logger=DEFAULTLOGGER):
    self.logger = logger

  @Pyro4.expose
  def ping(self):
    """Empty function, call to see if RPC connection is live.
    """
    pass

  @Pyro4.expose
  def putEvent(self, event=None):
    """Called by the remote client to send a VOEvent XML packet to this server. It just
       pushes the complete XML packet onto the queue for background processing, and returns
       immediately.
    """
    EventQueue.put(event)
    self.logger.info("Queued VOEvent XML, current queue size is %d" % EventQueue.qsize())

  def servePyroRequests(self):
    """When called, start serving Pyro requests.
    """
    global EXITING, PYRO_DAEMON

    iface = None
    self.logger.info('Getting interface address for VOEventHandler Pyro server')
    while iface is None:
      try:
        iface = Pyro4.socketutil.getInterfaceAddress(REFERENCEIP)  # What is the network IP of this receiver?
      except socket.error:
        self.logger.info("Network down, can't start pycontroller Pyro server, sleeping for 10 seconds")
        time.sleep(10)

    ns = None
    while not EXITING:
      self.logger.info("Starting VOEventHandler Pyro4 server")
      if ns is not None:
        try:
          ns._pyroRelease()
        except Pyro4.errors.PyroError:
          pass

      try:
        ns = Pyro4.locateNS()
      except Pyro4.errors.PyroError:
        self.logger.error("Can't locate Pyro nameserver - waiting 10 sec to retry")
        if not EXITING:
          time.sleep(10)
        continue

      try:
        existing = ns.lookup("VOEventHandler")
        self.logger.info("VOEventHandler still exists in Pyro nameserver with id: %s" % existing.object)
        self.logger.info("Previous Pyro daemon socket port: %d" % existing.port)
        # start the daemon on the previous port
        PYRO_DAEMON = Pyro4.Daemon(host=iface, port=existing.port)
        # register the object in the daemon with the old objectId
        PYRO_DAEMON.register(self, objectId=existing.object)
      except (Pyro4.errors.PyroError, socket.error):
        try:
          # just start a new daemon on a random port
          PYRO_DAEMON = Pyro4.Daemon(host=iface)
          # register the object in the daemon and let it get a new objectId
          # also need to register in name server because it's not there yet.
          uri = PYRO_DAEMON.register(self)
          ns.register("VOEventHandler", uri)
        except (Pyro4.errors.PyroError, socket.error):
          if not EXITING:
            self.logger.error("Exception in VOEventHandler Pyro4 startup. Retrying in 10 sec: %s" % (traceback.format_exc(),))
            time.sleep(10)
          else:
            self.logger.error("Exception in VOEventHandler, EXITING is true, shutting down: %s" % (traceback.format_exc(),))
          continue
      except Exception:
        if not EXITING:
          self.logger.error("Exception in VOEventHandler Pyro4 start. Retrying in 10 sec: %s" % (traceback.format_exc(),))
          time.sleep(10)
        else:
          self.logger.error("Exception in VOEventHandler, EXITING true, shutting down: %s" % (traceback.format_exc(),))
        continue

      if not EXITING:
        try:
          ns._pyroRelease()
          PYRO_DAEMON.requestLoop()
        except Exception:
          if not EXITING:
            self.logger.error("Exception in VOEventHandler Pyro4 server. Restarting in 10 sec: %s" % (traceback.format_exc(),))
            time.sleep(10)
          else:
            self.logger.error(
              "Exception in VOEventHandler Pyro4 server, EXITING true, shutting down: %s" % (traceback.format_exc(),))

    PYRO_DAEMON.close()


def QueueWorker():
  """Worker thread to process incoming message packets in the EventQueue. It is spawned on startup, and run continuously,
     blocking on EventQueue.get() if there's nothing to process. When an item is 'put' on the queue, the EventQueue.get()
     returns and the event is processed.
  """
  global EXITING
  while not EXITING:
    eventxml = EventQueue.get()
    DEFAULTLOGGER.info("Processing event, current queue size is %d" % EventQueue.qsize())
    for hfunc in EVENTHANDLERS:
      handled = hfunc(event=eventxml)
      if handled:   # One of the handlers accepted this event
        break    # Don't try any more event handlers.

    EventQueue.task_done()


if __name__ == '__main__':
  EventQueue = Queue.Queue(maxsize=10)

  # Start a background thread accepting network connections that add events to the queue.
  rpcHandler = VOEventHandler(logger=DEFAULTLOGGER)
  pyro_thread = threading.Thread(target=rpcHandler.servePyroRequests, name='PyroDaemon')
  pyro_thread.daemon = True
  pyro_thread.start()

  # Start a background thread to process incoming events from the queue, one by one.
  queue_thread = threading.Thread(target=QueueWorker, name='QueueDaemon', kwargs={'logger':DEFAULTLOGGER})
  queue_thread.daemon = True
  queue_thread.start()

  try:
    while True:
      time.sleep(3600)
  finally:
    EXITING = True
    PYRO_DAEMON.shutdown()
    time.sleep(1)
