# EcoServants NY Funder Research

A Python-based data extraction and filtration pipeline designed to identify, process, and track potential funder prospects in New York utilizing Big Metafounding (BMF) data records.

## 📁 Repository Structure

* **`data/`**: Directory containing the raw input datasets.
* **`extract_funders_from_bmf.py`**: Script to parse and extract relevant funding entities from raw BMF source files.
* **`filter_ny_funders.py`**: Script to filter the extracted data specifically for New York-based prospects.
* **`funder_prospects.csv`**: Compiled list of targeted prospective funding organizations.
* **`ny_funders.xlsx`** & **`ny_funders_updated.xlsx`**: Organized spreadsheet sheets capturing the refined New York funding targets.

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed along with `pandas` and `openpyxl` (required for Excel files):
```bash
pip install pandas openpyxl
```

### Execution Pipeline
1. Place your raw BMF files inside the `data/` folder.
2. Run the extraction script to parse the master foundation logs:
   ```bash
   python extract_funders_from_bmf.py
   ```
3. Run the filter script to isolate NY specific entities:
   ```bash
   python filter_ny_funders.py
   ```
4. A final Stage was entirely on excel spreadsheet, where I filled cells acording to researches on propublica web site.

## 🛠️ Built With
* **Python 100%** — Primary programming language.
* **Pandas** — Data manipulation and analytical processing.


