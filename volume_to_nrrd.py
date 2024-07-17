import os
import zarr
import json
import nrrd
import shutil
import tifffile
import argparse
import requests
import numpy as np

from config import username, password
from requests.auth import HTTPBasicAuth

# PI
# python volume_to_nrrd.py --x 2432 --y 2304 --z 10624 --w 768 --h 768 --d 768 --chunk 768

# Title
# python volume_to_nrrd.py --x 2612 --y 1765 --z 5049 --w 2304 --h 1536 --d 768 --chunk 768
# python volume_to_nrrd.py --x 2612 --y 1765 --z 4281 --w 2304 --h 1536 --d 768 --chunk 768
# python volume_to_nrrd.py --x 2630 --y 1900 --z 3513 --w 2304 --h 768 --d 768 --chunk 768
# python volume_to_nrrd.py --x 2645 --y 1831 --z 2736 --w 2304 --h 768 --d 768 --chunk 768
# python volume_to_nrrd.py --x 2656 --y 1860 --z 1968 --w 2304 --h 768 --d 768 --chunk 768

volume_chunk = 256
cminZ, cminY, cminX = 2000, 2000, 2000
cmaxZ, cmaxY, cmaxX = 12240, 4560, 5072

output_folder = "./output_volume/"
volume_folder = "../full-scrolls/Scroll1/PHercParis4.volpkg/seg-volumetric-labels/cubes/"
url_template = 'https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/seg-volumetric-labels/cubes/'

def download(url, filename):
    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download image {filename}, status code: {response.status_code}")
        return False

# ro, wo: initial minimum position of rData & wData
def fit_data(wData, rData, wo, ro):
    rd, rh, rw = rData.shape
    wd, wh, ww = wData.shape

    r0, r1, r2 = ro[0], ro[1], ro[2]
    w0, w1, w2 = wo[0], wo[1], wo[2]

    zs, ys, xs = max(r0, w0), max(r1, w1), max(r2, w2)
    ze, ye, xe = min(r0 + rd, w0 + wd), min(r1 + rh, w1 + wh), min(r2 + rw, w2 + ww)

    wData[(zs-w0):(ze-w0), (ys-w1):(ye-w1), (xs-w2):(xe-w2)] = rData[(zs-r0):(ze-r0), (ys-r1):(ye-r1), (xs-r2):(xe-r2)]

def main(xmin, ymin, zmin, w, h, d, nrrd_chunk):
    if os.path.exists(output_folder): shutil.rmtree(output_folder)

    os.makedirs(volume_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # calculate & download necessary volume files
    xs = max(xmin, cminX)
    ys = max(ymin, cminY)
    zs = max(zmin, cminZ)

    xe = min(xmin + w, cmaxX + volume_chunk)
    ye = min(ymin + h, cmaxY + volume_chunk)
    ze = min(zmin + d, cmaxZ + volume_chunk)

    nxs = cminX + (xs - cminX) // volume_chunk * volume_chunk
    nys = cminY + (ys - cminY) // volume_chunk * volume_chunk
    nzs = cminZ + (zs - cminZ) // volume_chunk * volume_chunk

    volume_data = np.zeros((ze - zs, ye - ys, xe - xs), dtype=np.uint8)

    for iz in range(nzs, ze, volume_chunk):
        for iy in range(nys, ye, volume_chunk):
            for ix in range(nxs, xe, volume_chunk):

                target = f'{iz:05d}_{iy:05d}_{ix:05d}'
                url = os.path.join(url_template, target, f'{target}_volume.nrrd')
                folder = os.path.join(volume_folder, target)
                filename = os.path.join(folder, f'{target}_volume.nrrd')

                # Check if output image already exists, and if so, skip download and resize
                if os.path.exists(filename):
                    print(f"Data {os.path.basename(url)} exists. Skipping download.")
                else:
                    print(f"Download {os.path.basename(url)} ...")
                    os.makedirs(folder, exist_ok=True)
                    download(url, filename)

                # write volume data into a numpy array
                data, header = nrrd.read(filename)
                data = data.astype('uint8')
                fit_data(volume_data, data, (zs, ys, xs), (iz, iy, ix))
    print('')

    # save it as a series of tif & nrrd
    for z in range(zmin, zmin + d, nrrd_chunk):
        cube = np.zeros((nrrd_chunk, nrrd_chunk, nrrd_chunk), dtype=np.uint8)

        for y in range(ymin, ymin + h, nrrd_chunk):
            for x in range(xmin, xmin + w, nrrd_chunk):

                target = f"{z:05d}_{y:05d}_{x:05d}_d{nrrd_chunk}"
                print(f"Processing {target}_volume.nrrd ...")

                # volume (z, y, x)
                fit_data(cube, volume_data, (z, y, x), (zs, ys, xs))

                # tiff (z, y, x), nrrd (x, y, z)
                filename = os.path.join(output_folder, f'{target}_volume.tif')
                tifffile.imwrite(filename, cube.transpose(0, 1, 2))
                filename = os.path.join(output_folder, f'{target}_volume.nrrd')
                nrrd.write(filename, cube.transpose(2, 1, 0))

    # generate a mask template
    print(f"Processing mask_template_d{nrrd_chunk}.nrrd ...")
    filename = os.path.join(output_folder, f'mask_template_d{nrrd_chunk}.nrrd')
    mask = np.zeros((nrrd_chunk, nrrd_chunk, nrrd_chunk), dtype=np.uint8)
    nrrd.write(filename, mask)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download Ryan ink 3d and transform into a series of NRRD files.')
    parser.add_argument('--x', type=int, help='minimium x')
    parser.add_argument('--y', type=int, help='minimium y')
    parser.add_argument('--z', type=int, help='minimium z')
    parser.add_argument('--w', type=int, default=256, help='width')
    parser.add_argument('--h', type=int, default=256, help='height')
    parser.add_argument('--d', type=int, default=256, help='depth')
    parser.add_argument('--chunk', type=int, default=256, help='chunk size')
    args = parser.parse_args()

    xmin, ymin, zmin = args.x, args.y, args.z
    w, h, d, nrrd_chunk = args.w, args.h, args.d, args.chunk

    main(xmin, ymin, zmin, w, h, d, nrrd_chunk)
