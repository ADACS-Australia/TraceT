from astropy.table import QTable
from astropy import units as u
import astropy_healpix as ah
from astropy.coordinates import SkyCoord, EarthLocation
import numpy as np
from astropy.time import Time
from yaml import load, Loader, dump

MWA_LAT = '-26:42:11.95'
MWA_LONG = '116:40:14.93'
MWA_HEIGHT = 377.8
MWA_SPOTS = 'trigger_app/MWA_SPOTS.txt'
MWA_SPOTS_YAML = 'trigger_app/MWA_SPOTS.yaml'

def getMWAPointingsFromSkymapFile(skymap):
    MWA = EarthLocation(lat=MWA_LAT,
                lon=MWA_LONG, height=MWA_HEIGHT * u.m)
    with open(MWA_SPOTS, 'r') as file:
        lines = file.readlines()

        # Step 2: Extract the relevant data
        # with open(MWA_SPOTS_YAML, 'r') as stream:
        #     data = load(stream, Loader=Loader)

        data = []
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if line.startswith(('---', 'N')) or not line:  # Skip header and empty lines
                continue
            values = line.split('|')
            n = int(values[0].strip())
            az = float(values[1].strip())
            el = float(values[2].strip())
            data.append((n, az, el))
        #     with open(MWA_SPOTS_YAML, 'w') as stream:
        #         dump(data, stream)

    results = []
    for entry in data:
        (n, az, alt) = entry
        mwa_coord = SkyCoord(az, alt, unit=(
            u.deg, u.deg), frame='altaz', obstime=Time.now(), location=MWA)
        ra_dec = mwa_coord.icrs
        ra = ra_dec.ra.deg * u.deg
        dec = ra_dec.dec.deg * u.deg
        level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
        nside = ah.level_to_nside(level)
        match_ipix = ah.lonlat_to_healpix(ra, dec, nside, order='nested')


        i = np.flatnonzero(ipix == match_ipix)[0]
        
        res = float(skymap[i]['PROBDENSITY'] * (np.pi / 180)**2)
        results.append((n, az, alt, ra, dec, i, res))
    return sorted(results, key=lambda x: -x[5])[:4]