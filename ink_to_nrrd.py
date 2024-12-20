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

# python ink_to_nrrd.py --x 2432 --y 2304 --z 10624 --w 768 --h 768 --d 768 --chunk 768

# Title

# python ink_to_nrrd.py --x 2860 --y 2853 --z 9657 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 2973 --y 2769 --z 8889 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3140 --y 2700 --z 8121 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3264 --y 2666 --z 7353 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3360 --y 2666 --z 6585 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3360 --y 2373 --z 5817 --w 768 --h 1536 --d 768 --chunk 768

# python ink_to_nrrd.py --x 3380 --y 1765 --z 5049 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3380 --y 1765 --z 4281 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3400 --y 1900 --z 3513 --w 768 --h 768 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3413 --y 1831 --z 2736 --w 768 --h 768 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3424 --y 1860 --z 1968 --w 768 --h 768 --d 768 --chunk 768

# python ink_to_nrrd.py --x 3490 --y 1537 --z 1200 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3574 --y 1693 --z 432 --w 768 --h 1536 --d 768 --chunk 768
# python ink_to_nrrd.py --x 3674 --y 1722 --z 0 --w 768 --h 1536 --d 768 --chunk 768

ny, nx, nz, zarr_chunk = 30, 31, 56, 256

zarr_folder = "../full-scrolls/community-uploads/ryan/3d_predictions_scroll1.zarr/"
url_template = 'https://dl.ash2txt.org/community-uploads/ryan/3d_predictions_scroll1.zarr/'

def download(url, filename):
    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download image {filename}, status code: {response.status_code}")
        return False

def process_ink(output_folder, xmin, ymin, zmin, w, h, d, nrrd_chunk):
    # if os.path.exists(output_folder): shutil.rmtree(output_folder)

    os.makedirs(zarr_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # download .zarray
    url = os.path.join(url_template, '.zarray')
    zarray_name = os.path.join(zarr_folder, '.zarray')
    if not os.path.exists(zarray_name): download(url, zarray_name)

    # calculate & download necessary zarr files
    xs = max(xmin, 0)
    ys = max(ymin, 0)
    zs = max(zmin, 0)

    xe = min(xmin + w, zarr_chunk * (nx + 1))
    ye = min(ymin + h, zarr_chunk * (ny + 1))
    ze = min(zmin + d, zarr_chunk * (nz + 1))

    nxs = xs // zarr_chunk
    nys = ys // zarr_chunk
    nzs = zs // zarr_chunk

    nxe = (xe - 1) // zarr_chunk
    nye = (ye - 1) // zarr_chunk
    nze = (ze - 1) // zarr_chunk

    for iy in range(nys, nye + 1, 1):
        for ix in range(nxs, nxe + 1, 1):
            for iz in range(nzs, nze + 1, 1):

                url = os.path.join(url_template, f'{iy}.{ix}.{iz}')
                filename = os.path.join(zarr_folder, os.path.basename(url))

                # Check if output image already exists, and if so, skip download and resize
                if os.path.exists(filename):
                    print(f"Data {os.path.basename(url)} exists. Skipping download.")
                else:
                    print(f"Download {os.path.basename(url)} ...")
                    download(url, filename)
    print('')

    # load zarr
    zarr_data = zarr.open(zarr_folder, mode="r")

    # save it as a series of tif & nrrd
    for z in range(zs, ze, nrrd_chunk):
        cube = np.zeros((nrrd_chunk, nrrd_chunk, nrrd_chunk), dtype=np.uint8)

        for y in range(ys, ye, nrrd_chunk):
            for x in range(xs, xe, nrrd_chunk):
                print(f"Processing {z:05d}_{y:05d}_{x:05d}_ink.nrrd ...")

                dy = min(ye - y, nrrd_chunk)
                dx = min(xe - x, nrrd_chunk)
                dz = min(ze - z, nrrd_chunk)

                # zarr (y, x, z)
                cube[ 0:dy, 0:dx, 0:dz ] = np.array(zarr_data[ y:y+dy, x:x+dx, z:z+dz ])

                # tiff (z, y, x), nrrd (z, y, x)
                filename = os.path.join(output_folder, f'{z:05d}_{y:05d}_{x:05d}_ink.tif')
                tifffile.imwrite(filename, cube.transpose(2, 0, 1))
                filename = os.path.join(output_folder, f'{z:05d}_{y:05d}_{x:05d}_ink.nrrd')
                nrrd.write(filename, cube.transpose(2, 0, 1))
                # nrrd.write(filename, cube.transpose(1, 0, 2))

    # generate a mask template
    print(f"Processing mask_template.nrrd ...")
    filename = os.path.join(output_folder, 'mask_template.nrrd')
    mask = np.zeros((nrrd_chunk, nrrd_chunk, nrrd_chunk), dtype=np.uint8)
    nrrd.write(filename, mask)

if __name__ == "__main__":
    output_folder = "./output_ink/"

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

    process_ink(output_folder, xmin, ymin, zmin, w, h, d, nrrd_chunk)




