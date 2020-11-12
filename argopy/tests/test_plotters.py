import pytest

import argopy
from argopy.errors import InvalidDashboard
from . import (
    requires_localftp,
    requires_connection,
    requires_matplotlib,
    has_matplotlib,
    has_seaborn,
    has_cartopy,
)
from argopy.plotters import bar_plot, plot_trajectory
from argopy import IndexFetcher as ArgoIndexFetcher

if has_matplotlib:
    import matplotlib as mpl

if has_cartopy:
    import cartopy


@requires_connection
def test_invalid_dashboard():
    with pytest.raises(InvalidDashboard):
        argopy.dashboard(wmo=5904797, type="invalid_service")


@requires_connection
def test_valid_dashboard():
    import IPython
    dsh = argopy.dashboard(wmo=5904797)
    assert isinstance(dsh, IPython.lib.display.IFrame)


@requires_localftp
@requires_matplotlib
class Test_index_plot:
    src = "localftp"
    local_ftp = argopy.tutorial.open_dataset("localftp")[0]
    requests = {
        "float": [[2901623], [2901623, 6901929, 5906072]],
        "profile": [[2901623, 12], [6901929, [5, 45]]],
        "region": [
            [-60, -40, 40.0, 60.0],
            [-60, -40, 40.0, 60.0, "2007-08-01", "2007-09-01"],
        ],
    }

    def __test_traj_plot(self, df):
        for ws in [False, has_seaborn]:
            for wc in [False, has_cartopy]:
                for legend in [True, False]:
                    fig, ax = plot_trajectory(
                        df, with_seaborn=ws, with_cartopy=wc, add_legend=legend
                    )
                    assert isinstance(fig, mpl.figure.Figure)

                    expected_ax_type = (
                        cartopy.mpl.geoaxes.GeoAxesSubplot
                        if has_cartopy and wc
                        else mpl.axes.Axes
                    )
                    assert isinstance(ax, expected_ax_type)

                    expected_lg_type = mpl.legend.Legend if legend else type(None)
                    assert isinstance(ax.get_legend(), expected_lg_type)

    def __test_bar_plot(self, df):
        for ws in [False, has_seaborn]:
            for by in [
                "institution",
                "institution_code",
                "profiler",
                "profiler_code",
                "ocean",
            ]:
                fig, ax = bar_plot(df, by=by, with_seaborn=ws)
                assert isinstance(fig, mpl.figure.Figure)

    def test_traj_plot_region(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["region"]:
                loader = ArgoIndexFetcher(src=self.src).region(arg)
                df = loader.to_dataframe()
                self.__test_traj_plot(df)

    def test_traj_plot_float(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["float"]:
                loader = ArgoIndexFetcher(src=self.src).float(arg)
                df = loader.to_dataframe()
                self.__test_traj_plot(df)

    def test_traj_plot_profile(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["profile"]:
                loader = ArgoIndexFetcher(src=self.src).profile(*arg)
                df = loader.to_dataframe()
                self.__test_bar_plot(df)

    def test_bar_plot_region(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["region"]:
                loader = ArgoIndexFetcher(src=self.src).region(arg)
                df = loader.to_dataframe()
                self.__test_bar_plot(df)

    def test_bar_plot_float(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["float"]:
                loader = ArgoIndexFetcher(src=self.src).float(arg)
                df = loader.to_dataframe()
                self.__test_bar_plot(df)

    def test_bar_plot_profile(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            for arg in self.requests["profile"]:
                loader = ArgoIndexFetcher(src=self.src).profile(*arg)
                df = loader.to_dataframe()
                self.__test_bar_plot(df)
