import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from LEOCraft.constellations.LEO_constellation import LEOConstellation
from LEOCraft.user_terminals.terminal import UserTerminal
from LEOCraft.visuals.view import Render


class SatRawView3D(Render):
    '''Rendering constellation view in 3D cartesian coordinate system (Earth-centered Earth-fixed (ECEF) coordinates)

    Build with package:
    - Plotly (Scatter3d and surface plots)
    - Numpy (Linear transformation)
    '''

    _TEXT: str = 'text'
    _COLOR_CODE: str = 'color_code'
    _SIZE: str = 'size'

    _X: str = 'x'
    _Y: str = 'y'
    _Z: str = 'z'

    def __init__(
            self,
            leo_con: LEOConstellation,
            title: str | None = None,
            globe_visibility: bool = True,
            lat: float = 0.0,
            long: float = 0.0,
            elevation_m: float = 0.0,
            globe_radius_km: float = 6371.0
    ) -> None:
        '''
        Parameters
        ---------
        leo_con: LEOConstellation
            Object of the LEO satellite constellation

        title: str, optional
            Title of the plot (default: LEOConstellation name)

        globe_visibility: bool, optional
            Visibility of the globe inside constellation network (default: visible)

        lat: float, optional
            View latitude degree (default: 0.0)

        long: float, optional
            View longitude degree (default: 0.0)

        elevation_m: float, optional
            View elevation from the earth surface (default: 0.0)

        globe_radius_km: float, optional
            Earth radius in KM (default: 6371 km)
        '''
        super().__init__(leo_con)
        self._EARTH_RADIUS_KM = globe_radius_km

        self.fig = go.Figure()
        self.setup_layout(title, globe_visibility, lat, long, elevation_m)

    def setup_layout(
            self,
            title: str | None,
            globe_visibility: bool,
            lat: float,
            long: float,
            elevation_m: float
    ) -> None:

        def __removed_background() -> dict:
            return dict(
                title='',
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False,
                backgroundcolor='rgba(0,0,0,0)'
            )

        def __update_scene() -> dict:
            x, y, z = UserTerminal.geodetic_to_cartesian(
                lat, long, elevation_m
            )
            return dict(
                xaxis=__removed_background(),
                yaxis=__removed_background(),
                zaxis=__removed_background(),
                camera=dict(
                    eye=dict(
                        x=x/MAGIC_NUMBER,
                        y=y/MAGIC_NUMBER,
                        z=z/MAGIC_NUMBER
                    )
                )
            )

        MAGIC_NUMBER = 5500000

        self.fig.update_layout(
            margin={"b": 0, "t": 35, "l": 0},
            title=title if title else self.leo_con.name,
            scene=__update_scene()
        )

        if globe_visibility:
            self.fig.add_trace(self._build_globe())

    def build(self) -> None:

        self.v.log('Building raw view 3D...  ')

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

        if len(self._cov):
            self.v.rlog('Adding coverage cones...  ')
            self.fig.add_traces(self._build_coverages())

        self.v.clr()

    def _build_globe(self) -> go.Surface:

        # Generate the coordinates for the sphere
        phi = np.linspace(0, 2 * np.pi, 50)
        theta = np.linspace(0, np.pi, 25)
        phi, theta = np.meshgrid(phi, theta)

        x = self._EARTH_RADIUS_KM * np.sin(theta) * np.cos(phi)
        y = self._EARTH_RADIUS_KM * np.sin(theta) * np.sin(phi)
        z = self._EARTH_RADIUS_KM * np.cos(theta)

        # Create a 3D surface plot for the globe
        return go.Surface(
            x=x, y=y, z=z,

            surfacecolor=np.ones_like(x),
            colorscale=[[0, 'rgb(228,237,246)'], [1, 'rgb(228,237,246)']],
            lighting=dict(
                ambient=0.8, diffuse=0.5, specular=0.1, roughness=0.5, fresnel=0.1
            ),
            lightposition=dict(x=-1500, y=-9000, z=-90),
            hoverinfo='none', showscale=False, opacity=1
        )

    def __generate_rotation_matrix_from_vectors(self, vector_1: np.ndarray, vector_2: np.ndarray) -> np.ndarray:
        """Find the rotation matrix that aligns vector_1 to vector_2

        Paramters
        --------
        vector_1: np.ndarray
            Vector 1
        vector_2: np.ndarray
            Vector 2

        Returns
        -------
        np.ndarray
            Rotation matrix
        """

        a = (vector_1/np.linalg.norm(vector_1)).reshape(3)
        b = (vector_2 / np.linalg.norm(vector_2)).reshape(3)
        v = np.cross(a, b)
        c = np.dot(a, b)
        s = np.linalg.norm(v)
        kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        return np.eye(3) + kmat + kmat @ kmat * ((1 - c) / (s ** 2))

    def __generate_coverage_cone(
            self, sat_coordinates: np.ndarray, nadir_coordinates: np.ndarray, radius_km
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate coverage cone from the satellites to earth surface

        Parameters
        ----------
        sat_coordinates: np.ndarray
            Cartesian coordinates of the satellite
        nadir_coordinates: np.ndarray
            Cartesian coordinates of nadir of satellites
        radius_km
            Coverage cone radius in km

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            Cartesian coordinates of the coverage cone
        """

        # Compute the axis vector and the height of the cone
        axis_vector = sat_coordinates - nadir_coordinates
        height = np.linalg.norm(axis_vector)

        # Normalize the axis vector
        axis_vector_normalized = axis_vector / height

        # Create the coordinates for a cone along the z-axis
        theta = np.linspace(0, 2 * np.pi, 20)
        z = np.linspace(0, height, 15)
        theta, z = np.meshgrid(theta, z)
        r = (height - z) / height * radius_km

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Rotation matrix to align z-axis to the axis_vector
        R = self.__generate_rotation_matrix_from_vectors(
            np.array([0, 0, 1]), axis_vector_normalized
        )

        # Apply the rotation
        xyz = np.vstack((x.flatten(), y.flatten(), z.flatten()))
        rotated_xyz = R @ xyz
        x_rotated = rotated_xyz[0, :].reshape(x.shape) + nadir_coordinates[0]
        y_rotated = rotated_xyz[1, :].reshape(y.shape) + nadir_coordinates[1]
        z_rotated = rotated_xyz[2, :].reshape(z.shape) + nadir_coordinates[2]

        return x_rotated, y_rotated, z_rotated

    def _build_coverages(self) -> list[go.Surface]:

        coverage_cone_trace_list = list()

        for sat_name in self._cov:
            sat_info = self.leo_con.sat_info(sat_name)

            radius_km = self.leo_con.shells[sat_info.shell_id].satellites[sat_info.id].coverage_cone_radius_m(
            )/1000

            sat_coordinates_km = np.array(
                [sat_info.cartesian_x/1000,
                 sat_info.cartesian_y/1000,
                 sat_info.cartesian_z/1000]
            )

            nadir_coordinates_km = np.array(
                [sat_info.nadir_x/1000,
                 sat_info.nadir_y/1000,
                 sat_info.nadir_z/1000]
            )

            x, y, z = self.__generate_coverage_cone(
                sat_coordinates_km, nadir_coordinates_km, radius_km
            )

            coverage_cone_trace_list.append(go.Surface(
                x=x, y=y, z=z,

                surfacecolor=np.ones_like(x),
                colorscale=[[0, self._COVERAGE_COLOR],
                            [1, self._COVERAGE_COLOR]],

                hoverinfo='none', showscale=False, opacity=0.2
            ))

        return coverage_cone_trace_list

    def _build_ground_stations(self) -> go.Scatter3d:
        dict_list = list()

        for gs_name in self._gs:
            gid, terminal = self.leo_con.gs_info(gs_name)

            dict_list.append({
                self._TEXT: f"G-{gid} {terminal.name} lat: {terminal.latitude_degree}, lng:{terminal.longitude_degree}",
                self._X: terminal.cartesian_x,
                self._Y: terminal.cartesian_y,
                self._Z: terminal.cartesian_z,
            })

        df = pd.DataFrame.from_dict(dict_list)

        for column in [self._X, self._Y, self._Z]:
            df[column] = df[column]/1000

        return go.Scatter3d(
            name="Ground station",
            x=df[self._X],
            y=df[self._Y],
            z=df[self._Z],
            text=df[self._TEXT],
            mode="markers",
            marker=dict(
                size=self._DEFAULT_GS_SIZE,
                color=self._GROUND_STATION_COLOR
            )
        )

    def _build_GSLs(self) -> list[go.Scatter3d]:

        GSLs_trace_list = list()

        for gs_name in self._gsl:
            gid = self.leo_con.ground_stations.decode_name(gs_name)
            terminal = self.leo_con.ground_stations.terminals[gid]

            for sat_name, distance_m in self.leo_con.gsls[gid]:
                sat_info = self.leo_con.sat_info(sat_name)

                GSLs_trace_list.append(go.Scatter3d(
                    name=f"G-{gid} to {sat_name}",
                    x=[terminal.cartesian_x/1000, sat_info.cartesian_x/1000],
                    y=[terminal.cartesian_y/1000, sat_info.cartesian_y/1000],
                    z=[terminal.cartesian_z/1000, sat_info.cartesian_z/1000],

                    text=f'''GSLs: {terminal.name} {
                        round(distance_m/1000, 2)}km''',
                    mode="lines",
                    line=dict(
                        color=self._GSL_COLOR,
                        width=self.get_thickness(gs_name, sat_name)
                    )
                ))

        return GSLs_trace_list

    def _build_satellites(self) -> go.Scatter3d:
        dict_list = list()
        color_map = dict()

        for sat_name in self._sat:
            sat_info = self.leo_con.sat_info(sat_name)
            # print(sat_info)

            if sat_info.altitude_km not in color_map:
                color_map[sat_info.altitude_km] = self._shell_colors.pop()

            dict_list.append({
                self._X: sat_info.cartesian_x,
                self._Y: sat_info.cartesian_y,
                self._Z: sat_info.cartesian_z,

                # self._COLOR_CODE: self._shell_colors[
                #     sat_info.shell_id % len(self._shell_colors)
                # ],
                self._COLOR_CODE: color_map[sat_info.altitude_km],

                self._TEXT: f'''ID: {sat_name} O: {sat_info.orbit_num} N: {sat_info.sat_num} KM: {sat_info.altitude_km}''',
                self._SIZE: self._SPECIAL_SAT_SIZE if sat_name in self._special_sats else self._DEFAULT_SAT_SIZE
            })

        df = pd.DataFrame.from_dict(dict_list)

        for column in [self._X, self._Y, self._Z]:
            df[column] = df[column]/1000

        return go.Scatter3d(
            x=df[self._X],
            y=df[self._Y],
            z=df[self._Z],
            mode='markers',
            name='Satellite',
            text=df[self._TEXT],
            marker=dict(size=df[self._SIZE], color=df[self._COLOR_CODE])
        )

    def _build_ISLs(self) -> list[go.Scatter3d]:
        ISLs_trace_list = list()

        for sat_name_a, sat_name_b in self._isl:
            sat_info_a = self.leo_con.sat_info(sat_name_a)
            sat_info_b = self.leo_con.sat_info(sat_name_b)

            ISLs_trace_list.append(go.Scatter3d(
                name=f"{sat_name_a} to {sat_name_b}",

                x=[sat_info_a.cartesian_x/1000, sat_info_b.cartesian_x/1000],
                y=[sat_info_a.cartesian_y/1000, sat_info_b.cartesian_y/1000],
                z=[sat_info_a.cartesian_z/1000, sat_info_b.cartesian_z/1000],


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
        'Start the view'
        self.v.log('Rendering...  ')
        self.fig.show()

    def export_html(self, filename: str | None = None) -> str:
        '''Explort into a HTML file

        Parameters
        -----------
        filename: str, optional
            HTML file name (default: classname.html)
        '''

        if not filename:
            filename = f'{self.leo_con.name}.html'

        self.v.log('Exporting HTML...  ')
        self.fig.write_html(filename)
        return filename

    def export_png(self, filename: str | None = None) -> str:
        '''Export into a PNG file

        Parameters
        ----------
        filename: str, optional
            PNG file name (default: classname.png)
        '''

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
