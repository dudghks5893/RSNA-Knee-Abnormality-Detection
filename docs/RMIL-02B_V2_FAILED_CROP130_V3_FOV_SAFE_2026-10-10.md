# RMIL-02B — V2 Crop130 Failure / V3 FOV-Safe CPU Cache Handoff (2026-10-10)

**Verified status:** V2 **FAILED**, not cached/released. V3 replacement CPU Notebook **PREPARED, NOT YET EXECUTED ON KAGGLE**. NO new GPU experiment, AUROC, K4 parity, or complete native pixel cache is claimed.

## What actually happened

- User shared Kaggle pasted log `붙여넣은 텍스트(1)(20261010-023738).txt` from Notebook `RMIL-02B_Native224_SharedCache_CPU.ipynb` (V2).
- Required two Kaggle Inputs detected successfully: original RSNA Knee competition + frozen `R2D_SHARED224_V1` Study/Series manifest Dataset; Python 3.12.13, pydicom 3.0.2, OpenCV 4.13.0, h5py 3.16.0.
- Frozen **300 Train + 58 Gold**, 358 Studies, **2,006 Series**, **66,430 physically ordered source Slices** passed UID and DICOM geometry audits. V2 planned **16 shards**, **3,333,191,680 raw pixel bytes**, **4,633,149,184 projected peak bytes**, < project 14GB decimal total working-file cap.
- **Actual error at first V2 pixel-cache decode:** `AssertionError` from `hh=int(round(130.0/dy)); ww=int(round(130.0/dx)); assert hh>=3 and ww>=3 and hh<=h and ww<=w`. At least one Series has native in-plane physical FOV below required 130mm and therefore cannot provide that requested full centered crop without handling image boundaries.
- **No 'SHARD VERIFIED' completion messages** appear in supplied log. V2 threw `FAILED_PARTIAL_SHARDS_PRESERVED` and did not generate a normal `RMIL-02B_results_for_review.zip`. An incomplete `.h5.tmp` might have been written; it must NOT be reused as valid. No disk quota error occurred. The failed log does NOT identify the offending Study/Series or the total number of affected Series, so do not invent those.

## Chosen V3 controlled-preprocess fix

V3 uses fixed **130mm physical FOV** at 224×224 resolution for every Series. Per in-plane axis, compute `wanted_px=round(130mm/pixel_spacing)`, center a crop on the original image; **intersect** with actual source pixels. If crop goes beyond source field, pad only outside-image pixels with **constant normalized Z=-5** (equivalently uint8 0 at final mapping) **before resizing**. No reflection, wraparound, or replication of anatomy; no implicit change from 130mm to smaller effective physical field. Normalize only on original real source pixels (padded pixels excluded from 0.5/99.5 percentile and Series global statistics).

- Preflight **all 2006 Series** for crop geometry/padding **before** starting expensive decode/HDF5 writes. Save `fov_crop_audit.csv` including physical FOV, desired crop, source intersection, pad widths, real/pad fractions; warn if >=20% padded. The actual number affected is UNKNOWN until V3 runs.
- Existing Series positional/UID/photometric validations, Scan SHA manifest checks, K4 numeric anchor and nested K4 ⊆ K16 ⊆ K24 ⊆ K32 policy are held fixed.
- Same 358 Studies/2006 Series/66430 DICOM slices retained. Output one native grayscale 224px uint8 Slice **once**; Window triplets are constructed by indexes. Shards ~220 MB, HDF5 SHA and readback verification, per-shard total working space check, 14GB project cap.
- Cache transformation identifier: `DICOM_PHYSICAL_CROP130_FOV_PAD_MINUS5_SERIES_PERCENTILE_SAMPLED_ZSCORE_CLAMP5_AREA224_UINT8_V3`. This is a **new** version, not original RMIL-01 parity.
- Use fresh Kaggle output directory `/kaggle/working/RMIL-02B_NATIVE224_V3/` and small metadata-only `RMIL-02B_V3_results_for_review.zip`. Do NOT attach or reuse V2 partial temporary caches in future training.
- **New notebook generated for the user:** `RMIL-02B_V3_Native224_FOVSafe_SharedCache_CPU.ipynb`, local SHA-256 `0089f337ff1a8bffb8a58169f6915b7b706a45ebd4875fd48a1ee68689cf6ebf`, valid Notebook JSON + all 4 Python code cells compile. Synthetic preprocessing smoke tests PASS for FOV 130mm-fit and undersized boundaries (including 26%/76% padding cases); nested selector PASS for 310 source Slice lengths N11..320. **Kaggle execution and data-specific result not yet observed**. Recommended Save Version `RMIL-02B-V3 Native224 FOVSafe CPU`, Accelerator None, Internet OFF, same two Inputs.
- **Next:** User runs V3 Save & Run All and shares log + `RMIL-02B_V3_results_for_review.zip`; independently verify CRC/JSON/CSV/metadata SHA/16 expected shard SHA manifest plus actual Kaggle full Notebook output (not bundled), 358/2006/66430, FOV padding distribution and storage cap before any GPU run. Retain complete Kaggle Output containing HDF5 shard files as future attached Dataset/Notebook Output. CPU artifact ZIP **does not contain pixel arrays**.

## Controlled GPU study after success

Pre-existing RMIL-01 performance is immutable and cannot be considered a K4 score under this V3 pixel transform. Train **NEW RMIL-02C K4/K16/K24** Mean baselines on exactly these new pixels and same architecture/optimizer/split/seed; nested centers ensure K16 includes K4 and K24 includes K16. Then fix K and compare MEAN vs Shared Window Attention (RMIL-02D) before target-specific RMIL-03. NO historical DINO cache reuse, per user's preference.

[Experiment protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md) · [Previous metadata PASS](RMIL-02A_COMPLETED_METADATA_AUDIT_2026-10-10.md).
