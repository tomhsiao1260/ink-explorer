# visualize the uv for a given cube & segment in that cube

import os
import cv2
import numpy as np
from loader import parse_obj, save_obj

if __name__ == "__main__":
    # zmin, ymin, xmin = 1200, 1537, 3490
    # zmin, ymin, xmin = 1200, 1800, 2990
    # zmin, ymin, xmin = 1200, 2305, 3490
    # zmin, ymin, xmin = 1968, 1860, 3424
    # zmin, ymin, xmin = 2736, 1831, 3413
    # zmin, ymin, xmin = 3513, 1900, 3400
    # zmin, ymin, xmin = 4281, 1765, 3380
    # zmin, ymin, xmin = 4281, 2533, 3380
    # zmin, ymin, xmin = 5049, 1765, 3380
    zmin, ymin, xmin = 5049, 2533, 3380

    output_dir = 'output_mask'
    inklabels_dir = '/Users/yao/Desktop/print/185753-ink.png'
    obj_dir = f'/Users/yao/Desktop/full-scrolls/community-uploads/yao/scroll1/{zmin:05}_{ymin:05}_{xmin:05}/{zmin:05}_{ymin:05}_{xmin:05}_20230702185753.obj'

    data = parse_obj(obj_dir)
    image = cv2.imread(inklabels_dir, cv2.IMREAD_GRAYSCALE)
    h, w = image.shape

    faces = data['faces'][:][:, :, 0] - 1
    uvs = data['uvs'][faces]

    uvs[:, :, 1] = 1 - uvs[:, :, 1] 
    uvs = (uvs * [w, h]).astype(np.int32)

    mask = np.zeros((h, w), dtype=np.uint8)

    for triangle in uvs:
        cv2.fillPoly(mask, [triangle], color=255)

    output = np.where(mask == 255, image, (image * 0.2).astype(np.uint8))

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{zmin:05}_{ymin:05}_{xmin:05}.png")
    cv2.imwrite(output_path, output)
