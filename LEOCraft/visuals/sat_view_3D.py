import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.visuals.view import Render


class SatView3D(Render):
    'Rendering in a globe using plotly packages'

    _TEXT = 'text'
    _LAT = 'lat'
    _LONG = 'long'
    _COLOR_CODE = 'color_code'
    _SIZE = 'size'

    def __init__(
        self,
        leo_con: LEOConstellation,
        lat: float = 0.0, long: float = 0.0, title: str | None = None
    ) -> None:
        '''
        Creates SatView 3D renderer

        Parameters
        ----------
        leo_con: LEOConstellation
            Object of LEO constellation 

        lat: float, optional
            View center latitude (default 0.0 degree)
        long: float, optional
            View center longitude (default 0.0 degree)

        title: str, optional
            Title (default classname)
        '''

        super().__init__(leo_con)

        self.fig = go.Figure()

        # Satellite to be tracked or need attention
        self._special_sats: set[str] = set()

        self.fig.update_layout(
            margin={"b": 0, "t": 35, "l": 0},
            title=title if title else self.leo_con.name,
            geo=dict(projection_type="orthographic")
        )

        # Set the view location here
        self.fig.update_geos(
            projection_rotation=dict(
                lon=long,
                lat=lat,
                roll=0
            ),
        )

    def highlight_satellites(self, sat_names: list[str]) -> None:
        '''
        Marks satellites with large markers

        Paramters
        --------
        sat_names: list[str]
            List of sat names
        '''
        self._special_sats.update(sat_names)

    def build(self) -> None:
        'Generate the view'

        self.v.log('Building view 3D...  ')

        if len(self._gsl):
            self.v.rlog('Adding GSLs...      ')
            self.fig.add_traces(self._build_GSLs())

        if len(self._isl):
            self.v.rlog('Adding ISLs...  ')
            self.fig.add_traces(self._build_ISLs())

        if len(self._sat):
            self.v.rlog('Adding satellites...   ')
            self.fig.add_trace(self._build_satellites())

        if len(self._gs):
            self.v.rlog('Adding ground stations...  ')
            self.fig.add_trace(self._build_ground_stations())

        # if len(self._cov):
        #     self._build_coverages()

        self.v.clr()

    # def _build_coverages(self) -> None:
    #     for sat_name in self._cov:
    #         sat_info = self.leo_con.sat_info(sat_name)
    #         radius = self.leo_con.shells[sat_info.shell_id].satellites[sat_info.id].coverage_cone_radius_m(
    #         )

    def _build_ground_stations(self) -> None:
        dict_list = list()

        for gs_name in self._gs:
            gid, terminal = self.leo_con.gs_info(gs_name)

            dict_list.append({
                self._TEXT: f"G-{gid} {terminal.name}",
                self._LAT: float(terminal.latitude_degree),
                self._LONG: float(terminal.longitude_degree),
            })

        df = pd.DataFrame.from_dict(dict_list)
        return go.Scattergeo(
            name="Ground station",
            lon=df[self._LONG],
            lat=df[self._LAT],
            text=df[self._TEXT],
            mode="markers",
            marker=dict(size=9, color=self._GROUND_STATION_COLOR)
        )

    def _build_GSLs(self) -> None:
        GSLs_trace_list = list()

        for gs_name in self._gsl:
            gid = self.leo_con.ground_stations.decode_name(gs_name)
            terminal = self.leo_con.ground_stations.terminals[gid]

            for sat_name, distance_m in self.leo_con.gsls[gid]:
                sat_info = self.leo_con.sat_info(sat_name)

                GSLs_trace_list.append(go.Scattergeo(
                    name=f"G-{gid} to {sat_name}",
                    lon=[
                        float(terminal.longitude_degree),
                        sat_info.nadir_longitude
                    ],
                    lat=[
                        float(terminal.latitude_degree),
                        sat_info.nadir_latitude
                    ],
                    text=f'''GSLs: {terminal.name} {
                        round(distance_m/1000, 2)}km''',
                    mode="lines",
                    line=dict(
                        color=self._GSL_COLOR,
                        width=self.get_thickness(gs_name, sat_name)
                    )
                ))

        return GSLs_trace_list

    def _build_satellites(self) -> None:
        dict_list = list()

        for sat_name in self._sat:
            sat_info = self.leo_con.sat_info(sat_name)

            dict_list.append({
                self._LAT: sat_info.nadir_latitude,
                self._LONG: sat_info.nadir_longitude,

                self._COLOR_CODE: self._SHELL_COLORS[
                    sat_info.shell_id % len(self._SHELL_COLORS)
                ],
                self._TEXT: f'''ID: {sat_name} O: {sat_info.orbit_num} N: {sat_info.sat_num}''',
                self._SIZE: 18 if sat_name in self._special_sats else 9
            })

        df = pd.DataFrame.from_dict(dict_list)
        return go.Scattergeo(
            name="Satellite",
            lat=df[self._LAT],
            lon=df[self._LONG],
            text=df[self._TEXT],
            mode="markers",
            marker=dict(size=df[self._SIZE], color=df[self._COLOR_CODE])
        )

    def _build_ISLs(self) -> None:
        ISLs_trace_list = list()

        for sat_name_a, sat_name_b in self._isl:
            sat_info_a = self.leo_con.sat_info(sat_name_a)
            sat_info_b = self.leo_con.sat_info(sat_name_b)

            ISLs_trace_list.append(go.Scattergeo(
                name=f"{sat_name_a} to {sat_name_b}",

                lon=[sat_info_a.nadir_longitude, sat_info_b.nadir_longitude],
                lat=[sat_info_a.nadir_latitude, sat_info_b.nadir_latitude],

                text=f'''ISL: {sat_name_a}-{sat_name_b} {round(
                    self.leo_con.link_length(sat_name_a, sat_name_b)/1000, 2
                )}km''',

                mode="lines",
                line=dict(
                    width=self.get_thickness(sat_name_a, sat_name_b),
                    color=self.get_color(sat_name_a, sat_name_b)
                )
            ))

        return ISLs_trace_list

    def show(self) -> None:
        self.v.log('Rendering...  ')
        self.fig.show()

    def export_html(self, filename: str | None = None) -> str:

        if not filename:
            filename = f'{self.leo_con.name}.html'

        self.v.log('Exporting HTML...  ')
        self.fig.write_html(filename)
        return filename

    def export_png(self, filename: str | None = None) -> str:

        if not filename:
            filename = f'{self.leo_con.name}.png'

        self.v.log('Exporting PNG...  ')
        pio.write_image(
            fig=self.fig,
            file=filename,

            width=1920,
            height=1080
        )
        return filename
