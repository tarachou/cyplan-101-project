# San Francisco Destination Availability by Neighborhood Income

CYPLAN 101 Track B midterm project.

This project compares mapped destinations and their recorded opening hours across six San Francisco neighborhoods: two from each of three relative income groups.

The midterm analysis establishes the data foundation. It does not yet calculate 15-minute walking, transit, or driving accessibility.

## Setup and running the analysis

The project was developed using Python 3.9.13.

From the project folder, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Open `analysis.ipynb` in VS Code and select the project's `.venv` Python kernel. Use **Restart Kernel and Run All Cells** to reproduce the analysis.

Run the notebook with the project folder as the working directory. Data and output paths are relative to that folder.

Package installation is a setup step and does not need to be repeated for each notebook run.

## Data sources

- **Neighborhood boundaries:** The supplied SF Analysis Neighborhoods file, `data/analysis_neighborhoods.geojson`, contains 41 neighborhoods.
- **Income and households:** The 2024 ACS 5-year dataset from the US Census Bureau. Fields B19013 and B11001 provide median household income and total households, including margins of error. The raw response is included as `data/raw/acs_2024_sf_tracts_raw.csv`.
- **Tract boundaries:** The Census Bureau's 2024 California TIGER/Line tract boundaries. The notebook downloads the ZIP if it is missing and filters it to San Francisco County.
- **Destinations and opening hours:** OpenStreetMap data retrieved through OSMnx. The raw GeoJSON snapshot and query metadata are stored in `data/raw/`.

Source links:

- ACS API: https://api.census.gov/data/2024/acs/acs5
- Tract boundaries: https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_06_tract.zip
- OpenStreetMap attribution and licensing: https://www.openstreetmap.org/copyright

Keep the supplied raw snapshots to reproduce the submitted results. A fresh OpenStreetMap download may produce different records.

## Analysis workflow

1. Check neighborhood names and geometries.
2. Clean Census estimates and document special missing-value codes.
3. Match Census statistics to tract boundaries using GEOIDs.
4. Overlay tracts with neighborhoods in EPSG:26910, a projected CRS measured in meters.
5. Estimate household allocations and household-weighted neighborhood income indicators.
6. Divide all 41 neighborhoods into relative income thirds.
7. Select two neighborhoods near each group's median, requiring at least 1,000 estimated households for case selection.
8. Collect and classify destinations within half-mile-buffered search areas.
9. Review destination status, categories, possible duplicates, and boundary cases.
10. Spatially join destination points to search areas using `gpd.sjoin`.
11. Audit opening-hours information and evaluate eligible schedules.
12. Save cleaned datasets, cleaning logs, summary tables, maps, and charts.

The spatial join determines which destinations contribute to each search area's counts and time-of-day results.

## Cleaning and preliminary results

The destination workflow starts with 4,797 candidates and retains 3,709 destination records after screening, review, and merging.

Of the retained destinations:

- 1,605 have schedules eligible for evaluation.
- 2,078 have missing hours.
- 26 have ambiguous comments and remain unknown during evaluation.

Four opening-hours strings received documented punctuation repairs. Original source text is preserved.

Schedules are evaluated every 30 minutes from 06:00 through 24:00 on Wednesday, October 21, and Saturday, October 24, 2026, using the America/Los_Angeles time zone.

Detailed decisions and affected record counts are saved in `outputs/tables/`, including `business_cleaning_summary.csv` and `acs_cleaning_log.csv`.

## Outputs

- `data/raw/`: source snapshots and query metadata.
- `data/processed/`: cleaned Census data, destination points, study boundaries, search-area membership, and recorded opening states.
- `outputs/tables/`: summaries and cleaning/review logs.
- `outputs/figures/`: neighborhood map and four preliminary chart figures.

## Limitations

The income indicator is a household-weighted average of tract median incomes, not an official neighborhood median. Household allocation still assumes uniform distribution within the neighborhood-covered portion of each tract. Renormalizing allocations conserves household totals by construction; it does not verify their locations.

The six neighborhoods are purposively selected cases, not a representative sample establishing an income effect. The 1,000-household selection threshold is a practical case-selection rule, not a guarantee of statistical reliability.

OpenStreetMap coverage and opening-hours completeness vary between areas. Recorded hours are not verified business activity, and missing or ambiguous hours remain unknown.

Polygon destinations are represented by interior points rather than verified entrances. Search areas overlap, so a destination can contribute to multiple neighborhood summaries. Duplicate screening may miss additional duplicate representations.

Buffered destination counts and recorded opening states do not measure travel accessibility. Residential origins, transport networks, and travel-time calculations remain work for the final project.