import pandas as pd
import plotly.graph_objects as go

from LEOCraft.visuals.sat_raw_view_3D import SatRawView3D


class SatView3D(SatRawView3D):
    '''Rendering constellation view on Geographical Scatter Plot

    Build with package:
    - Plotly (Scattergeo)
    '''

    _LAT = 'lat'
    _LONG = 'long'

    def setup_layout(
            self,
            title: str | None,
            globe_visibility: bool,
            lat: float,
            long: float,
            elevation_m: float
    ) -> None:

        # Not used in Scattergeo
        del globe_visibility
        del elevation_m

        self.fig.update_layout(
            margin={"b": 0, "t": 35, "l": 0},
            title=title if title else self.leo_con.name,
        )

        # Set the view location here
        self.fig.update_geos(
            projection_type="orthographic",
            projection_rotation=dict(
                lon=long,
                lat=lat,
                roll=0
            )
        )

    def _build_coverages(self) -> None:
        self.v.rlog('Adding coverage cones...  (not supported)')

    def _build_ground_stations(self) -> go.Scattergeo:
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
            marker=dict(
                size=self._DEFAULT_GS_SIZE,
                color=self._GROUND_STATION_COLOR
            )
        )

    def _build_GSLs(self) -> list[go.Scattergeo]:
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
                        sat_info.nadir_longitude_deg
                    ],
                    lat=[
                        float(terminal.latitude_degree),
                        sat_info.nadir_latitude_deg
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

    def _build_satellites(self) -> go.Scattergeo:
        dict_list = list()
        color_map = dict()

        for sat_name in self._sat:
            sat_info = self.leo_con.sat_info(sat_name)
            # print(sat_info)

            if sat_info.altitude_km not in color_map:
                color_map[sat_info.altitude_km] = self._shell_colors.pop()

            dict_list.append({
                self._LAT: sat_info.nadir_latitude_deg,
                self._LONG: sat_info.nadir_longitude_deg,

                # self._COLOR_CODE: self._shell_colors[
                #     sat_info.shell_id % len(self._shell_colors)
                # ],
                self._COLOR_CODE: color_map[sat_info.altitude_km],

                self._TEXT: f'''ID: {sat_name} O: {sat_info.orbit_num} N: {sat_info.sat_num}''',
                self._SIZE: self._SPECIAL_SAT_SIZE if sat_name in self._special_sats else self._DEFAULT_SAT_SIZE
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

    def _build_ISLs(self) -> list[go.Scattergeo]:
        ISLs_trace_list = list()

        for sat_name_a, sat_name_b in self._isl:
            sat_info_a = self.leo_con.sat_info(sat_name_a)
            sat_info_b = self.leo_con.sat_info(sat_name_b)

            ISLs_trace_list.append(go.Scattergeo(
                name=f"{sat_name_a} to {sat_name_b}",

                lon=[sat_info_a.nadir_longitude_deg,
                     sat_info_b.nadir_longitude_deg],
                lat=[sat_info_a.nadir_latitude_deg,
                     sat_info_b.nadir_latitude_deg],

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
