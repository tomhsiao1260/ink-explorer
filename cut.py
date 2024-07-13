import copy
import numpy as np

def re_index(data):
    if (data['faces'].shape[0] == 0): return

    data['faces'] -= 1
    selected_vertices = np.unique(data['faces'][:,:,0])

    # only leave the vertices used to form the faces
    data['vertices'] = data['vertices'][selected_vertices]
    data['normals']  = data['normals'][selected_vertices]
    data['uvs']      = data['uvs'][selected_vertices]
    data['colors']   = data['colors'][selected_vertices]

    # update face index
    vertex_mapping = { old_index: new_index for new_index, old_index in enumerate(selected_vertices) }
    data['faces'] = np.vectorize(lambda x: vertex_mapping.get(x, x))(data['faces'])
    data['faces'] += 1
    
def cut_obj(data, splitAxis, splitOffset, survive, align = True):
    triVertices = data['vertices'][data['faces'][:,:,0] - 1]

    # number of vertices of each triangle located in the lower side (0~3)
    tri_lower_bool = triVertices[:, :, splitAxis] < splitOffset
    tri_lower_num = np.sum(tri_lower_bool, axis=1)

    # straighten the cutting edge (tweak the edge vertices position)
    if (align):
        f = data['faces'][tri_lower_num == 1]
        v = data['vertices'][f[:,:,0] - 1]
        mask = v[:, :, splitAxis] < splitOffset
        i = np.unique(f[:, :, 0][mask] - 1)
        data['vertices'][i, splitAxis] = splitOffset

        f = data['faces'][tri_lower_num == 2]
        v = data['vertices'][f[:,:,0] - 1]
        mask = v[:, :, splitAxis] > splitOffset
        i = np.unique(f[:, :, 0][mask] - 1)
        data['vertices'][i, splitAxis] = splitOffset

    # choose the side we need
    if (survive == 'left'):  data['faces'] = data['faces'][tri_lower_num >= 2]
    if (survive == 'right'): data['faces'] = data['faces'][tri_lower_num < 2]

    # return both
    if (survive == 'both'):
        left = copy.deepcopy(data)
        right = copy.deepcopy(data)
        left['faces'] = data['faces'][tri_lower_num >= 2]
        right['faces'] = data['faces'][tri_lower_num < 2]
        return left, right

    return data

# cut a given obj along z-axis
def cutLayer(data, layerMin, layerMax, align = True):
    # cut z
    cut_obj(data, splitAxis = 2, splitOffset = layerMin, survive = 'right', align = align)
    cut_obj(data, splitAxis = 2, splitOffset = layerMax, survive = 'left', align = align)

    re_index(data)
    return data

# cut a given obj into two along z-axis
def cutDivide(data, cutZ, align = True):
    left, right = cut_obj(data, splitAxis = 2, splitOffset = cutZ, survive = 'both', align = align)

    re_index(left)
    re_index(right)
    return left, right 

# cut a given obj via a bounding box
def cutBounding(data, boxMin, boxMax, align = True):
    # cut x
    d_max = 10
    cut_obj(data, splitAxis = 0, splitOffset = boxMin[0], survive = 'right', align = align)
    cut_obj(data, splitAxis = 0, splitOffset = boxMax[0], survive = 'left', align = align)
    # cut y
    cut_obj(data, splitAxis = 1, splitOffset = boxMin[1], survive = 'right', align = align)
    cut_obj(data, splitAxis = 1, splitOffset = boxMax[1], survive = 'left', align = align)
    # cut z
    cut_obj(data, splitAxis = 2, splitOffset = boxMin[2], survive = 'right', align = align)
    cut_obj(data, splitAxis = 2, splitOffset = boxMax[2], survive = 'left', align = align)

    re_index(data)
    return data