import os
from abc import ABC, abstractmethod

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.utilities import ProcessingLog


class Performance(ABC):
    '''
    Abstract class for performance measurement of constellation

    Follows two stage implementation
    - Build: prepare the setup
    - Compute: Calculate/Analyze/Measure
    '''

    def __init__(self,  leo_con: Constellation) -> None:
        self.leo_con = leo_con

        self.v = ProcessingLog()

    @abstractmethod
    def build(self) -> None:
        pass

    @abstractmethod
    def compute(self) -> None:
        pass

    def _create_export_dir(self, prefix_path: str = '.') -> str:
        'Create directory for performance'
        dir = f'{prefix_path}/Performance'
        if not os.path.isdir(dir):
            os.makedirs(dir, exist_ok=True)
        return dir
