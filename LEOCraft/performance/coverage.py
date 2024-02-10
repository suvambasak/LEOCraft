import math

from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.performance import Performance


class Coverage(Performance):
    '''
    Implements Performance for measuring coverage metrices of a constellation

    Computes:
    - Number of ground station out of coverage
    - Coverage metrices
    '''

    def __init__(self, leo_con: Constellation) -> None:
        super().__init__(leo_con)

        self.dead_GS_count: int
        self.coverage_metric: float

    def build(self) -> None:
        self.v.nl()
        self.v.log('Building coverage...')

    def compute(self) -> None:
        self.v.log('Computing coverage...')
        self._count_user_terminals_out_of_coverage()
        self._visible_sats_log_sum()

    def _count_user_terminals_out_of_coverage(self) -> None:
        "Counts terminal without satellite links"

        dead_count = 0
        for sats_in_range in self.leo_con.gsls:
            if 0 == len(sats_in_range):
                dead_count += 1
        self.dead_GS_count = round(dead_count, 3)
        self.v.log(f'Out of coverage GS:\t{self.dead_GS_count}')

    def _visible_sats_log_sum(self) -> None:
        "Calculates coverage metric"

        log_sum = 0.0
        for sats_in_range in self.leo_con.gsls:
            log_sum += math.log10(
                len(sats_in_range)
            ) if sats_in_range else 0
        self.coverage_metric = round(log_sum, 3)
        self.v.log(f'Coverage metric:\t{self.coverage_metric}')
