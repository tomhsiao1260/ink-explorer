import json
import argparse

from cut_obj import process_obj
from ink_to_nrrd import process_ink
from volume_to_nrrd import process_volume

# python app.py --segment 20230702185753 --x 2630 --y 1900 --z 3513 --w 2304 --h 768 --d 768 --chunk 768

def main(output_folder, segment, xmin, ymin, zmin, w, h, d, chunk):
    info = {}
    info['mask'] = f'mask_template_d768.nrrd'
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
                output_folder = f"./cubes/{x}_{y}_{z}/"

                main(output_folder, segment, x, y, z, w, h, d, chunk)
