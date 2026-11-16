# Real water-quality datasets

These CSV files were downloaded from public GitHub repositories on 2026-11-15
for evaluating the water-potability fuzzy inference system.

| File | Source | Records | Relevant fields |
|---|---|---:|---|
| `water_quality_analytics.csv` | [siddhikalate-ds/water-quality-analytics-](https://github.com/siddhikalate-ds/water-quality-analytics-) | 400 | `pH`, `DO_mg_L`, `TDS_mg_L`, `Turbidity_NTU` |
| `water_quality_dataset.csv` | [nallamillisavitha/Water-Quality-Data-Analysis-System](https://github.com/nallamillisavitha/Water-Quality-Data-Analysis-System) | 103 | `pH`, `DO [mg/l]`, `TDS [mg/l]`, `Turbidity [NTU]` |
| `predicting_wqi_data.csv` | [Ummaarr/PREDICTING-WATER-QUALITY-INDEX-USING-MACHINE-LEARNING](https://github.com/Ummaarr/PREDICTING-WATER-QUALITY-INDEX-USING-MACHINE-LEARNING) | 115 | `pH`, `DO(mg/l)`, `TDS(mg/l)`, no turbidity column |
| `smart_water_quality.csv` | [aastha130307/Smart-Water-Quality-Monitoring-System](https://github.com/aastha130307/Smart-Water-Quality-Monitoring-System) | 6,720 | `ph`, `Turbidity`, `Solids` (TDS proxy), no DO column |
| `water_quality_ml.csv` | [mahabatool45-sudo/ml-project](https://github.com/mahabatool45-sudo/ml-project) | 2,000 | `pH`, `Dissolved_Oxygen`, `TDS`, `Turbidity` |
| `back_bay_refuge_water_quality.csv` | [U.S. Fish & Wildlife Service / Data.gov](https://catalog.data.gov/dataset/water-quality-data) | 2,371 | `pH`, dissolved oxygen, turbidity not reported, salinity available |

The first two files can be passed through the project after column-name
normalization. The other two are retained as supplementary real-world sources:
`predicting_wqi_data.csv` lacks turbidity, while `smart_water_quality.csv` lacks
dissolved oxygen and uses `Solids` as a TDS-like measurement. Do not silently
substitute those fields when benchmarking the four-input FIS.

`water_quality_ml.csv` is the most convenient additional four-input file after
column normalization. `back_bay_refuge_water_quality.csv` is an official
government field dataset and is useful for validating pH and dissolved-oxygen
behavior, but it does not contain TDS or turbidity.

The CSV contents are kept unchanged from their public sources; the source links
above provide provenance and the original schemas.
