import os
import requests
import tifffile
import numpy as np
from requests.auth import HTTPBasicAuth

y, x, z = 5, 8, 8

username = ""
password = ""

output_folder = "cell"
output_stack_folder = "cell_stack"
url_template = 'https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/volume_grids/20230205180739/cell_yxz_{:03}_{:03}_{:03}.tif'

def create_stack():
    shX = 3072
    shY = 1792
    shZ = 2304

    w = 1536
    h = 1536

    xs = (x - 1) * 500 - shX
    ys = (y - 1) * 500 - shY
    zs = (z - 1) * 500 - shZ

    xe = xs + 500
    ye = ys + 500
    ze = zs + 500

    os.makedirs(output_stack_folder, exist_ok=True)

    url = url_template.format(y, x, z)
    filename = os.path.join(output_folder, os.path.basename(url))
    data = tifffile.imread(filename).astype('float') / 256
    data = data.astype('uint8')

    for l in range(zs, ze, 1):
        img = np.zeros((h, w), dtype=np.uint8)
        img[ys:ye, xs:xe] = data[(l-zs), :500, :500]

        filename = os.path.join(output_stack_folder, f'{l:04d}.tif')
        tifffile.imwrite(filename, img)

def download_image(url, filename):
    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download image {filename}, status code: {response.status_code}")
        return False

def main():
    url = url_template.format(y, x, z)
    filename = os.path.join(output_folder, os.path.basename(url))

    if not os.path.exists(output_folder): os.makedirs(output_folder)
    if os.path.exists(filename):
        print(f"Output image {filename} already exists. Skipping download.")
    else:
        download_image(url, filename)

    create_stack()

if __name__ == "__main__":
    main()
