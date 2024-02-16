import os
import shutil
import unittest

from LEOCraft.visuals.sat_view_2D import SatView2D
from LEOCraft.visuals.sat_view_3D import SatView3D
from tests.test_LEO_constellation import (_create_multi_shell,
                                          _create_single_shell)


class TestView(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.test_directory = f'{os.getcwd()}/ViewLEOConstellation'
        os.makedirs(self.test_directory, exist_ok=True)

        self.shell_1 = _create_single_shell()
        self.shell_3 = _create_multi_shell()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.test_directory)

    def _build_view(self, view: SatView2D | SatView3D) -> SatView3D | SatView2D:
        view.add_ground_stations('G-0', 'G-1', 'G-2', 'G-3')
        view.add_satellites('S0-0', 'S0-1', 'S0-2', 'S0-3', 'S0-26')
        view.add_coverages('S0-0', 'S0-1', 'S0-40', 'S0-31', 'S0-30')
        view.add_GSLs('G-1', 'G-2')
        view.add_ISLs((('S0-0', 'S0-1'), ('S0-1', 'S0-2')))
        view.add_routes('G-2_G-3', 'G-0_G-1', 'G-2_G-6', k=0)
        view.add_routes('G-0_G-5', k=5)

        view.add_all_ground_stations()
        view.add_all_satellites()
        view.add_all_coverages()
        view.add_all_GSLs()
        view.add_all_ISLs()
        view.add_all_routes()

        view.build()

        return view

    def test_2D(self):
        for leo_con in [self.shell_1, self.shell_3]:
            view = self._build_view(SatView2D(leo_con))

            path = view.export_html(f'{self.test_directory}/3DTest.html')
            self.assertTrue(os.path.exists(path))

    def test_3D(self):
        for leo_con in [self.shell_1, self.shell_3]:
            view = self._build_view(SatView3D(leo_con))

            path = view.export_html(f'{self.test_directory}/3DTest.html')
            self.assertTrue(os.path.exists(path))
            path = view.export_png(f'{self.test_directory}/3DTest.png')
            self.assertTrue(os.path.exists(path))
