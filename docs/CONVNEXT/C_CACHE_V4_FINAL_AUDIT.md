# C-CACHE-V4 Final Audit — 2026-10-18

Status: **CACHE_COMPLETE / 5PACK_PASS / TRAIN_READY**

## Dataset paths

- P00: `/kaggle/input/datasets/woniyeon/c-geom-mv320-cache-pack-00/C_GEOM_MV320_CACHE_PACK_00/c_geom_mv320_pack00.h5`
- P01: `/kaggle/input/datasets/woniyeon/c-geom-mv320-cache-pack-01/C_GEOM_MV320_CACHE_PACK_01/c_geom_mv320_pack01.h5`
- P02: `/kaggle/input/datasets/woniyeon/c-geom-mv320-cache-pack-02/C_GEOM_MV320_CACHE_PACK_02/c_geom_mv320_pack02.h5`
- P03: `/kaggle/input/datasets/yhlucas/c-geom-mv320-cache-pack-03/C_GEOM_MV320_CACHE_PACK_03/c_geom_mv320_pack03.h5`
- P04: `/kaggle/input/datasets/yhlucas/c-geom-mv320-cache-pack-04/C_GEOM_MV320_CACHE_PACK_04/c_geom_mv320_pack04.h5`

## Pack audit

| Pack | Studies | HDF5 GiB | Runtime min | HDF5 SHA256 |
|---|---:|---:|---:|---|
| P00 | 882 | 16.156 | 32.97 | `c8e18d2a417e3f77f5dbd97aa9d9db0d8b8b2647cee3fef6958accbb577047b0` |
| P01 | 882 | 16.156 | 30.37 | `bec05bf22268f55610fb62d6ed87fdf7d0e70e7975c832b72595c5ad96f4b8bf` |
| P02 | 881 | 16.137 | 29.46 | `1d320715bc0d4bb8f28c61689a1937ecd2a308b2ad33479e930428517de08c44` |
| P03 | 881 | 16.137 | 22.36 | `1fe92037909668e4bab528d251ec9f44ab4e2255653b0ec3da049260cdf5f4a8` |
| P04 | 881 | 16.137 | 34.68 | `b53b1ee5be77878b3dbedbbac649f76d487df8d04ccfd864577a114f0c3bd2bc` |

Total HDF5 size: **80.723 GiB**.

## Global cross-pack integrity

- Studies: **4,407 / 4,407**
- Unique StudyInstanceUID: **4,407**
- Cross-pack Study overlap: **0**
- Study missing: **0**
- Total valid windows: **282,048 = 4,407 × 64**
- Every Study valid windows: **64/64**
- Invalid windows: **0**
- Decode failures: **0**
- Prep skips: **0**
- HDF5 full readback verification: **PASS all 5 Packs**
- All emitted window rows use `IOP_IPP` physical ordering.
- Global windows: **141,024**
- Local windows: **141,024**

View counts:
- GLOBAL 141,024
- ANTERIOR 35,630
- CENTER 35,123
- POSTERIOR 33,984
- BILAT_L 18,641
- BILAT_R 17,646

Plane counts:
- Sagittal 121,528
- Coronal 84,938
- Axial 75,582

## Crop coverage audit

Across 282,048 valid windows:
- mean coverage: **0.999110**
- p05: **0.998037**
- minimum: **0.408753**
- coverage <0.90: **493 windows (0.175%)**, 86 Studies / 89 Series
- coverage <0.80: **397 windows (0.141%)**, 70 Studies / 73 Series

Important interpretation:
- all 493 windows below 0.90 are **Axial local** views only:
  - ANTERIOR 165
  - CENTER 164
  - POSTERIOR 164
- Sagittal and Coronal local views have no <0.90 cases; their minimum coverage is about 0.994.
- This matches the frozen contract: when source FOV itself is smaller than requested 110 mm, use the available physical extent and record coverage rather than inventing padded anatomy.
- Therefore these rare low-coverage rows are **not a cache-build failure** and do not justify rebuilding the cache.

## Frozen cache contract

- segmentation-free
- competition DICOM only for generation
- dense `[N,64,3,320,320] uint8`
- Global≈32 / Local≈32
- local 110 mm with ±30 mm physical offsets
- shift-to-fit when requested local center would leave source FOV
- source FOV <110 mm → available extent
- thin stack: spacing <1.75 mm → approx 3.5 mm slab
- no compression
- 8-channel window metadata
- label-independent cache

## Decision

**C-CACHE-V4 is accepted as final Branch-C training cache. Do not regenerate.**

Immediate next:
1. Freeze exact ConvNeXt-Small timm model/checkpoint path and SHA.
2. Build C-BASE 2-Fold training notebook against these five HDF5 inputs.
3. V4 Routed Broad + frozen Gold58 29/29 split.
4. Target-specific spatial attention → target-specific Window MIL.
5. Run actual T4×2 resource/runtime probe before full training.
