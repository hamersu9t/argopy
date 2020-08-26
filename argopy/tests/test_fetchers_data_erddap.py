import numpy as np
import xarray as xr

import pytest
import unittest
import tempfile

import argopy
from argopy import DataFetcher as ArgoDataFetcher
from argopy.errors import ErddapServerError, CacheFileNotFound, FileSystemHasNoCache
from argopy.utilities import (
    list_available_data_src,
    isconnected,
    isAPIconnected,
    erddap_ds_exists,
    is_list_of_strings,
    is_list_of_integers,
)
from . import (
    requires_connected_erddap,
    requires_connected_erddap_phy,
    requires_connected_erddap_bgc,
    requires_connected_erddap_ref,
)

argopy.set_options(api_timeout=3 * 60)  # From Github actions, requests can take a while
AVAILABLE_SOURCES = list_available_data_src()
CONNECTED = isconnected()
CONNECTEDAPI = isAPIconnected(src="erddap", data=True)
if CONNECTEDAPI:
    DSEXISTS = erddap_ds_exists(ds="ArgoFloats")
    DSEXISTS_bgc = erddap_ds_exists(ds="ArgoFloats-bio")
    DSEXISTS_ref = erddap_ds_exists(ds="ArgoFloats-ref")
else:
    DSEXISTS = False
    DSEXISTS_bgc = False
    DSEXISTS_ref = False


@requires_connected_erddap
class Test_Backend:
    """ Test main API facade for all available dataset and access points of the ERDDAP fetching backend """

    src = "erddap"

    @requires_connected_erddap_phy
    def test_cachepath_notfound(self):
        with tempfile.TemporaryDirectory() as testcachedir:
            with argopy.set_options(cachedir=testcachedir):
                loader = ArgoDataFetcher(src=self.src, cache=True).profile(6902746, 34)
                with pytest.raises(CacheFileNotFound):
                    loader.fetcher.cachepath

    @requires_connected_erddap_phy
    def test_nocache(self):
        with argopy.set_options(cachedir="dummy"):
            loader = ArgoDataFetcher(src=self.src, cache=False).profile(6902746, 34)
            loader.to_xarray()
            with pytest.raises(FileSystemHasNoCache):
                loader.fetcher.cachepath

    @requires_connected_erddap_phy
    def test_clearcache(self):
        with tempfile.TemporaryDirectory() as testcachedir:
            with argopy.set_options(cachedir=testcachedir):
                loader = ArgoDataFetcher(src=self.src, cache=True).float(
                    [1901393, 6902746]
                )
                try:
                    loader.to_xarray()
                    loader.clear_cache()
                    with pytest.raises(CacheFileNotFound):
                        loader.fetcher.cachepath
                except ErddapServerError:  # Test is passed when something goes wrong because of the erddap server, not our fault !
                    pass
                except Exception:
                    raise

    @requires_connected_erddap_phy
    def test_caching_float(self):
        with tempfile.TemporaryDirectory() as testcachedir:
            with argopy.set_options(cachedir=testcachedir):
                loader = ArgoDataFetcher(src=self.src, cache=True).float(
                    [1901393, 6902746]
                )
                try:
                    # 1st call to load and save to cachedir:
                    ds = loader.to_xarray()
                    # 2nd call to load from cached file:
                    ds = loader.to_xarray()
                    assert isinstance(ds, xr.Dataset)
                    assert is_list_of_strings(loader.fetcher.uri)
                    assert is_list_of_strings(loader.fetcher.cachepath)
                except ErddapServerError:  # Test is passed when something goes wrong because of the erddap server, not our fault !
                    pass
                except Exception:
                    raise

    @requires_connected_erddap_phy
    def test_caching_profile(self):
        with tempfile.TemporaryDirectory() as testcachedir:
            with argopy.set_options(cachedir=testcachedir):
                loader = ArgoDataFetcher(src=self.src, cache=True).profile(6902746, 34)
                try:
                    # 1st call to load and save to cachedir:
                    ds = loader.to_xarray()
                    # 2nd call to load from cached file
                    ds = loader.to_xarray()
                    assert isinstance(ds, xr.Dataset)
                    assert is_list_of_strings(loader.fetcher.uri)
                    assert is_list_of_strings(loader.fetcher.cachepath)
                except ErddapServerError:  # Test is passed when something goes wrong because of the erddap server, not our fault !
                    pass
                except Exception:
                    raise

    @requires_connected_erddap_phy
    def test_caching_region(self):
        with tempfile.TemporaryDirectory() as testcachedir:
            with argopy.set_options(cachedir=testcachedir):
                loader = ArgoDataFetcher(src=self.src, cache=True).region(
                    [-40, -30, 30, 40, 0, 100, "2011", "2012"]
                )
                try:
                    # 1st call to load and save to cachedir:
                    ds = loader.to_xarray()
                    # 2nd call to load from cached file
                    ds = loader.to_xarray()
                    assert isinstance(ds, xr.Dataset)
                    assert is_list_of_strings(loader.fetcher.uri)
                    assert is_list_of_strings(loader.fetcher.cachepath)
                except ErddapServerError:  # Test is passed when something goes wrong because of the erddap server, not our fault !
                    pass
                except Exception:
                    raise

    @requires_connected_erddap_phy
    def test_N_POINTS(self):
        n = (
            ArgoDataFetcher(src=self.src)
            .region([-70, -65, 35.0, 40.0, 0, 10.0, "2012-01", "2013-12"])
            .fetcher.N_POINTS
        )
        assert isinstance(n, int)

    def __testthis_profile(self, dataset):
        for arg in self.args["profile"]:
            try:
                f = ArgoDataFetcher(src=self.src, ds=dataset).profile(*arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
                assert is_list_of_strings(f.fetcher.uri)
            except ErddapServerError:
                # Test is passed when something goes wrong because of the erddap server, not our fault !
                pass
            except Exception:
                print(
                    "ERDDAP request:\n", f.fetcher.uri,
                )
                pass

    def __testthis_float(self, dataset):
        for arg in self.args["float"]:
            try:
                f = ArgoDataFetcher(src=self.src, ds=dataset).float(arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
                assert is_list_of_strings(f.fetcher.uri)
            except ErddapServerError:
                # Test is passed when something goes wrong because of the erddap server, not our fault !
                pass
            except Exception:
                print(
                    "ERDDAP request:\n", f.fetcher.uri,
                )
                pass

    def __testthis_region(self, dataset):
        for arg in self.args["region"]:
            try:
                f = ArgoDataFetcher(src=self.src, ds=dataset).region(arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
                assert is_list_of_strings(f.fetcher.uri)
            except ErddapServerError:
                # Test is passed when something goes wrong because of the erddap server, not our fault !
                pass
            except Exception:
                print(
                    "ERDDAP request:\n", f.fetcher.uri,
                )
                pass

    def __testthis(self, dataset):
        for access_point in self.args:
            if access_point == "profile":
                self.__testthis_profile(dataset)
            elif access_point == "float":
                self.__testthis_float(dataset)
            elif access_point == "region":
                self.__testthis_region(dataset)

    @requires_connected_erddap_phy
    def test_phy_float(self):
        self.args = {}
        self.args["float"] = [[1901393], [1901393, 6902746]]
        self.__testthis("phy")

    @requires_connected_erddap_phy
    def test_phy_profile(self):
        self.args = {}
        self.args["profile"] = [
            [6902746, 34],
            [6902746, np.arange(12, 13)],
            [6902746, [1, 12]],
        ]
        self.__testthis("phy")

    @requires_connected_erddap_phy
    def test_phy_region(self):
        self.args = {}
        self.args["region"] = [
            [-70, -65, 35.0, 40.0, 0, 10.0],
            [-70, -65, 35.0, 40.0, 0, 10.0, "2012-01", "2013-12"],
        ]
        self.__testthis("phy")

    @requires_connected_erddap_bgc
    def test_bgc_float(self):
        self.args = {}
        self.args["float"] = [[5903248], [7900596, 2902264]]
        self.__testthis("bgc")

    @requires_connected_erddap_bgc
    def test_bgc_profile(self):
        self.args = {}
        self.args["profile"] = [
            [5903248, 34],
            [5903248, np.arange(12, 14)],
            [5903248, [1, 12]],
        ]
        self.__testthis("bgc")

    @requires_connected_erddap_bgc
    def test_bgc_region(self):
        self.args = {}
        self.args["region"] = [
            [-70, -65, 35.0, 40.0, 0, 10.0],
            [-70, -65, 35.0, 40.0, 0, 10.0, "2012-01-1", "2012-12-31"],
        ]
        self.__testthis("bgc")

    @requires_connected_erddap_ref
    def test_ref_region(self):
        self.args = {}
        self.args["region"] = [
            [-70, -65, 35.0, 40.0, 0, 10.0],
            [-70, -65, 35.0, 40.0, 0, 10.0, "2012-01-01", "2012-12-31"],
        ]
        self.__testthis("ref")


@requires_connected_erddap_phy
class Test_BackendParallel:
    """ This test backend for parallel requests """

    src = "erddap"
    requests = {}
    requests["region"] = [
        [-60, -55, 40.0, 45.0, 0.0, 10.0],
        [-60, -55, 40.0, 45.0, 0.0, 10.0, "2007-08-01", "2007-09-01"],
    ]
    requests["wmo"] = [[6902766, 6902772, 6902914]]

    def test_methods(self):
        args_list = [
            {"src": self.src, "parallel": "thread"},
            {"src": self.src, "parallel": True, "parallel_method": "thread"},
        ]
        for fetcher_args in args_list:
            loader = ArgoDataFetcher(**fetcher_args).float(self.requests["wmo"][0])
            assert isinstance(loader, argopy.fetchers.ArgoDataFetcher)

        args_list = [
            {"src": self.src, "parallel": True, "parallel_method": "toto"},
            {"src": self.src, "parallel": "process"},
            {"src": self.src, "parallel": True, "parallel_method": "process"},
        ]
        for fetcher_args in args_list:
            with pytest.raises(ValueError):
                ArgoDataFetcher(**fetcher_args).float(self.requests["wmo"][0])

    def test_chunks_region(self):
        for access_arg in self.requests["region"]:
            fetcher_args = {
                "src": self.src,
                "parallel": True,
                "chunks": {"lon": 1, "lat": 2, "dpt": 1, "time": 2},
            }
            try:
                f = ArgoDataFetcher(**fetcher_args).region(access_arg)
                assert isinstance(f.to_xarray(), xr.Dataset)
                assert is_list_of_strings(f.fetcher.uri)
                assert len(f.fetcher.uri) == 4
            except ErddapServerError:
                # Test is passed when something goes wrong because of the erddap server, not our fault !
                pass
            except Exception:
                print(
                    "ERDDAP request:\n", f.fetcher.uri,
                )
                pass

    def test_chunks_wmo(self):
        for access_arg in self.requests["wmo"]:
            fetcher_args = {"src": self.src, "parallel": True, "chunks": {"wmo": 2}}
            try:
                # f = ArgoDataFetcher(**fetcher_args).float(access_arg)
                f = ArgoDataFetcher(**fetcher_args).profile(access_arg, 12)
                assert isinstance(f.to_xarray(), xr.Dataset)
                assert is_list_of_strings(f.fetcher.uri)
                assert len(f.fetcher.uri) == 2
            except ErddapServerError:
                # Test is passed when something goes wrong because of the erddap server, not our fault !
                pass
            except Exception:
                print(
                    "ERDDAP request:\n", f.fetcher.uri,
                )
                pass


if __name__ == "__main__":
    unittest.main()
