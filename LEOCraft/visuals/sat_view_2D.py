import webbrowser

import folium

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.visuals.view import Render


class SatView2D(Render):
    'Rendering the 2D HTML using folium packages'

    _COVERAGE_OPACITY = 0.15
    _COVERAGE_FILL_OPACITY = 0.05

    def __init__(
        self,
        leo_con: LEOConstellation,
        default_zoom: int = 2, lat: float = 0.0, long: float = 0.0,
    ) -> None:
        super().__init__(leo_con)

        self.map = folium.Map(
            location=[lat, long],
            zoom_start=default_zoom
        )

    def build(self) -> None:
        self.v.log('Building view 2D...  ')

        if len(self._cov):
            self.v.rlog('Adding coverages...  ')
            self._build_coverages()

        if len(self._gsl):
            self.v.rlog('Adding GSLs...    ')
            self._build_GSLs()

        if len(self._isl):
            self.v.rlog('Adding ISLs...   ')
            self._build_ISLs()

        if len(self._gs):
            self.v.rlog('Adding ground stations...  ')
            self._build_ground_stations()

        if len(self._sat):
            self.v.rlog('Adding satellites...  ')
            self._build_satellites()

        self.v.clr()

    def _build_ground_stations(self) -> None:
        for gs_name in self._gs:
            gid, terminal = self.leo_con.gs_info(gs_name)

            folium.Marker(
                [float(terminal.latitude_degree),
                 float(terminal.longitude_degree)],

                popup=f'''<i>Coordinates: {terminal.latitude_degree}, {
                    terminal.longitude_degree}</i>''',
                tooltip=f'''{gid}:{terminal.name}'''

            ).add_to(self.map)

    def _build_GSLs(self) -> None:
        for gs_name in self._gsl:
            gid = self.leo_con.ground_stations.decode_name(gs_name)
            terminal = self.leo_con.ground_stations.terminals[gid]

            for sat_name, distance_m in self.leo_con.gsls[gid]:
                sat_info = self.leo_con.sat_info(sat_name)

                trail_coordinates = [
                    (float(sat_info.nadir_latitude),
                     float(sat_info.nadir_longitude)),
                    (float(terminal.latitude_degree),
                     float(terminal.longitude_degree))
                ]

                folium.PolyLine(
                    trail_coordinates,
                    color=self._GSL_COLOR,
                    weight=self.get_thickness(gs_name, sat_name),
                    tooltip=f'''{terminal.name} to {sat_name}, {round(
                        distance_m/1000, 2
                    )}km'''
                ).add_to(self.map)

    def _build_satellites(self) -> None:
        for sat_name in self._sat:
            sat_info = self.leo_con.sat_info(sat_name)

            self._add_circle(
                float(sat_info.nadir_latitude),
                float(sat_info.nadir_longitude),
                tooltip_text=sat_name,
                color=self._SHELL_COLORS[
                    sat_info.shell_id % len(self._SHELL_COLORS)
                ],

                popup_text=f'''Name:{sat_name} O: {
                    sat_info.orbit_num} N: {sat_info.sat_num}'''
            )

    def _build_coverages(self) -> None:
        for sat_name in self._cov:
            sat_info = self.leo_con.sat_info(sat_name)
            radius = self.leo_con.shells[sat_info.shell_id].satellites[sat_info.id].coverage_cone_radius_m(
            )

            self._add_circle(
                float(sat_info.nadir_latitude),
                float(sat_info.nadir_longitude),
                radius=radius,
                tooltip_text=sat_name,
                color=self._COVERAGE_COLOR,
                opacity=self._COVERAGE_OPACITY,
                fill_opacity=self._COVERAGE_FILL_OPACITY,

                popup_text=f'''Name:{sat_name} O: {
                    sat_info.orbit_num} N: {sat_info.sat_num}'''
            )

    def _build_ISLs(self) -> None:
        for sat_name_a, sat_name_b in self._isl:
            sat_info_a = self.leo_con.sat_info(sat_name_a)
            sat_info_b = self.leo_con.sat_info(sat_name_b)
            distance_m = self.leo_con.link_length(sat_name_a, sat_name_b)

            trail_coordinates = [
                (float(sat_info_a.nadir_latitude),
                 float(sat_info_a.nadir_longitude)),
                (float(sat_info_b.nadir_latitude),
                 float(sat_info_b.nadir_longitude))
            ]

            folium.PolyLine(
                trail_coordinates,

                weight=self.get_thickness(sat_name_a, sat_name_b),
                color=self.get_color(sat_name_a, sat_name_b),

                tooltip=f'''ISL:{sat_name_a}-{sat_name_b},
                    {round(distance_m/1000, 2)}km'''
            ).add_to(self.map)

    def _add_circle(
        self,
        lat: float, long: float,
        popup_text: str = "", tooltip_text: str = "",
        color: str = "crimson", radius: float = 0.0,
        opacity: float = 1, fill_opacity: float = 1
    ) -> None:

        folium.Circle(
            radius=radius,
            location=[lat, long],
            popup=popup_text,
            color=color,
            fill=True,
            tooltip=tooltip_text,
            opacity=opacity,
            fill_opacity=fill_opacity
        ).add_to(self.map)

    def export_html(self, filename: str | None = None) -> str:
        if not filename:
            filename = f'{self.leo_con.name}.html'

        self.v.log('Exporting HTML...  ')
        self.map.save(filename)
        return filename

    def show(self) -> None:
        filename = f'{self.leo_con.name}.html'

        self.v.log('Rendering...  ')
        self.map.save(filename)
        webbrowser.open_new_tab(filename)
