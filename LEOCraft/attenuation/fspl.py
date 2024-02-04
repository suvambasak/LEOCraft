from math import log2, log10, pi

from LEOCraft.attenuation.loss_model import LossModel


class FSPL(LossModel):
    """
    Extends LossModel
    Implements the loss model using free-space path loss (FSPL) and shannon channel capacity for attenuation in ground to satellite links
    """

    SPEED_OF_LIGHT_C = 3e+8  # m/s
    ANTENNA_EFFICIENCY = 60  # %
    BOLTZMANNS_CONSTANT = 1.38e-23  # J/K

    def __init__(
        self,
        frequency_Hz: float = 28.5*1000000000,  # Frequency in Hz
        Tx_power_dBm: float = 98.4,             # Tx power dBm
        bandwidth_Hz: float = 0.5*1000000000,   # Bandwidth Hz
        GT_ratio: float = 13.6                  # G/T ratio
    ) -> None:
        """Create free-space path loss (FSPL) model.
        Default parameters are from Starlink (gen1) FCC [1]


        Parameters
        ----------
        frequency_Hz : float
            Channel frequency in Hz
        Tx_power_dBm : float
            Transmit Power (dBm)(EIRP)
        bandwidth_Hz: float
            Bandwidth in Hz
        satellite_catalog_number: int
            Unique ID for satellite
        GT_ratio: float
            Ratio of the antenna gain (G) to the system noise temperature (T)

        Reference:
        [1] https://doi.org/10.1016/j.actaastro.2019.03.040
        """

        self.frequency_Hz = frequency_Hz
        self.Tx_power_dBm = Tx_power_dBm

        self.bandwidth_Hz = bandwidth_Hz
        self.GT_ratio = GT_ratio

        self.lambda_m = self.SPEED_OF_LIGHT_C/self.frequency_Hz

    def _antenna_gain_dB(self, antenna_diameter_m) -> float:
        "Calculate antenna gain"

        gain = (self.ANTENNA_EFFICIENCY/100) * \
            pow(pi * antenna_diameter_m / self.lambda_m, 2)

        return 10 * log10(gain)

    def set_Tx_antenna_gain(self, gain_dB=None, antenna_diameter_m=None) -> None:
        '''
        Set transmitter antenna gain with either directly (dB) or calculate from the antenna diameter (m)

        Parameters
        ----------
        gain_dB : float, optional
            Tx antenna gain in dB, (34.5 dB[1])
        antenna_diameter_m : float, optional
            Tx antenna diameter in meters (EIRP) (3.5 m [1])

        Reference:
        [1] https://doi.org/10.1016/j.actaastro.2019.03.040
        '''

        if gain_dB:
            self.Tx_gain_dB = gain_dB
        else:
            self.Tx_gain_dB = self._antenna_gain_dB(antenna_diameter_m)

    def set_Rx_antenna_gain(self, gain_dB=None, antenna_diameter_m=None) -> None:
        '''
        Set receiver antenna gain with either directly (dB) or calculate from the antenna diameter (m)

        Parameters
        ----------
        gain_dB : float, optional
            Rx antenna gain in dB, (40.9 dB [1])
        antenna_diameter_m : float, optional
            Rx antenna diameter in meters (EIRP) (3.5 m [1])

        Reference:
        [1] https://doi.org/10.1016/j.actaastro.2019.03.040
        '''

        if gain_dB:
            self.Rx_gain_dB = gain_dB
        else:
            self.Rx_gain_dB = self._antenna_gain_dB(antenna_diameter_m)

    def power_received(self, antenna_separation_m: float) -> float:
        """Calculates the power received (dBm) at a given distance between Tx and Rx antenna in meters

        Parameters
        ----------
        antenna_separation_m : float
            Distance between Tx and Rx antenna in meters
        """

        Rx_power_dBm = self.Tx_power_dBm + self.Tx_gain_dB + self.Rx_gain_dB - \
            20 * log10(4*pi*antenna_separation_m/self.lambda_m)

        return Rx_power_dBm

    def _data_rate_bps(self, temperature_k: float, antenna_separation_m: float) -> int:
        """Legacy method to calculate data rate in b/s

        Parameters
        ----------
        temperature_k : float
            System temperature in kelvin
        antenna_separation_m : float
            Distance between Tx and Rx antenna in meters


        Returns
        -------
        int
            Data rate (b/s) 
        """

        # Rx power from dBm to watt
        Rx_power_w = pow(
            10, (self.power_received(antenna_separation_m)-30)/10
        )

        SNR = Rx_power_w/(self.BOLTZMANNS_CONSTANT *
                          temperature_k*self.bandwidth_Hz)
        channel_capacity = self.bandwidth_Hz*log2(1+SNR)

        return int(channel_capacity)

    def data_rate_bps(self, antenna_separation_m: float, partition: int = 1) -> int:
        """Calculates the data rate in bps using G/T ratio of the system

        Parameters
        ----------
        antenna_separation_m : float
            Distance between Tx and Rx antenna in meters
        partition : float, optional
            Number of ground station under the shadow of satellite


        Returns
        -------
        int
            Data rate (b/s) 
        """

        bandwidth_Hz = self.bandwidth_Hz/partition
        # print ('BW_Hz',bandwidth_Hz)

        # Singal power in dBm without Rx gain
        signal_dBm = self.Tx_power_dBm + self.Tx_gain_dB - 20 * \
            log10(4*pi*antenna_separation_m/self.lambda_m)

        # print('signal_dBm', signal_dBm)

        # Singal power in watt
        signal_w = pow(
            10, (signal_dBm-30)/10
        )/partition
        # print('signal_w', signal_w)

        SNR = (signal_w*self.GT_ratio) / \
            (self.BOLTZMANNS_CONSTANT*bandwidth_Hz)

        # print('SNR', SNR)

        channel_capacity = bandwidth_Hz*log2(1+SNR)
        # print ('channel_capacity',channel_capacity)

        return int(channel_capacity)
