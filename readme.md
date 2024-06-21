# How to run

Install packages.

```
pip install -r requirements.txt
```

Enter `USERNAME` and `PASSWORD` and then Download the data.

```bash
sh download.sh
```

Transform axis & generate OME/Zarr data.

```python
python transform_xyz.py <YOUR_ZARR_NAME>.zarr
```

Transform Zarr to Tiff.

```python
python zarr_to_tif.py <YOUR_ZARR_NAME>.zarr
```