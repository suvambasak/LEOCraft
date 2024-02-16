from LEOCraft.constellations.constellation import Constellation
from LEOCraft.performance.basic.coverage import Coverage


class Coverage(Coverage):
    def __init__(self, leo_con: Constellation) -> None:
        super().__init__(leo_con)

        self.dead_flight_count: int
        self.flight_coverage_metric: float

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

        self.dead_flight_count = self._count_user_terminals_out_of_coverage(
            self.leo_con.fsls
        )
        self.v.log(f'Out of coverage flights:\t{self.dead_flight_count}')

        self.flight_coverage_metric = self._visible_sats_log_sum(
            self.leo_con.fsls
        )
        self.v.log(f'Flight coverage metric:\t{self.flight_coverage_metric}')
