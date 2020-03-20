#!/bin/env python
# -*coding: UTF-8 -*-
#

import os
import sys
import numpy as np
import pandas as pd
import xarray as xr

from argopy.errors import NetCDF4FileNotFoundError, InvalidDatasetStructure

@xr.register_dataset_accessor('argo')
class ArgoAccessor:
    """

        Class registered under scope ``argo`` to access a :class:`xarray.Dataset` object.

        # Ensure all variables are of the Argo required dtype
        ds.argo.cast_types()

        # Convert a collection of points into a collection of profiles
        ds.argo.point2profile()

        #todo

        # Convert a collection of profiles to a collection of points
        ds.argo.profile2point()

        # Make sure that the dataset complies with Argo vocabulary
        # Should be done at init with a private function ???
        # This could be usefull if a netcdf file is open directly
        ds.argo.check()



     """
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._added = list() # Will record all new variables added by argo
        self._dims = list(xarray_obj.dims.keys()) # Store the initial list of dimensions

        if 'N_PROF' in self._dims:
            self._type = 'profile'
        elif 'index' in self._dims:
            self._type = 'point'
        else:
            raise InvalidDatasetStructure("Argo dataset structure not recognised")

    def _add_history(self, txt):
        if 'history' in self._obj.attrs:
            self._obj.attrs['history'] += "; %s" % txt
        else:
            self._obj.attrs['history'] = txt

    def cast_types(self):
        """ Make sure variables are of the appropriate types

            This is hard coded, but should be retrieved from an API somewhere
            Should be able to handle all possible variables encountered in the Argo dataset
        """
        ds = self._obj

        def cast_this(da, type):
            #         print("\n")
            try:
                da.values = da.values.astype(type)
                da.attrs['casted'] = True
            except:
                print("Oops!", sys.exc_info()[0], "occured.")
                print("Fail to cast: ", da.dtype, "into:", type, "for: ", da.name)
                print("Encountered values:", np.unique(da))
            return da

        list_str = ['PLATFORM_NUMBER', 'DATA_MODE', 'DIRECTION', 'DATA_CENTRE', 'DATA_TYPE', 'FORMAT_VERSION',
                    'HANDBOOK_VERSION',
                    'PROJECT_NAME', 'PI_NAME', 'STATION_PARAMETERS', 'DATA_CENTER', 'DC_REFERENCE',
                    'DATA_STATE_INDICATOR',
                    'PLATFORM_TYPE', 'FIRMWARE_VERSION', 'POSITIONING_SYSTEM', 'PROFILE_PRES_QC', 'PROFILE_PSAL_QC',
                    'PROFILE_TEMP_QC',
                    'PARAMETER', 'SCIENTIFIC_CALIB_EQUATION', 'SCIENTIFIC_CALIB_COEFFICIENT',
                    'SCIENTIFIC_CALIB_COMMENT',
                    'HISTORY_INSTITUTION', 'HISTORY_STEP', 'HISTORY_SOFTWARE', 'HISTORY_SOFTWARE_RELEASE',
                    'HISTORY_REFERENCE',
                    'HISTORY_ACTION', 'HISTORY_PARAMETER', 'VERTICAL_SAMPLING_SCHEME', 'FLOAT_SERIAL_NO']
        list_int = ['PLATFORM_NUMBER', 'WMO_INST_TYPE', 'WMO_INST_TYPE', 'CYCLE_NUMBER', 'CONFIG_MISSION_NUMBER']
        list_datetime = ['REFERENCE_DATE_TIME', 'DATE_CREATION', 'DATE_UPDATE',
                         'JULD', 'JULD_LOCATION', 'SCIENTIFIC_CALIB_DATE', 'HISTORY_DATE']

        for v in ds.data_vars:
            ds[v].attrs['casted'] = False
            if v in list_str and ds[v].dtype == 'O':  # Object
                ds[v] = cast_this(ds[v], str)

            if v in list_int:  # and ds[v].dtype == 'O':  # Object
                ds[v] = cast_this(ds[v], int)

            if v in list_datetime and ds[v].dtype == 'O':  # Object
                if 'conventions' in ds[v].attrs and ds[v].attrs['conventions'] == 'YYYYMMDDHHMISS':
                    if ds[v].size != 0:
                        if len(ds[v].dims) <= 2:
                            val = ds[v].astype(str).values.astype('U14')
                            val[val == '              '] = 'nan'  # This should not happen, but still ! That's real world data
                            ds[v].values = pd.to_datetime(val, format='%Y%m%d%H%M%S')
                        else:
                            s = ds[v].stack(dummy_index=ds[v].dims)
                            val = s.astype(str).values.astype('U14')
                            val[val == '              '] = 'nan'  # This should not happen, but still ! That's real world data
                            s.values = pd.to_datetime(val, format='%Y%m%d%H%M%S')
                            ds[v].values = s.unstack('dummy_index')
                        ds[v] = cast_this(ds[v], np.datetime64)
                    else:
                        ds[v] = cast_this(ds[v], np.datetime64)

                elif v == 'SCIENTIFIC_CALIB_DATE':
                    ds[v] = cast_this(ds[v], str)
                    s = ds[v].stack(dummy_index=ds[v].dims)
                    s.values = pd.to_datetime(s.values, format='%Y%m%d%H%M%S')
                    ds[v].values = (s.unstack('dummy_index')).values
                    ds[v] = cast_this(ds[v], np.datetime64)

            if "QC" in v and "PROFILE" not in v:
                if ds[v].dtype == 'O':  # convert object to string
                    ds[v] = cast_this(ds[v], str)

                # Address weird string values:
                # (replace missing or nan values by a '0' that will be cast as a integer later

                if ds[v].dtype == '<U3':  # string, len 3 because of a 'nan' somewhere
                    ii = ds[v] == '   '  # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                    ii = ds[v] == 'nan'  # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                    ds[v] = cast_this(ds[v], np.dtype('U1'))  # Get back to regular U1 string

                if ds[v].dtype == '<U1':  # string
                    ii = ds[v] == ' '  # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                    ii = ds[v] == 'n'  # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                # finally convert QC strings to integers:
                ds[v] = cast_this(ds[v], int)

            if ds[v].dtype != 'O':
                ds[v].attrs['casted'] = True
        return ds

    def cast_types_deprec(self):
        """ Make sure variables are of the appropriate types

            This is hard coded, but should be retrieved from an API somewhere
        """
        if self._type != 'point':
            raise InvalidDatasetStructure("Method only available for a collection of points")
        ds = self._obj

        def cast_this(da, type):
            try:
                da.values = da.values.astype(type)
            except ValueError:
                print("Fail to cast: ", da.dtype, "into:", type)
                print("Encountered values:", np.unique(da))
            return da

        for v in ds.data_vars:
            if "QC" in v:
                if ds[v].dtype == 'O': # convert object to string
                    ds[v] = cast_this(ds[v], str)

                # Address weird string values:
                # (replace missing or nan values by a '0' that will be cast as a integer later

                if ds[v].dtype == '<U3': # string, len 3 because of a 'nan' somewhere
                    ii = ds[v] == '   ' # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                    ii = ds[v] == 'nan' # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                    ds[v] = cast_this(ds[v], np.dtype('U1')) # Get back to regular U1 string

                if ds[v].dtype == '<U1': # string
                    ii = ds[v] == ' ' # This should not happen, but still ! That's real world data
                    ds[v] = xr.where(ii, '0', ds[v])

                # finally convert QC strings to integers:
                ds[v] = cast_this(ds[v], int)

            if v == 'PLATFORM_NUMBER' and ds['PLATFORM_NUMBER'].dtype == 'float64':  # Object
                ds['PLATFORM_NUMBER'] = cast_this(ds['PLATFORM_NUMBER'], int)

            if v == 'DATA_MODE' and ds['DATA_MODE'].dtype == 'O':  # Object
                ds['DATA_MODE'] = cast_this(ds['DATA_MODE'], str)
            if v == 'DIRECTION' and ds['DIRECTION'].dtype == 'O':  # Object
                ds['DIRECTION'] = cast_this(ds['DIRECTION'], str)
        return ds

    def filter_data_mode(self, keep_error=True):
        """ Filter variables according to their data mode

            For data mode 'R' and 'A': keep <PARAM> (eg: 'PRES', 'TEMP' and 'PSAL')
            For data mode 'D': keep <PARAM_ADJUSTED> (eg: 'PRES_ADJUSTED', 'TEMP_ADJUSTED' and 'PSAL_ADJUSTED')

            This applies to <PARAM> and <PARAM_QC>
        """

        #########
        # Sub-functions
        #########
        def ds_split_datamode(xds):
            """ Create one dataset for each of the data_mode

                Split full dataset into 3 datasets
            """
            # Real-time:
            argo_r = ds.where(ds['DATA_MODE'] == 'R', drop=True)
            for v in plist:
                vname = v.upper() + '_ADJUSTED'
                if vname in argo_r:
                    argo_r = argo_r.drop_vars(vname)
                vname = v.upper() + '_ADJUSTED_QC'
                if vname in argo_r:
                    argo_r = argo_r.drop_vars(vname)
                vname = v.upper() + '_ADJUSTED_ERROR'
                if vname in argo_r:
                    argo_r = argo_r.drop_vars(vname)
            # Real-time adjusted:
            argo_a = ds.where(ds['DATA_MODE'] == 'A', drop=True)
            for v in plist:
                vname = v.upper()
                if vname in argo_a:
                    argo_a = argo_a.drop_vars(vname)
                vname = v.upper() + '_QC'
                if vname in argo_a:
                    argo_a = argo_a.drop_vars(vname)
            # Delayed mode:
            argo_d = ds.where(ds['DATA_MODE'] == 'D', drop=True)
            return argo_r, argo_a, argo_d

        def fill_adjusted_nan(ds, vname):
            """Fill in the adjusted field with the non-adjusted wherever it is NaN

               Ensure to have values even for bad QC data in delayed mode
            """
            ii = ds.where(np.isnan(ds[vname + '_ADJUSTED']), drop=1)['index']
            ds[vname + '_ADJUSTED'].loc[dict(index=ii)] = ds[vname].loc[dict(index=ii)]
            return ds

        def new_arrays(argo_r, argo_a, argo_d, vname):
            """ Merge the 3 datasets into a single ine with the appropriate fields

                Homogeneise variable names.
                Based on xarray merge function with ’no_conflicts’: only values
                which are not null in both datasets must be equal. The returned
                dataset then contains the combination of all non-null values.

                Return a xarray.DataArray
            """
            DS = xr.merge(
                (argo_r[vname],
                 argo_a[vname + '_ADJUSTED'].rename(vname),
                 argo_d[vname + '_ADJUSTED'].rename(vname)))
            DS_QC = xr.merge((
                argo_r[vname + '_QC'],
                argo_a[vname + '_ADJUSTED_QC'].rename(vname + '_QC'),
                argo_d[vname + '_ADJUSTED_QC'].rename(vname + '_QC')))
            if keep_error:
                DS_ERROR = xr.merge((
                    argo_a[vname + '_ADJUSTED_ERROR'].rename(vname + '_ERROR'),
                    argo_d[vname + '_ADJUSTED_ERROR'].rename(vname + '_ERROR')))
                DS = xr.merge((DS, DS_QC, DS_ERROR))
            else:
                DS = xr.merge((DS, DS_QC))
            return DS

        #########
        # filter
        #########
        ds = self._obj

        # Define variables to filter:
        possible_list = ['PRES', 'TEMP', 'PSAL', 'DOXY']
        plist = [p for p in possible_list if p in ds.data_vars]

        # Create one dataset for each of the data_mode:
        argo_r, argo_a, argo_d = ds_split_datamode(ds)

        # Fill in the adjusted field with the non-adjusted wherever it is NaN
        for v in plist:
            argo_d = fill_adjusted_nan(argo_d, v.upper())

        # Drop QC fields in delayed mode dataset:
        for v in plist:
            vname = v.upper()
            if vname in argo_d:
                argo_d = argo_d.drop_vars(vname)
            vname = v.upper() + '_QC'
            if vname in argo_d:
                argo_d = argo_d.drop_vars(vname)

        # Create new arrays with the appropriate variables:
        PRES = new_arrays(argo_r, argo_a, argo_d, 'PRES')
        TEMP = new_arrays(argo_r, argo_a, argo_d, 'TEMP')
        PSAL = new_arrays(argo_r, argo_a, argo_d, 'PSAL')
        if 'doxy' in plist:
            DOXY = new_arrays(argo_r, argo_a, argo_d, 'DOXY')

        # Create final dataset by merging all available variables
        if 'doxy' in plist:
            final = xr.merge((TEMP, PSAL, PRES, DOXY))
        else:
            final = xr.merge((TEMP, PSAL, PRES))

        # Merge with all other variables:
        other_variables = list(set([v for v in list(ds.data_vars) if 'ADJUSTED' not in v]) - set(list(final.data_vars)))
        # other_variables.remove('DATA_MODE')  # Not necessary anymore
        for p in other_variables:
            final = xr.merge((final, ds[p]))

        final.attrs = ds.attrs
        final.argo._add_history('Variables filtered according to DATA_MODE')
        final = final[np.sort(final.data_vars)]

        # Cast data types and add attributes:
        final = final.argo.cast_types()

        return final

    def point2profile(self):
        """ Transform a collection of points into a collection of profiles

        """
        if self._type != 'point':
            raise InvalidDatasetStructure("Method only available to a collection of points")
        ds = self._obj

        def fillvalue(da):
            """ Return fillvalue for a dataarray """
            # https://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.kind.html#numpy.dtype.kind
            if da.dtype.kind in ['U']:
                fillvalue = ' '
            elif da.dtype.kind == 'i':
                fillvalue = 99999
            elif da.dtype.kind == 'M':
                fillvalue = np.datetime64("NaT")
            else:
                fillvalue = np.nan
            return fillvalue

        def uid(wmo_or_uid, *cyc):
            """ UID encoder/decoder

                unique_float_profile_id = uid(690024,34) # Encode
                wmo, cyc = uid(unique_float_profile_id) # Decode
            """
            if cyc:
                return np.vectorize(int)(1e4 * wmo_or_uid + cyc).ravel()
            else:
                return np.vectorize(int)(wmo_or_uid / 1e4), -np.vectorize(int)(
                    1e4 * np.vectorize(int)(wmo_or_uid / 1e4) - wmo_or_uid)

        # Find the maximum nb of points for a single profile:
        ds['dummy_argo_counter'] = xr.DataArray(np.ones_like(ds['index'].values), dims='index',
                                                coords={'index': ds['index']})
        ds['dummy_argo_uid'] = xr.DataArray(uid(ds['PLATFORM_NUMBER'].values, ds['CYCLE_NUMBER'].values),
                                            dims='index', coords={'index': ds['index']})
        that = ds.groupby('dummy_argo_uid').sum()['dummy_argo_counter']
        N_LEVELS = int(that.max().values)
        N_PROF = len(np.unique(ds['dummy_argo_uid']))
        assert N_PROF * N_LEVELS >= len(ds['index'])

        # Create a new dataset
        # with empty ['N_PROF', 'N_LEVELS'] arrays for each variables of the dataset
        new_ds = []
        for vname in ds.data_vars:
            if ds[vname].dims == ('index',):
                new_ds.append(xr.DataArray(np.full((N_PROF, N_LEVELS), fillvalue(ds[vname]), dtype=ds[vname].dtype),
                                           dims=['N_PROF', 'N_LEVELS'],
                                           coords={'N_PROF': np.arange(N_PROF),
                                                   'N_LEVELS': np.arange(N_LEVELS)},
                                           name=vname))
        # Also add coordinates:
        for vname in ds.coords:
            if ds[vname].dims == ('index',):
                new_ds.append(xr.DataArray(np.full((N_PROF,), fillvalue(ds[vname]), dtype=ds[vname].dtype),
                                           dims=['N_PROF'],
                                           coords={'N_PROF': np.arange(0, N_PROF)},
                                           name=vname))
        new_ds = xr.merge(new_ds)
        for vname in ds.coords:
            if ds[vname].dims == ('index',):
                new_ds = new_ds.set_coords(vname)
        new_ds = new_ds.drop('index')

        # Drop N_LEVELS dims:
        vlist = ['PLATFORM_NUMBER', 'CYCLE_NUMBER']
        for vname in vlist:
            new_ds[vname] = new_ds[vname].isel(N_LEVELS=0).drop('N_LEVELS')
        # Fill in other coordinates
        vlist = ['LATITUDE', 'LONGITUDE', 'TIME', 'JULD']
        for i_prof, dummy_argo_uid in enumerate(np.unique(ds['dummy_argo_uid'])):
            wmo, cyc = uid(dummy_argo_uid)
            new_ds['PLATFORM_NUMBER'].loc[dict(N_PROF=i_prof)] = wmo
            new_ds['CYCLE_NUMBER'].loc[dict(N_PROF=i_prof)] = cyc
            that = ds.where(ds['PLATFORM_NUMBER'] == wmo, drop=1).where(ds['CYCLE_NUMBER'] == cyc, drop=1)
            for vname in vlist:
                if vname in new_ds.data_vars:
                    new_ds[vname].loc[dict(N_PROF=i_prof)] = np.unique(that[vname].values)[0]

        # Fill other variables with appropriate measurements:
        for i_prof in new_ds['N_PROF']:
            wmo = new_ds['PLATFORM_NUMBER'].sel(N_PROF=i_prof).values
            cyc = new_ds['CYCLE_NUMBER'].sel(N_PROF=i_prof).values
            that = ds.where(ds['PLATFORM_NUMBER'] == wmo, drop=1).where(ds['CYCLE_NUMBER'] == cyc, drop=1)
            N = len(that['index'])  # nb of measurements for this profile
            for vname in ds.data_vars:
                if ds[vname].dims == ('index',) and 'N_LEVELS' in new_ds[vname].dims:
                    new_ds[vname].sel(N_PROF=i_prof).loc[dict(N_LEVELS=range(0, N))] = that[vname].values

        new_ds = new_ds.drop_vars(['dummy_argo_counter', 'dummy_argo_uid'])
        new_ds = new_ds[np.sort(new_ds.data_vars)]
        new_ds.attrs = ds.attrs
        new_ds.attrs['sparsiness'] = np.round(len(ds['index']) * 100 / (N_PROF * N_LEVELS),2)

        self._type = 'profile'
        return new_ds

    def profile2point(self):
        """ Convert a collection of profiles to a collection of points """
        if self._type != 'profile':
            raise InvalidDatasetStructure("Method only available for a collection of profiles (N_PROF dimemsion)")
        ds = self._obj
        ds, = xr.broadcast(ds)
        ds = ds.stack(index=list(ds.dims))
        ds = ds.reset_index('index').drop(['N_PROF', 'N_LEVELS'])
        ds['index'] = np.arange(0, len(ds['index']))
        possible_coords = ['LATITUDE', 'LONGITUDE', 'TIME', 'JULD']
        for c in possible_coords:
            if c in ds.data_vars:
                ds = ds.set_coords(c)
        ds = ds[np.sort(ds.data_vars)]
        return ds

class LocalLoader(object):
    """
        A generic loader class based on xarray.
        If it can't find a file, it raises a specific error for easy catching.
    """
    def __init__(self):
        self._dac = {'KM': 'kma',
                     'IF': 'coriolis',
                     'AO': 'aoml',
                     'CS': 'csiro',
                     'KO': 'kordi',
                     'JA': 'jma',
                     'HZ': 'csio',
                     'IN': 'incois',
                     'NM': 'nmdis',
                     'ME': 'meds',
                     'BO': 'bodc'}

    @staticmethod
    def _load_nc(file_path, verbose):
        """
        Loads a .nc file using xarray, with a check for file 404s.
        :param file_path:
        :return:
        """
        if os.path.isfile(file_path):
            return xr.open_dataset(file_path, decode_times=False)
        else:
            raise NetCDF4FileNotFoundError(path=file_path, verbose=verbose)

class ArgoMultiProfLocalLoader(LocalLoader):
    """
    Set the snapshot root path when you create the instance.
    Then, it knows how to navigate the folder structure of a snapshot.
    """
    def __init__(self, argo_root_path):
        LocalLoader.__init__(self)
        self.argo_root_path = argo_root_path

    def load_from_inst_code(self, institute_code, wmo, verbose=True):
        """
        Wrapper load function for argo.
        :param institute_code: the code used to identify institutes (e.g. "IF")
        :param wmo: the wmo floater ID (int)
        :param verbose: prints error message
        :return: the contents as an xrarray
        """
        doifile = os.path.join(self.argo_root_path, self._dac[institute_code], str(wmo), ("%i_prof.nc" % wmo))
        return self._load_nc(doifile, verbose=verbose)

    def load_from_inst(self, institute, wmo, verbose=True):
        """
        Wrapper load function for argo.
        :param institute: the name of the institute (e.g. "coriolis")
        :param wmo: the wmo floater ID (int)
        :param verbose: prints error message
        :return: the contents as an xrarray
        """
        doifile = os.path.join(self.argo_root_path, institute, str(wmo), ("%i_prof.nc" % wmo))
        return self._load_nc(doifile, verbose)