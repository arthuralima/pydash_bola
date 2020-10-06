
'''
Abstract Class for Simple Module Implementation.

Class implements basic functionality to be called by the main program.
'''

from abc import ABCMeta, abstractmethod
from base.scheduler import Scheduler
from base.scheduler_event import Scheduler_Event
from base.message import Message, Message_Kind

class Simple_Module(metaclass=ABCMeta):

    def __init__(self, id):
        self.scheduler = Scheduler()
        self.id = id

    def send_up(self, msg):
        self.scheduler.add_event(Scheduler_Event(msg, self.id, self.id-1))

        #if self.id == 0:
        #    print(f'Object {self} with id {self.id} is in the top of the control stack!')
        #    exit(0)


    def send_down(self, msg):
        self.scheduler.add_event(Scheduler_Event(msg, self.id, self.id+1))

    @abstractmethod
    def initialize(self):
        print(f'> Initializing module {self.__class__.__name__}')
        pass

    @abstractmethod
    def finalization(self):
        print(f'> Finalization module {self.__class__.__name__}')
        pass

    @abstractmethod
    def handle_xml_request(self, msg):
        pass

    @abstractmethod
    def handle_xml_response(self, msg):
        pass

    @abstractmethod
    def handle_segment_size_request(self, msg):
        pass

    @abstractmethod
    def handle_segment_size_response(self, msg):
        pass

    def handle_message(self, msg):
        if msg.get_kind() == Message_Kind.XML_REQUEST:
            self.handle_xml_request(msg)
        elif msg.get_kind() == Message_Kind.XML_RESPONSE:
            self.handle_xml_response(msg)
        elif msg.get_kind() == Message_Kind.SEGMENT_REQUEST:
            self.handle_segment_size_request(msg)
        elif msg.get_kind() == Message_Kind.SEGMENT_RESPONSE:
            self.handle_segment_size_response(msg)
        else:
            raise ValueError(f'Invalid Message Kind - {msg}')

        pass