import numpy as np
from loader import parse_obj, save_obj
from cut import re_index, cut_obj

path_last_full = './obj_path/20230702185753_cut.obj'

path_bot = './obj_path/20230510153006_cut.obj'
path_mid = './obj_path/20240102231959.obj'
path_top = './obj_path/20231016151002_cut.obj'

obj_bot = parse_obj(path_bot)
obj_mid = parse_obj(path_mid)
obj_top = parse_obj(path_top)

# _
bot_min = np.min(obj_bot['vertices'], axis=0)
# 2396
bot_max = np.max(obj_bot['vertices'], axis=0)

# 3504
mid_min = np.min(obj_mid['vertices'], axis=0)
# 4295
mid_max = np.max(obj_mid['vertices'], axis=0)

# 5403
top_min = np.min(obj_top['vertices'], axis=0)
# _
top_max = np.max(obj_top['vertices'], axis=0)

print(bot_min)
print(bot_max)

print(mid_min)
print(mid_max)

print(top_min)
print(top_max)

data = parse_obj('./obj_path/20230702185753.obj')
cut_obj(data, splitAxis=2, splitOffset=5049, survive='right', align=True)
re_index(data)
cut_obj(data, splitAxis=2, splitOffset=(5049+768), survive='left', align=True)
re_index(data)
# save_obj(path_last_full, data)

print(np.min(data['vertices'], axis=0))
print(np.max(data['vertices'], axis=0))

# # 2920 1849 2396
# # 2920 1916 3503
# full_min = np.min(data['vertices'], axis=0)
# # 4644 3311 5404
# # 4612 2642 4296
# full_max = np.max(data['vertices'], axis=0)

# print(full_min)
# print(full_max)



