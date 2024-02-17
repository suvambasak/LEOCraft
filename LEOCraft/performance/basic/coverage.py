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
        self.GS_coverage_metric: float

    def build(self) -> None:
        self.v.nl()
        self.v.log('Building coverage...')

    def compute(self) -> None:
        self.v.log('Computing coverage...')
        self.dead_GS_count = self._count_user_terminals_out_of_coverage(
            self.leo_con.gsls
        )
        self.v.log(f'Out of coverage GS:\t{self.dead_GS_count}')

        self.GS_coverage_metric = self._visible_sats_log_sum(self.leo_con.gsls)
        self.v.log(f'GS coverage metric:\t{self.GS_coverage_metric}')

    def _count_user_terminals_out_of_coverage(self, sls: list[set[str, float]]) -> int:
        '''Counts terminal without satellite links

        Parameters:
        ---------
        sls: list[set[str, float]]
            List of the sets of sls (satellite links)

        Returns:
        --------
        int
            Count of no links
        '''

        dead_count = 0
        for sats_in_range in sls:
            if 0 == len(sats_in_range):
                dead_count += 1
        return dead_count

    def _visible_sats_log_sum(self, sls: list[set[str, float]]) -> float:
        '''Calculates coverage metric

        Parameters:
        ---------
        sls: list[set[str, float]]
            List of the sets of sls (satellite links)

        Returns:
        --------
        int
            Count of no links
        '''

        log_sum = 0.0
        for sats_in_range in sls:
            log_sum += math.log10(
                len(sats_in_range)
            ) if sats_in_range else 0

        return log_sum
