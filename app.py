import json
import argparse

from cut_obj import process_obj
from ink_to_nrrd import process_ink
from volume_to_nrrd import process_volume

# PI

# python app.py --segment 20230702185753 --x 2432 --y 2304 --z 10624 --w 768 --h 768 --d 768 --chunk 768

# Title

# python app.py --segment 20230702185753 --x 2860 --y 2853 --z 9657 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 2973 --y 2769 --z 8889 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3140 --y 2700 --z 8121 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3264 --y 2666 --z 7353 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3360 --y 2666 --z 6585 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3360 --y 2373 --z 5817 --w 768 --h 1536 --d 768 --chunk 768

# python app.py --segment 20230702185753 --x 3380 --y 1765 --z 5049 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3380 --y 1765 --z 4281 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3400 --y 1900 --z 3513 --w 768 --h 768 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3413 --y 1831 --z 2736 --w 768 --h 768 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3424 --y 1860 --z 1968 --w 768 --h 768 --d 768 --chunk 768

# python app.py --segment 20230702185753 --x 3490 --y 1537 --z 1200 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3574 --y 1693 --z 432 --w 768 --h 1536 --d 768 --chunk 768
# python app.py --segment 20230702185753 --x 3674 --y 1722 --z 0 --w 768 --h 1536 --d 768 --chunk 768

def main(output_folder, segment, xmin, ymin, zmin, w, h, d, chunk):
    info = {}
    info['mask'] = f'mask_template.nrrd'
    info['volume'] = [f'{zmin:05d}_{ymin:05d}_{xmin:05d}_ink.nrrd']
    info['segments'] = []
    info['z'] = zmin
    info['y'] = ymin
    info['x'] = xmin
    info['size'] = chunk

    if (segment):
        process_obj(output_folder, segment, xmin, ymin, zmin, w, h, d, chunk)
        info['segments'].append(f'{zmin:05d}_{ymin:05d}_{xmin:05d}_{segment}.obj')

    if (zmin + chunk > 2000):
        process_volume(output_folder, xmin, ymin, zmin, w, h, d, chunk)
        info['volume'].append(f'{zmin:05d}_{ymin:05d}_{xmin:05d}_volume.nrrd')

    process_ink(output_folder, xmin, ymin, zmin, w, h, d, chunk)

    meta = {}
    meta['chunks'] = []
    meta['chunks'].append(info)

    with open(f"./{output_folder}/meta.json", "w") as outfile:
        json.dump(meta, outfile, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--segment', type=str, help='segment id')
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

    for z in range(zmin, zmin + d, chunk):
        for y in range(ymin, ymin + h, chunk):
            for x in range(xmin, xmin + w, chunk):

                w, h, d = chunk, chunk, chunk
                output_folder = f"./cubes/{z:05}_{y:05}_{x:05}/"

                main(output_folder, segment, x, y, z, w, h, d, chunk)
