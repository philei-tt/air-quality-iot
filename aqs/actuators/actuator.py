from abc import abstractmethod
from typing import List

from aqs.actuators.action import Action


class Actuator:
    def __init__(self, name):
        self._name = name
        
    def get_name(self):
        return self._name
    
    @abstractmethod
    def get_supported_actions(self) -> List[Action]:
        raise NotImplementedError()
    
    @abstractmethod
    def act(self, action: Action, value=None):
        raise NotImplementedError()
    
    @abstractmethod
    def get_state(self):
        raise NotImplementedError()
    
    @abstractmethod
    def is_alive(self):
        return True
    
    @abstractmethod
    def close(self):
        raise NotImplementedError()
