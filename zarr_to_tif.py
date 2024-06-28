import os
import sys
import zarr
import argparse
import numpy as np
import tifffile
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "output_zarr_ome_dir", 
            help="Name of directory that will contain OME/zarr datastore")
    parser.add_argument(
            "output_stack", 
            help="Name of directory that will contain output stack")

    args = parser.parse_args()

    zarrdir = Path(args.output_zarr_ome_dir)
    if zarrdir.suffix != ".zarr":
        print("Name of ouput zarr directory must end with '.zarr'")
        return 1

    zdir = args.output_zarr_ome_dir

    # data = zarr.open('../scroll2zarr-learn-forward/scroll.zarr/0/', mode="r")
    data = zarr.open(f'{zdir}/0/', mode="r")
    data = np.array(data)

    output = args.output_stack
    if os.path.exists(output): shutil.rmtree(output)

    os.makedirs(output, exist_ok=True)

    print(data.shape)
    print(np.min(data))
    print(np.max(data))

    for i in range(data.shape[0]):
        filename = os.path.join(output, f'{i:03d}.tif')
        tifffile.imwrite(filename, data[i])

if __name__ == '__main__':
    sys.exit(main())
