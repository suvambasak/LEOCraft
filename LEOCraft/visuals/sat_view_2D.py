import webbrowser

import folium

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.satellite_topology.LEO_sat_topology import LEOSatelliteTopology
from LEOCraft.visuals.view import Render


class SatView2D(Render):
    'Rendering the 2D HTML using folium packages'

    _COVERAGE_COLOR = "#FF6666"
    _COVERAGE_OPACITY = 0.15
    _COVERAGE_FILL_OPACITY = 0.05
    _GSL_COLOR = "green"

    def _add_circle(
        self,
        lat: float,
        long: float,
        popup_text: str = "",
        tooltip_text: str = "",
        color: str = "crimson",
        radius: float = 0.0,
        opacity: float = 1,
        fill_opacity: float = 1
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

        if len(self.view.gs):
            self._build_ground_stations()
        if len(self.view.gsl):
            self._build_GSLs()
        if len(self.view.sat):
            self._build_satellites()
        if len(self.view.cov):
            self._build_coverages()
        if len(self.view.isl):
            self._build_ISLs()

    def _build_ground_stations(self) -> None:
        self.v.rlog('Adding ground stations...  ')

        for gs_name in self.view.gs:
            gid = self.leo_con.ground_stations.decode_name(gs_name)
            terminal = self.leo_con.ground_stations.terminals[gid]

            folium.Marker(
                [float(terminal.latitude_degree),
                 float(terminal.longitude_degree)],

                popup=f'''<i>Coordinates: {terminal.latitude_degree}, {
                    terminal.longitude_degree}</i>''',
                tooltip=f'''{gid}:{terminal.name}'''

            ).add_to(self.map)

        self.v.clr()

    def _build_GSLs(self) -> None:
        self.v.rlog('Adding GSLs...  ')

        for gs_name in self.view.gsl:
            gid = self.leo_con.ground_stations.decode_name(gs_name)
            terminal = self.leo_con.ground_stations.terminals[gid]

            for sat_name, distance_m in self.leo_con.gsls[gid]:
                shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)
                sat_lat, sat_long = self.leo_con.shells[shell_id].satellites[sid].nadir(
                )

                trail_coordinates = [
                    (
                        float(sat_lat), float(sat_long)
                    ),
                    (
                        float(terminal.latitude_degree),
                        float(terminal.longitude_degree)
                    )
                ]

                folium.PolyLine(
                    trail_coordinates,
                    tooltip=f'''{terminal.name} to {sat_name}, {
                        round(distance_m/1000, 2)}km''',
                    color=self._GSL_COLOR
                ).add_to(self.map)

        self.v.clr()

    def _build_satellites(self) -> None:
        self.v.rlog('Adding satellites...  ')

        for sat_name in self.view.sat:
            shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)
            lat, long = self.leo_con.shells[shell_id].satellites[sid].nadir()

            self._add_circle(
                float(lat), float(long),

                popup_text=f'''Name:{sat_name} O: {shell_id} sid: {sid}''',
                tooltip_text=sat_name
            )

        self.v.clr()

    def _build_coverages(self) -> None:
        self.v.rlog('Adding coveragess...  ')

        for sat_name in self.view.cov:

            shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name)
            lat, long = self.leo_con.shells[shell_id].satellites[sid].nadir()
            radius = self.leo_con.shells[shell_id].satellites[sid].coverage_cone_radius_m(
            )

            self._add_circle(
                float(lat), float(long),
                radius=radius,

                popup_text=f'''Name:{sat_name} O: {shell_id} sid: {sid}''',
                tooltip_text=sat_name,

                color=self._COVERAGE_COLOR,
                opacity=self._COVERAGE_OPACITY,
                fill_opacity=self._COVERAGE_FILL_OPACITY,
            )

        self.v.clr()

    def _build_ISLs(self) -> None:
        self.v.rlog('Adding ISLs...  ')

        for sat_name_a, sat_name_b in self.view.isl:

            shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name_a)
            sat_loc_1 = self.leo_con.shells[shell_id].satellites[sid].nadir()
            shell_id, sid = LEOSatelliteTopology.decode_sat_name(sat_name_b)
            sat_loc_2 = self.leo_con.shells[shell_id].satellites[sid].nadir()

            trail_coordinates = [
                (float(sat_loc_1[0]), float(sat_loc_1[1])),
                (float(sat_loc_2[0]), float(sat_loc_2[1]))
            ]
            distance_m = self.leo_con.link_length(sat_name_a, sat_name_b)

            folium.PolyLine(
                trail_coordinates,
                tooltip=f'''ISL:{sat_name_a}-{sat_name_b},
                    {round(distance_m/1000, 2)}km'''
            ).add_to(self.map)

        self.v.clr()

    def export_html(self, filename: str = "index.html") -> str:
        self.v.log('Rendering...  ')

        self.map.save(filename)
        return filename

    def show(self, filename: str = "index.html") -> None:
        self.v.log('Rendering...  ')

        self.map.save(filename)
        webbrowser.open_new_tab(filename)
