# (C) British Crown Copyright 2011 - 2016, Met Office
#
# This file is part of cartopy.
#
# cartopy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cartopy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cartopy.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

import itertools
import os

import numpy as np

import cartopy.crs as ccrs


SPECIAL_CASES = {
    ccrs.PlateCarree: [{}, {'central_longitude': 180}],
    ccrs.RotatedPole: [{'pole_longitude': 177.5, 'pole_latitude': 37.5}],
    ccrs.UTM: [{'zone': 30}],
    ccrs.AzimuthalEquidistant: [{'central_latitude': 90}],
}


COASTLINE_RESOLUTION = {ccrs.OSNI: '10m',
                        ccrs.OSGB: '50m',
                        ccrs.EuroPP: '50m'}

PRJ_SORT_ORDER = {'PlateCarree': 1,
                  'Mercator': 2, 'Mollweide': 2, 'Robinson': 2,
                  'TransverseMercator': 2, 'LambertCylindrical': 2,
                  'LambertConformal': 2, 'Stereographic': 2, 'Miller': 2,
                  'Orthographic': 2, 'UTM': 2, 'AlbersEqualArea': 2,
                  'AzimuthalEquidistant': 2, 'Sinusoidal': 2,
                  'InterruptedGoodeHomolosine': 3, 'RotatedPole': 3,
                  'OSGB': 4}


def find_projections():
    for obj_name, o in vars(ccrs).copy().items():
        if isinstance(o, type) and issubclass(o, ccrs.Projection) and \
           not obj_name.startswith('_') and obj_name not in ['Projection']:

            yield o


if __name__ == '__main__':
    fname = os.path.join(os.path.dirname(__file__), 'source',
                         'crs', 'projections.rst')
    table = open(fname, 'w')

    table.write('.. _cartopy_projections:\n\n')
    table.write('Cartopy projection list\n')
    table.write('=======================\n\n\n')

    prj_class_sorter = lambda cls: (PRJ_SORT_ORDER.get(cls.__name__, 100),
                                    cls.__name__)
    for prj in sorted(find_projections(), key=prj_class_sorter):
        name = prj.__name__

        table.write(name + '\n')
        table.write('-' * len(name) + '\n\n')

        table.write('.. autoclass:: cartopy.crs.%s\n' % name)

        for instance_args in SPECIAL_CASES.get(prj, [{}]):
            prj_inst = prj(**instance_args)
            aspect = (np.diff(prj_inst.x_limits) /
                      np.diff(prj_inst.y_limits))[0]
            width = 3 * aspect
            if width == int(width):
                width = int(width)

            instance_params = ', '.join('{}={}'.format(k, v)
                                        for k, v in instance_args.items())
            instance_creation_code = '{}({})'.format(name, instance_params)
            code = """
.. plot::

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    plt.figure(figsize=({width}, 3))
    ax = plt.axes(projection=ccrs.{proj_constructor})
    ax.coastlines(resolution={coastline_resolution!r})
    ax.gridlines()

\n""".format(width=width, proj_constructor=instance_creation_code,
             coastline_resolution=COASTLINE_RESOLUTION.get(prj, '110m'))

            table.write(code)
