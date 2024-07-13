import argparse
import numpy as np
from loader import parse_obj, save_obj
from cut import cutLayer, cutBounding

# python cut_obj.py 20230702185753 --x 2630 --y 1900 --z 3513 --w 2304 --h 768 --d 768 --chunk 768

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
    w, h, d, nrrd_chunk = args.w, args.h, args.d, args.chunk

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
