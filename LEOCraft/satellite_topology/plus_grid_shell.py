from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology


class PlusGridShell(LEOSatelliteTopology):
    """
    Implements +Grid topology in a shell.
    Extendes LEOSatelliteTopology class

    - Generates TLE of all the satellite in a shell
    - Export TLEs into a file
    - Generates ISL links (sat_1, sat_2)
    - Export ISLs into a CSV file


    Reference:
    [1] https://github.com/snkas/hypatia/tree/master/satgenpy
    [2] Kassing S, Bhattacherjee D, Águas AB, Saethre JE, Singla A. Exploring the" Internet from space" with Hypatia. InProceedings of the ACM Internet Measurement conference 2020 Oct 27 (pp. 214-229).
    """

    def build_ISLs(self) -> None:
        "Generates ISL links (sat_1, sat_2)"

        for i in range(self.orbits):
            for j in range(self.sat_per_orbit):
                sat = i * self.sat_per_orbit + j

                # Link to the next in the orbit
                sat_same_orbit = i * self.sat_per_orbit + \
                    ((j + 1) % self.sat_per_orbit)
                sat_adjacent_orbit = (
                    (i + 1) % self.orbits
                ) * self.sat_per_orbit + (j % self.sat_per_orbit)

                # Same orbit
                self.isls.add(
                    (min(sat, sat_same_orbit), max(sat, sat_same_orbit))
                )
                # Adjacent orbit
                self.isls.add(
                    (min(sat, sat_adjacent_orbit), max(sat, sat_adjacent_orbit))
                )
