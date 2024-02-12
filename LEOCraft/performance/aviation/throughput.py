import json

from LEOCraft.constellations.LEO_aviation_constellation import \
    LEOAviationConstellation
from LEOCraft.performance.route_classifier.aviation_classifier import \
    AviationClassifier
from LEOCraft.performance.throughput_LP import ThroughputLP


class Throughput(ThroughputLP):
    'Implements ThroughputLP for computing LEO constellation throughput GS to Flight terminals'

    def __init__(self, leo_con: LEOAviationConstellation, tm_path: str) -> None:
        super().__init__(leo_con, tm_path)

        self._rcategories = AviationClassifier(self.leo_con)

    def _process_traffic_metrics(self) -> None:
        'Create demand_metrics from traffic metrics file'
        with open(self._traffic_metrics_file) as json_file:
            self.demand_metrics = json.loads(json_file.read())

    def build(self) -> None:
        super().build()

        # Adding FSLs
        self.v.rlog('Connecting all flight terminals...')
        for tid, _ in enumerate(self.leo_con.aircrafts.terminals):
            self.leo_con.connect_flight_cluster_terminals(
                self.leo_con.aircrafts.encode_name(tid)
            )
        self.v.clr()
