import os
import nrrd
import tifffile
import numpy as np

input_folder = 'pi_stack'
output_folder = 'pi_nrrd'
filename = 'pi.nrrd'

def create_nrrd():
    d = 768
    h = 768
    w = 768

    os.makedirs(output_folder, exist_ok=True)

    # z, y, x
    data_nrrd = np.zeros((d, h, w), dtype=np.uint8)

    for i in range(d):
        data = tifffile.imread(os.path.join(input_folder, f'{i:03d}.tif'))
        data_nrrd[i, :, :] = data[:h, 99:99+w]
        # data_nrrd[i, :, :] = data[:h, :w]

    # x, y, z
    nrrd.write(os.path.join(output_folder, filename), data_nrrd.transpose(2, 1, 0))

def main():
    create_nrrd()

if __name__ == "__main__":
    main()

