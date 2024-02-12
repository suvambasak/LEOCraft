import json

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.performance.route_classifier.basic_classifier import \
    BasicClassifier
from LEOCraft.performance.throughput_LP import ThroughputLP


class Throughput(ThroughputLP):
    'Implements ThroughputLP for computing LEO constellation throughput GS to GS'

    def __init__(self, leo_con: LEOConstellation, tm_path: str) -> None:
        super().__init__(leo_con, tm_path)

        self._rcategories = BasicClassifier(self.leo_con)

    def _process_traffic_metrics(self) -> None:
        '''Create demand_metrics merging two up and down flows from the JSON file

        i.e. Creates one flow of (G-X_G-Y + G-Y_G-X)
        '''

        with open(self._traffic_metrics_file) as json_file:
            content = json.loads(json_file.read())

        self.demand_metrics = dict()

        for s in range(len(self.leo_con.ground_stations.terminals)):
            for d in range(s+1, len(self.leo_con.ground_stations.terminals)):
                s_gs_name = self.leo_con.ground_stations.encode_name(s)
                d_gs_name = self.leo_con.ground_stations.encode_name(d)
                outgoing_key = f"{s_gs_name}_{d_gs_name}"
                incoming_key = f"{d_gs_name}_{s_gs_name}"

                self.demand_metrics[outgoing_key] = content[incoming_key] + \
                    content[outgoing_key]
