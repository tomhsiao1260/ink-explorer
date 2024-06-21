#!/bin/sh

FOLDER="pi.zarr"
USERNAME=""
PASSWORD=""

# title
XMIN=3085
XMAX=4473

YMIN=1926
YMAX=3295

# 1:20 ~ 3:00
ZMIN=2395
ZMAX=5403

# # pi
# XMIN=2471
# XMAX=3103

# YMIN=2549
# YMAX=2965

# ZMIN=10585
# ZMAX=11200

################################################
#############        .zarray       #############
################################################
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
    echo "folder $FOLDER deleted"
fi

rclone copy :http:/community-uploads/ryan/3d_predictions_scroll1.zarr/.zarray ./ --http-url https://$USERNAME:$PASSWORD@dl.ash2txt.org/

# receive params
read CHUNK <<< "$(jq -r '.chunks | "\(.[0])"' ".zarray")"
echo "Chunk Size: $CHUNK"

# calculate indices
xs=$(expr $XMIN / $CHUNK)
xe=$(expr $XMAX / $CHUNK)

ys=$(expr $YMIN / $CHUNK)
ye=$(expr $YMAX / $CHUNK)

zs=$(expr $ZMIN / $CHUNK)
ze=$(expr $ZMAX / $CHUNK)

echo "Indices X: $xs to $xe"
echo "Indices Y: $ys to $ye"
echo "Indices Z: $zs to $ze"

W=$(((xe - xs + 1) * CHUNK))
H=$(((ye - ys + 1) * CHUNK))
D=$(((ze - zs + 1) * CHUNK))

echo "Shape (w, h, d): $W, $H, $D"

# change shape & add dimension_separator attribute
jq --argjson H $H --argjson W $W --argjson D $D '
    .shape = [$H, $W, $D] |
    . + {"dimension_separator": "/"}
    ' ".zarray" > temp.zarray

mkdir -p "$FOLDER/0"
mv temp.zarray "$FOLDER/0/.zarray" && rm ".zarray"

# ################################################
# #############      chunk data      #############
# ################################################
for ((y = ys; y <= ye; y++)); do
    for ((x = xs; x <= xe; x++)); do
        mkdir -p "$FOLDER/0/$((y-ys))/$((x-xs))"

        for ((z = zs; z <= ze; z++)); do
            FILE="$y.$x.$z"
            rclone copy :http:/community-uploads/ryan/3d_predictions_scroll1.zarr/$FILE ./ --http-url https://$USERNAME:$PASSWORD@dl.ash2txt.org/ --progress --multi-thread-streams=8 --transfers=8

            mv $FILE "$FOLDER/0/$((y-ys))/$((x-xs))/$((z-zs))"
        done
    done
done
