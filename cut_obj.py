import argparse
import numpy as np
from loader import parse_obj, save_obj
from cut import cutLayer, cutBounding

# python cut_obj.py 20230702185753 --min 3072 1792 3500 --size 768 768 768
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate volume via boudning box')
    parser.add_argument('segment', type=str, help='segment id')
    parser.add_argument('--min', nargs=3, type=int, metavar=('X', 'Y', 'Z'), help='bounding box minimum (x, y, z)')
    parser.add_argument('--size', nargs=3, type=int, metavar=('X', 'Y', 'Z'), help='bounding box size (w, h, d)')
    args = parser.parse_args()

    segment = args.segment
    boxSize = np.array(args.size)
    boxMin = np.array(args.min)
    boxMax = boxMin + boxSize

    # load .obj
    obj_path = f'../full-scrolls/Scroll1.volpkg/paths/{segment}/{segment}.obj'
    data = parse_obj(obj_path)
    # cut a given .obj along z-axis
    cutLayer(data, layerMin = boxMin[2], layerMax = boxMax[2])
    # cut a given .obj along bounding box
    cutBounding(data, boxMin, boxMax)

    # save obj (z, y, x)
    filename = f'{segment}_{boxMin[2]}_{boxMin[1]}_{boxMin[0]}.obj'
    save_obj(filename, data)