import csv

from LEOCraft.user_terminals.terminal import TerminalCoordinates, UserTerminal


class Aircraft(UserTerminal):

    def __init__(self, replaced_gs_csv: str, flight_cluster_csv: str) -> None:
        super().__init__()

        self._replaced_gs = replaced_gs_csv
        self._flight_cluster = flight_cluster_csv

        self.flights: dict[str, list[TerminalCoordinates]] = dict()

    def build(self) -> None:
        "Creates Terminal Coordinates object for each flight replaced GSes and flights"
        self._build_replaced_gs()
        self._build_flight_cluster()

    def _build_replaced_gs(self) -> None:
        # Reading the CSV file
        with open(self._replaced_gs) as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Creating TerminalCoordinates objects for each GS
            for row in csv_reader:

                cartesian = self.geodetic_to_cartesian(
                    float(row["latitude_degree"]),
                    float(row["longitude_degree"]),
                    float(row["elevation_m"])
                )

                self.terminals.append(
                    TerminalCoordinates(
                        name=row['name'],
                        latitude_degree=str(row['latitude_degree']),
                        longitude_degree=str(row['longitude_degree']),
                        elevation_m=float(row['elevation_m']),
                        cartesian_x=cartesian[0],
                        cartesian_y=cartesian[1],
                        cartesian_z=cartesian[2]
                    )
                )

    def _build_flight_cluster(self) -> None:
        # Reading the CSV file
        with open(self._flight_cluster) as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Creating TerminalCoordinates objects for each GS
            for row in csv_reader:

                cartesian = self.geodetic_to_cartesian(
                    float(row["latitude_degree"]),
                    float(row["longitude_degree"]),
                    float(row["elevation_m"])
                )

                if row['name'] not in self.flights.keys():
                    self.flights[row['name']] = list()

                self.flights[row['name']].append(
                    TerminalCoordinates(
                        name=row['name'],
                        latitude_degree=str(row['latitude_degree']),
                        longitude_degree=str(row['longitude_degree']),
                        elevation_m=float(row['elevation_m']),
                        cartesian_x=cartesian[0],
                        cartesian_y=cartesian[1],
                        cartesian_z=cartesian[2]
                    )
                )

    def encode_name(self, id: int) -> str:
        '''Encode ground station name

        Parameters
        -------
        gid: int
            Terminal ID

        Returns
        -------
        str
            Encode terminal name
        '''
        return f'F-{id}'

    def decode_name(self, name: str) -> int:
        """Decode ground station name

        Parameters
        -------
        name: str
            Encoded name

        Returns
        -------
        int
            id
        """
        return int(name.split('-')[1])
