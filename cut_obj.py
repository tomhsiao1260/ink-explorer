import os
import copy
import shutil
import argparse
import numpy as np
from loader import parse_obj, save_obj
from cut import re_index, cutLayer, cutBounding

# python cut_obj.py 20230702185753 --x 2630 --y 1900 --z 3513 --w 2304 --h 768 --d 768 --chunk 768

output_folder = "./obj_output/"

def main(segment, xmin, ymin, zmin, w, h, d, chunk):
    if os.path.exists(output_folder): shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    # calculate the boundary
    boxMin = np.array([xmin, ymin, zmin])
    boxMax = boxMin + np.array([w, h, d])

    # load obj
    obj_path = f'../full-scrolls/Scroll1.volpkg/paths/{segment}/{segment}.obj'
    data = parse_obj(obj_path)

    # cut a given .obj along z-axis
    cutLayer(data, layerMin = boxMin[2], layerMax = boxMax[2])
    re_index(data)
    # cut a given .obj along bounding box
    cutBounding(data, boxMin, boxMax)
    re_index(data)

    # cut & save it as a series of obj
    for x in range(boxMin[0], boxMax[0], chunk):
        for y in range(boxMin[1], boxMax[1], chunk):
            for z in range(boxMin[2], boxMax[2], chunk):

                print(f"Processing {segment}_{z}_{y}_{x}_d{chunk}.obj ...")

                chunk_boxMin = np.array([x, y, z])
                chunk_boxMax = chunk_boxMin + np.array([chunk, chunk, chunk])
                chunk_data = copy.copy(data)

                cutBounding(chunk_data, chunk_boxMin, chunk_boxMax)
                re_index(chunk_data)

                filename = os.path.join(output_folder, f'{segment}_{z}_{y}_{x}_d{chunk}.obj')
                save_obj(filename, chunk_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cut segment into multiple chunks')
    parser.add_argument('segment', type=str, help='segment id')
    parser.add_argument('--x', type=int, help='minimium x')
    parser.add_argument('--y', type=int, help='minimium y')
    parser.add_argument('--z', type=int, help='minimium z')
    parser.add_argument('--w', type=int, default=256, help='width')
    parser.add_argument('--h', type=int, default=256, help='height')
    parser.add_argument('--d', type=int, default=256, help='depth')
    parser.add_argument('--chunk', type=int, default=256, help='chunk size')
    args = parser.parse_args()

    segment = args.segment
    xmin, ymin, zmin = args.x, args.y, args.z
    w, h, d, chunk = args.w, args.h, args.d, args.chunk

    main(segment, xmin, ymin, zmin, w, h, d, chunk)
