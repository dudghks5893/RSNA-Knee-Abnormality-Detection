# RMIL-02A — Completed Native Slice Metadata/Geometry and Disk Preflight Audit

**Updated:** 2026-10-10. **Status: COMPLETED — PASS_METADATA_PREFLIGHT.** RMIL-02B image cache **NOT CREATED**; original RMIL-01 K4 pixel preprocessing parity **NOT EVALUATED**. Gold58 repeated development validation, not an independent test; NO model training or AUROC change.

## User-supplied evidence / independent integrity audit

- Original Kaggle output log `붙여넣은 텍스트(1)(20261009-193311).txt` and review file `RMIL-02A_results_for_review.zip`; independently SHA256-hashed received ZIP **`fbabf2840be680d62c636f86af5e4bb1cc87a3c6c2619fe875d0dfca6008520f`**.
- Original ZIP **10 entries**, `ZipFile.testzip() == None` (CRC PASS), all **9 manifest-listed artifact SHA-256 hashes independently recomputed PASS**, all tables/JSON readable and internally consistent. `issues.csv` has **0 issues**.
- Kaggle logs show actual competition source `/kaggle/input/competitions/rsna-knee-abnormality-detection`, legacy K4 `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`, exact manifest SHA and full frozen K4 pixel/meta SHA checks PASS, pydicom 3.0.2, CPU (no GPU). Source DICOM sample `pixel_array` decoded PASS (512×512 int16). All are prior Kaggle runtime reports; the underlying DICOM files were not present in the uploaded review ZIP.
- Frozen 300 Train + 58 Gold = **358 unique Studies**, **2,006 unique Series**, **66,430 physically ordered source DICOM Slices**, zero geometry/UID/plane/Sequence metadata issues, all Series have ≥3 consecutive real Slice candidates. Survey recorded **11.254 min** Kaggle runtime. Source metadata original order, physical position, slice spacing, Series/SOP identifiers, unique center selections all independently verified within the ZIP.
- `cache_index_sha256.csv` original SHA **`664b9b6ef3889e2d1d9694b0fd0424afa32ce8785ea99ddfdfbb53d85e87495e`**.
- **New insight, independently reproduced over 2,006 JSONL records:** old K4 `legacy_K4_series_centers_uninterpreted` equals `np.rint(np.linspace(0.1*(N-1), 0.9*(N-1), 4)).astype(int)` **for all 2006/2006 Series**, using each actual source Series length. This proves a numerical legacy selection-index formula. It does **NOT** prove that the old preprocessing used the same forward/reverse physical Slice ordering, exact Crop130mm, percentile/Z-score normalization, interpolation, MONOCHROME1 conversion or quantization. The new `uniform_spaced_valid_centers_v1` 4-centers typically differ from old K4 center indices.

## Actual K feasibility (358 Studies × all 2,006 Series)

| K | Complete K Series | Underfilled Series | Mean effective K/Series | Total actual unique 3-Slice Windows | Raw separate 3×224² uint8 GiB if stored |
|---:|---:|---:|---:|---:|---:|
| 4 | 2,006 (100%) | 0 | 4.000000 | 8,024 | 1.124886 |
| 16 | 1,924 (95.91%) | 82 | 15.871386 | 31,838 | 4.463373 |
| 24 | 1,513 (75.42%) | 493 | 22.667996 | 45,472 | 6.374725 |
| 32 | 516 (25.72%) | 1,490 | 26.685942 | 53,532 | 7.504658 |

Native per-Series Slice count range 11–320, median 30; max physically valid centered triplets N−2. No duplicate-padding or synthetic extra evidence. **Conservative next GPU experiment recommendation after cache parity:** paired **K16 MEAN vs K24 MEAN**, not K16 vs K32 first. K24 adds **13,634** actual windows over K16 (+42.8%); K32 adds only **8,060** over K24 (+17.7%), and 74.28% of Series cannot fill K32. K32 is a conditional later study, not prohibited.

## Real disk budget

- Source native 224×224 uint8 1-channel estimate: **66,430 × 224 × 224 = 3,333,191,680 bytes = 3.104276657 GiB**. This is exact pixel payload arithmetic using actual counted source Slice numbers, NOT actual encoded cache disk size.
- Overhead/staging estimate: **ceil(payload×1.30) + 300,000,000 = 4,633,149,184 bytes = 4.633 GB (decimal)**.
- Actual Kaggle `/kaggle/working` existing output at preflight: **16,218,532 bytes**. Project **14.0 GB decimal aggregate output cap**; remaining cap **13,983,781,468 bytes**, physical free **20,924,284,928 bytes**, reserved physical free 2GB, effective safe additional **13,983,781,468 bytes**.
- Result **`single_run_cache_eligible_by_budget = true`**, but classified **`BUDGET_CANDIDATE_ONLY_NOT_PIXEL_PARITY_RELEASE`**. RMIL-02B must recheck each 256–512MB shard write and all working usage; avoid a second large duplicate ZIP. The Kaggle platform saved-output limit is documented as 20GB; 14GB is stricter project cap, not a platform limit.

## Controlled selection correction for future GPU work

The RMIL-02A `uniform_spaced_valid_centers_v1` independently recomputes each K set and is **not nested** across K. Thus it is valid for feasibility, but do NOT use it as a strict add-only K16→K24 GPU ablation. New planned version `NESTED_LEGACY_ANCHORED_FARTHEST_POINT_V2` starts with the four numerically verified legacy K4 centers and appends each missing center with maximum distance to nearest selected center (deterministic lowest-index tie-break), storing K4/K16/K24/K32 as prefixes of one sequence. Physical ordering / exact legacy pixel pipeline must still be verified. See the [detailed selector v2 policy](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).

## Next step and BLOCKER

**RMIL-02B0, PREPARED CPU Notebook (not executed):** `RMIL-02B0_K4_Pixel_Parity_Probe_CPU.ipynb`, local SHA256 **`0bf941097a3bdd5db04b4093f6dfe7e853127b5704011db5cbe98251a209804c`**; requires only the same two Kaggle inputs. It samples 9 original train/Gold Series across the three planes and compares a set of explicit diagnostic Crop130/normalization/interpolation and physical order hypotheses against SHA-pinned original K4 uint8 tensor bytes. Reports candidate MAE/exact byte match rates and SHA+review ZIP. It does NOT create any image cache and **a sample match is not final full-parity certification**. Original exact `R2D-CACHE-01` code is preferable if retrievable; without it, do not silently declare `RMIL-02B` new full-native single-channel image cache approved.

**After strict K4 pixel parity is proven:** CPU-build only the 358-Study native 224×224 grayscale Slice cache, 14GB project output cap, SHA shards and metadata-only ZIP. Shared cache avoids building K16/24/32 duplicate images. Then controlled K16 Mean vs K24 Mean and at a matched selected K Mean vs shared Attention on Kaggle T4×2. Preserve RMIL-01 result; RMIL-03 disease-aware attention remains a later separate hypothesis. C1/C2/C3, folds, Exp57 hybrid all undecided.

[RMIL-02/03 approved protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md) · [RMIL-01 completed audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md).
