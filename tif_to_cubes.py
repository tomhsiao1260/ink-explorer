import os
import re
import nrrd
import shutil
import tifffile
import numpy as np
from pathlib import Path

input_folder = 'pi_stack'
output_folder = 'pi_cubes'

# # title
# tif_startZ, tif_startY, tif_startX = 2304, 1792, 3072

# pi
tif_startZ, tif_startY, tif_startX = 10496, 2304, 2304

cube_startZ, cube_startY, cube_startX = 2000, 2000, 2000

chunk = 256

def tif_to_cubes():
    tiffdir = Path(input_folder)
    cubedir = Path(output_folder)

    # load tiff files
    tiffs = tiffdir.glob("*.tif")
    rec = re.compile(r'([0-9]+)\.\w+$')

    inttiffs = {}
    for tiff in tiffs:
        tname = tiff.name
        match = rec.match(tname)
        if match is None: continue

        ds = match.group(1)
        itiff = int(ds)
        if itiff in inttiffs:
            err = "File %s: tiff id %d already used"%(tname,itiff)
            print(err)
            return err
        inttiffs[itiff] = tiff

    if len(inttiffs) == 0:
        err = "No tiffs found"
        print(err)
        return err

    itiffs = list(inttiffs.keys())
    itiffs.sort()

    minz = itiffs[0]
    maxz = itiffs[-1]

    # calculate the boundary
    tiff0 = tifffile.imread(inttiffs[minz])
    ny0, nx0 = tiff0.shape

    tif_endZ = tif_startZ + len(itiffs)
    tif_endY = tif_startY + ny0
    tif_endX = tif_startX + nx0

    startZ = (tif_startZ - cube_startZ) // chunk * chunk + cube_startZ
    startY = (tif_startY - cube_startY) // chunk * chunk + cube_startY
    startX = (tif_startX - cube_startX) // chunk * chunk + cube_startX

    endZ = (tif_endZ - cube_startZ) // chunk * chunk + cube_startZ
    endY = (tif_endY - cube_startY) // chunk * chunk + cube_startY
    endX = (tif_endX - cube_startX) // chunk * chunk + cube_startX

    # write into cubes
    if cubedir.exists(): shutil.rmtree(cubedir)
    os.makedirs(cubedir, exist_ok=True)

    for z in range(startZ, endZ + chunk, chunk):
        # cube data init (z, y, x)
        data = np.zeros((chunk, (endY - startY + chunk), (endX - startX + chunk)), dtype=np.uint8)

        # wrtie data
        for layer in range(chunk):
            zLayer = z + layer
            if (zLayer < tif_startZ or zLayer >= tif_endZ): continue

            sy, sx = tif_startY - startY, tif_startX - startX
            tif = tifffile.imread(inttiffs[ zLayer - tif_startZ ])
            data[ layer, sy:sy+ny0, sx:sx+nx0 ] = tif

        # save it (x, y, z)
        for y in range(startY, endY + chunk, chunk):
            for x in range(startX, endX + chunk, chunk):

                z0, y0, x0 = 0, y - startY, x - startX
                cube = data[ z0:z0+chunk, y0:y0+chunk, x0:x0+chunk ]

                # filename = str(cubedir / f'ink_{z}_{y}_{x}.tif')
                # tifffile.imwrite(filename, cube)
                filename = str(cubedir / f'ink_{z}_{y}_{x}.nrrd')
                nrrd.write(filename, cube.transpose(2, 1, 0))

def main():
    tif_to_cubes()

if __name__ == "__main__":
    main()
