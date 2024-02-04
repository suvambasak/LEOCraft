from abc import ABC, abstractmethod


class LossModel(ABC):
    "Abstract class for the attenuation in ground to satellite links"

    @abstractmethod
    def data_rate_bps(self, antenna_separation_m: float, partition: int = 1) -> int:
        """Calculate the data rate in bits/s for a ground to satellite link

        Parameters
        ----------
        antenna_separation_m : float
            Distance between ground station antenna and satellite antenna
        partition : int, optional
            Number of ground station being served by a satellite

        Returns
        -------
        int
            Data rate (b/s) 
        """
        pass
