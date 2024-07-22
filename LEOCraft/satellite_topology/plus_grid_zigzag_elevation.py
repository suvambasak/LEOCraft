from LEOCraft.satellite_topology.plus_grid_shell import PlusGridShell
from LEOCraft.satellite_topology.satellite import LEOSatellite


class PlusGridZigzagElevation(PlusGridShell):
    """
    Extendes PlusGridShell class and implements +Grid topology in a shell
    where consecutive orbits are kept in elevation difference of 5 to 10 km
    forming Zig Zag east to west (inter-orbit).

    - Generates TLE of all the satellite in a shell
    - Export TLEs into a file
    - Generates ISL links (sat_1, sat_2)
    - Export ISLs into a CSV file
    """

    def __init__(
        self,
        id: int,
        orbits: int,
        sat_per_orbit: int,

        altitude_pattern_m: list[float],
        inclination_degree: float,
        angle_of_elevation_degree: float,
        phase_offset: float,
    ) -> None:
        """Create a new shell for a LEO constellation

        Parameters
        ----------
        id: int
            Unique shell number
        orbits: int
            Number of orbits
        sat_per_orbit: int
            Number of satellites per orbit
        altitude_pattern_m : list[float]
            List of consecutive orbit's altitude pattern in meter(s)
        inclination_degree : float
            Angle of inclination in degree
        angle_of_elevation_degree:
            Min angle of elevation in degree

        phase_offset: float: float
            Offset between satellite of adjacent orbit
        """

        assert len(altitude_pattern_m) > 1

        super().__init__(
            id=id,
            orbits=orbits,
            sat_per_orbit=sat_per_orbit,

            altitude_m=altitude_pattern_m[0],
            inclination_degree=inclination_degree,
            angle_of_elevation_degree=angle_of_elevation_degree,
            phase_offset=phase_offset
        )

        self.altitude_pattern_m = altitude_pattern_m

    def build_satellites(self) -> None:
        "Build TLEs and set epoch time satellites of this shell"

        satellite_counter = 0

        altitude_index = 0
        for orbit in range(0, self.orbits):

            # Orbit across longitude
            raan_degree = orbit * 360.0 / self.orbits
            orbit_wise_shift = 0
            if orbit % 2 == 1:
                # Phase_offset between two adjacent orbits
                orbit_wise_shift = 360.0 / self.sat_per_orbit * self.phase_offset

            # For each satellite in the orbit
            for n_sat in range(0, self.sat_per_orbit):

                # Position of the satellite in orbit
                mean_anomaly_degree = orbit_wise_shift + \
                    (n_sat * 360 / self.sat_per_orbit)

                # Creating satellites
                _leosat = LEOSatellite(
                    altitude_m=self.altitude_pattern_m[
                        orbit % len(self.altitude_pattern_m)
                    ],
                    inclination_degree=self.inclination_degree,
                    angle_of_elevation_degree=self.angle_of_elevation_degree,
                    satellite_catalog_number=satellite_counter+1,
                    raan_degree=raan_degree,
                    mean_anomaly_degree=mean_anomaly_degree,
                    satellite_name=self.name
                )
                _leosat.build()

                # Fetch and check the epoch from the TLES data
                # In the TLE, the epoch is given with a Julian data of yyddd.fraction
                # ddd is actually one-based, meaning e.g. 18001 is 1st of January, or 2018-01-01 00:00.
                # As such, to convert it to Astropy Time, we add (ddd - 1) days to it
                # See also: https://www.celestrak.com/columns/v04n03/#FAQ04

                # Consistent epoch check
                if self.universal_epoch is None:
                    self.universal_epoch = _leosat.epoch
                if _leosat.epoch != self.universal_epoch:
                    raise ValueError("The epoch of all TLES must be the same")
                self.satellites.append(_leosat)

                satellite_counter += 1

    @property
    def filename(self) -> str:
        """Generates file name from orbital parameters

        Returns
        -------
        str
            File name 
        """

        return f"{self.__class__.__name__}_{self.id}_o{self.orbits}n{self.sat_per_orbit}h{'-'.join([str(h) for h in self.altitude_pattern_m])}i{self.inclination_degree}e{self.angle_of_elevation_degree}p{self.phase_offset}"
