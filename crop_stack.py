import os
import tifffile
import numpy as np

ymin, xmin, zmin = 5, 7, 8
ymax, xmax, zmax = 5, 9, 9

input_folder = "stack"
output_folder = "crop_stack"

def create_stack():
    shX = 3072
    shY = 1792
    shZ = 2304

    w = 1536
    h = 1536
    d = 3328

    xs = max((xmin - 1) * 500 - shX, 0)
    ys = max((ymin - 1) * 500 - shY, 0)
    zs = max((zmin - 1) * 500 - shZ, 0)

    xe = min(xmax * 500 - shX, w)
    ye = min(ymax * 500 - shY, h)
    ze = min(zmax * 500 - shZ, d)

    # 0, 1427
    print('x: ', xs, xe - 1)
    # 208, 707
    print('y: ', ys, ye - 1)
    # 1196, 2195
    print('z: ', zs, ze - 1)

    os.makedirs(output_folder, exist_ok=True)

    for l in range(zs, ze, 1):
        filename = os.path.join(input_folder, f'{l:04d}.tif')
        data = tifffile.imread(filename)
        img = np.zeros((h, w), dtype=np.uint8)
        img[ys:ye, xs:xe] = data[ys:ye, xs:xe]

        filename = os.path.join(output_folder, f'{l:04d}.tif')
        tifffile.imwrite(filename, img)

if __name__ == "__main__":
    create_stack()
