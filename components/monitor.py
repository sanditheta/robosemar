from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Tuple, Callable, Union, Optional

# Observer and Subject Interfaces

logger = logging.getLogger(__name__)


class Observer(ABC):
    @abstractmethod
    def update(self, status: Union[str, bool], timestamp: int) -> None:
        pass


def register_observers(instance: 'Subject', observers: Union[Observer, List[Observer]]) -> None:
    if not isinstance(observers, list):
        observers = [observers]
    for observer in observers:
        if observer not in instance._observers:
            instance._observers.append(observer)

def remove_observers(instance: 'Subject', observers: Union[Observer, List[Observer]]) -> None:
    if not isinstance(observers, list):
        observers = [observers]
    for observer in observers:
        if observer in instance._observers:
            instance._observers.remove(observer)

def notify_observers(instance: 'Subject', status: Union[str, bool], timestamp: int) -> None:
    for observer in instance._observers:
        observer.update(status, timestamp)

class VoiceLogger(Observer):
    def update(self, status: Union[str, bool], timestamp: int) -> None:
        logger.info(f"Voice detected with status: {status} at timestamp: {timestamp}")
