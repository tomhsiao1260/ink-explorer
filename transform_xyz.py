import sys
import zarr
import argparse
import numpy as np
from pathlib import Path
from scroll_to_ome import resize

def transform(zdir):
    data = zarr.open(f'{zdir}/0/', mode="r")

    # y, x, z
    print('zarr shape: ', data.shape)

    # z, y, x
    dat = np.array(data).transpose(2, 0, 1)

    shape = (data.shape[2], data.shape[0], data.shape[1])
    chunks = (data.chunks[2], data.chunks[0], data.chunks[1])
    dtype = data.dtype

    store = zarr.NestedDirectoryStore(f'{zdir}/0/')

    tzarr = zarr.open(
        store=store, 
        shape=shape, 
        chunks=chunks,
        dtype = dtype,
        write_empty_chunks=False,
        fill_value=0,
        compressor=None,
        # compressor=data.compressor,
        mode='w',
        )

    tzarr[:, :, :] = dat

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "output_zarr_ome_dir", 
            help="Name of directory that will contain OME/zarr datastore")

    zarrdir = Path(args.output_zarr_ome_dir)
    if zarrdir.suffix != ".zarr":
        print("Name of ouput zarr directory must end with '.zarr'")
        return 1

    zdir = args.output_zarr_ome_dir
    transform(zdir)

    nlevels = 6
    existing_level = 0
    algorithm = 'mean'

    for l in range(existing_level, nlevels-1):
        err = resize(zarrdir, l, algorithm)

if __name__ == '__main__':
    sys.exit(main())
