import unittest

from LEOCraft.attenuation.fspl import FSPL


class TestLossModel(unittest.TestCase):
    def setUp(self) -> None:
        # Starlink gen 2 model
        # self.loss_model = LossModel(
        #     28.3*1000000000, 58.64, 1.6*1000000000, 13.6
        # )
        # self.loss_model.set_Tx_antenna_gain(gain_dB=34.5)

        # Starlink gen 1 FCC: https://doi.org/10.1016/j.actaastro.2019.03.040
        self.loss_model = FSPL()
        self.loss_model.set_Tx_antenna_gain(antenna_diameter_m=3.5)

    def test_data_rate_bps_by_GT(self) -> None:
        # Altitude change
        data_rate_500 = self.loss_model.data_rate_bps(500*1000)
        data_rate_505 = self.loss_model.data_rate_bps(505*1000)
        data_rate_510 = self.loss_model.data_rate_bps(510*1000)
        data_rate_515 = self.loss_model.data_rate_bps(515*1000)

        self.assertTrue(data_rate_500 > data_rate_505)
        self.assertTrue(data_rate_505 > data_rate_510)
        self.assertTrue(data_rate_510 > data_rate_515)

        # Serving multiple ground station

        # Serving two GS
        data_rate_500_1 = self.loss_model.data_rate_bps(503*1000, 2)
        data_rate_500_2 = self.loss_model.data_rate_bps(504*1000, 2)

        self.assertTrue(data_rate_500_1 > data_rate_500_2)
        self.assertTrue(data_rate_500 > (data_rate_500_1+data_rate_500_2))

    def test_legacy(self) -> None:
        lm = FSPL(
            28.5*1000000000, 98.4, 0.5*1000000000, 13.6)
        lm.set_Tx_antenna_gain(antenna_diameter_m=3.5)

        self.assertEqual(
            58.16034295050158,
            lm.Tx_gain_dB
        )

        lm.set_Rx_antenna_gain(antenna_diameter_m=3.5)
        self.assertTrue(
            abs(lm.Rx_gain_dB-58.22335952) < 0.3
        )

        lm.set_Rx_antenna_gain(gain_dB=40.9)
        self.assertTrue(40.9, lm.Rx_gain_dB)

        self.assertEqual(
            21.114419774397817,
            lm.power_received(550000)
        )

        self.assertEqual(
            17512389598,
            lm._data_rate_bps(535.9, 550000)
        )
