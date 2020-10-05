import xarray as xr
import pytest

import argopy
from argopy import IndexFetcher as ArgoIndexFetcher
from argopy.errors import InvalidFetcherAccessPoint, InvalidFetcher, ErddapServerError
from . import (
    AVAILABLE_INDEX_SOURCES,
    requires_fetcher_index,
    requires_connected_erddap_index,
    requires_localftp_index,
    requires_connection,
)


@requires_fetcher_index
def test_invalid_accesspoint():
    src = list(AVAILABLE_INDEX_SOURCES.keys())[0]  # Use the first valid data source
    with pytest.raises(InvalidFetcherAccessPoint):
        ArgoIndexFetcher(
            src=src
        ).invalid_accesspoint.to_xarray()  # Can't get data if access point not defined first
    with pytest.raises(InvalidFetcherAccessPoint):
        ArgoIndexFetcher(
            src=src
        ).to_xarray()  # Can't get data if access point not defined first


def test_invalid_fetcher():
    with pytest.raises(InvalidFetcher):
        ArgoIndexFetcher(src="invalid_fetcher").to_xarray()


@requires_connection
@requires_fetcher_index
class Test_AllBackends:
    """ Test main API facade for all available index fetching backends """

    local_ftp = argopy.tutorial.open_dataset("localftp")[0]

    # todo Determine the list of output format to test
    # what else beyond .to_xarray() ?

    fetcher_opts = {}

    # Define API entry point options to tests:
    # These should be available online and with the argopy-data dummy gdac ftp
    args = {}
    args["float"] = [[2901623], [6901929, 2901623]]
    args["region"] = [
        [-60, -40, 40.0, 60.0],
        [-60, -40, 40.0, 60.0, "2007-08-01", "2007-09-01"],
    ]
    args["profile"] = [[2901623, 2], [6901929, [5, 45]]]

    def __test_float(self, bk, **ftc_opts):
        """ Test float index fetching for a given backend """
        for arg in self.args["float"]:
            try:
                options = {**self.fetcher_opts, **ftc_opts}
                f = ArgoIndexFetcher(src=bk, **options).float(arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
            except ErddapServerError:
                # Test is passed even if something goes wrong with the erddap server
                pass
            except Exception:
                raise

    def __test_profile(self, bk, **ftc_opts):
        """ Test profile index fetching for a given backend """
        for arg in self.args["profile"]:
            try:
                options = {**self.fetcher_opts, **ftc_opts}
                f = ArgoIndexFetcher(src=bk, **options).profile(*arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
            except ErddapServerError:
                # Test is passed even if something goes wrong with the erddap server
                pass
            except Exception:
                raise

    def __test_region(self, bk, **ftc_opts):
        """ Test float index fetching for a given backend """
        for arg in self.args["region"]:
            try:
                options = {**self.fetcher_opts, **ftc_opts}
                f = ArgoIndexFetcher(src=bk, **options).region(arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
            except ErddapServerError:
                # Test is passed even if something goes wrong with the erddap server
                pass
            except Exception:
                raise

    @pytest.mark.skip(reason="Waiting for https://github.com/euroargodev/argopy/issues/16")
    @requires_connected_erddap_index
    def test_float_erddap(self):
        self.__test_float("erddap")

    @requires_localftp_index
    def test_float_localftp(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            self.__test_float("localftp", index_file="ar_index_global_prof.txt")

    @requires_localftp_index
    def test_profile_localftp(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            self.__test_profile("localftp", index_file="ar_index_global_prof.txt")

    @pytest.mark.skip(reason="Waiting for https://github.com/euroargodev/argopy/issues/16")
    @requires_connected_erddap_index
    def test_region_erddap(self):
        self.__test_region("erddap")

    @requires_localftp_index
    def test_region_localftp(self):
        with argopy.set_options(local_ftp=self.local_ftp):
            self.__test_region("localftp", index_file="ar_index_global_prof.txt")
