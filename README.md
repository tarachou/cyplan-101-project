# San Francisco Walking Accessibility by Neighborhood Income

Team Members: Bushra Noor, Ash Gupta, Tara Chou, Prabhav Pagadala
CYPLAN 101 Track B project.

This project compares walking access to destinations and their recorded opening hours across six San Francisco neighborhoods: two from each of three relative income groups.

The notebook contains the original midterm analysis followed by the final walking-accessibility analysis. The final analysis uses residential origins, an OpenStreetMap pedestrian network, and recorded opening schedules to estimate reachable destinations throughout the day.

Transit and driving accessibility are not implemented.

## Setup and running the analysis

The current analysis was developed using Python 3.13.5 in the `.venv-final` environment. Package versions are listed in `requirements.txt`.

To create a new environment, first ensure that `python3` refers to a Python 3.13 interpreter:

```bash
python3 --version
python3 -m venv .venv-final
source .venv-final/bin/activate
python -m pip install -r requirements.txt
```

If the environment already exists, activate it:

```bash
source .venv-final/bin/activate
```

Open `analysis.ipynb` in VS Code and select `.venv-final/bin/python` as the notebook kernel. Terminal activation and notebook kernel selection are separate steps.

Run the notebook with the project folder as the working directory. Paths are relative to that folder. Cells depend on earlier cells and should be run in order.

Run the notebook cells in order, starting from a fresh kernel.

Package installation is a setup step and does not need to be repeated for each notebook run.

### Local files and internet access

Ensure project files are downloaded locally before running the notebook or committing changes. Cloud-only placeholder files can cause read errors or slow imports.

Keep the saved source snapshots, network, metadata, and distance checkpoint to reproduce the analyzed results. Some cells download missing inputs or reuse cached responses. Fresh downloads may produce different records.

An internet connection is needed for downloads and for the external map libraries and background tiles used by the interactive maps.

## Data sources

- **Neighborhood boundaries:** `data/analysis_neighborhoods.geojson` contains 41 San Francisco Analysis Neighborhoods.
- **Income and households:** The 2024 ACS 5-year dataset provides tract median household income and household counts through B19013 and B11001, including margins of error. These estimates cover 2020–2024.
- **Tract boundaries:** The Census Bureau's 2024 California TIGER/Line tract boundaries, filtered to San Francisco County.
- **Destinations and opening hours:** OpenStreetMap records retrieved through OSMnx. Original snapshots and query metadata are preserved.
- **Residential locations:** SF Planning land-use attributes, with a source data date of August 17, 2026. Residential-use counts and supplied centroid coordinates support origin selection.
- **Pedestrian network:** An expanded OpenStreetMap walking network downloaded through OSMnx.
- **External route comparison:** Google Maps walking directions were inspected for 10 sample journeys.

Source links:

- ACS API: https://api.census.gov/data/2024/acs/acs5
- Tract boundaries: https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_06_tract.zip
- SF land-use attributes: https://data.sf.gov/resource/c5ge-t6pj.json
- OpenStreetMap attribution and licensing: https://www.openstreetmap.org/copyright

The datasets have different reference periods. Current source records and recorded schedules do not establish historical business activity on the analysis dates.

## Study neighborhoods and income indicator

The selected neighborhoods are:

| Relative income group | Neighborhoods |
|---|---|
| Lower | Bayview Hunters Point; Japantown |
| Middle | Mission; Sunset/Parkside |
| Higher | Haight Ashbury; Mission Bay |

The income indicator is a household-weighted average of tract median incomes, not an official neighborhood median.

Tracts and neighborhoods are overlaid in EPSG:26910, a projected coordinate system measured in meters. Household allocations are renormalized over each tract's neighborhood-covered area.

All 41 neighborhoods are divided into relative income thirds. Two cases near each group's median are selected, requiring at least 1,000 estimated households.

## Analysis workflow

### Midterm foundation

1. Check neighborhood names and geometries.
2. Clean Census estimates and document special missing-value codes.
3. Match Census statistics to tract boundaries using GEOIDs.
4. Overlay tracts and neighborhoods.
5. Estimate household allocations and neighborhood income indicators.
6. Select six study neighborhoods.
7. Collect destinations in half-mile-buffered search areas.
8. Review status, categories, duplicates, geometry, and opening hours.
9. Save preliminary destination counts and recorded availability.

These buffered counts provide descriptive context; they are not walking-accessibility measures.

### Final walking analysis

1. Screen SF Planning residential-use records and select locations inside the six neighborhoods.
2. Select one reported residential location per occupied 250-meter grid cell within each neighborhood.
3. Download an expanded pedestrian network and destination inventory surrounding the study neighborhoods.
4. Apply documented destination status, category, duplicate, and opening-hours decisions.
5. Review origin and destination connections to the pedestrian network.
6. Construct routing attachments, including modeled approach distances.
7. Calculate shortest-path distances up to 2,000 meters.
8. Evaluate recorded opening schedules at 74 reference times.
9. Summarize reachable destinations by origin, neighborhood, category, and time.
10. Compare walking-time, speed, unknown-hours, and unresolved-connection scenarios.
11. Inspect 10 sample journeys against external walking directions.
12. Export tables, figures, and interactive HTML maps.

## Cleaning and inventory counts

### Midterm inventory

The original destination workflow starts with 4,797 candidates and retains 3,709 destination records.

Of these, 1,605 have schedules eligible for evaluation. Another 2,078 have missing hours, and 26 have ambiguous comments that remain unknown during evaluation.

### Expanded final inventory

The expanded destination workflow starts with 8,574 candidates:

| Step | Records affected |
|---|---:|
| Excluded by status screening | 145 |
| Held for unresolved status | 16 |
| Excluded as out-of-scope services or shopping-centre aggregates | 1,478 |
| Held for unresolved category decisions | 166 |
| Held for unresolved duplicate relationships | 31 |
| Redundant representations combined through supported merges | 10 |
| Retained destination records | 6,728 |

Original source records and documented review decisions are preserved.

Of the 6,728 retained destinations:

- 2,830 have schedules eligible for evaluation.
- 3,853 have missing hours.
- 45 have comments requiring review and remain unknown.
- Seven destination schedules receive documented syntax repairs.

No destinations are removed solely because opening hours are missing or ambiguous.

### Residential origins and routing coverage

The residential source contains 153,765 records. Screening retains 139,533 locations with positive dwelling or group-quarter counts and usable coordinates.

Of these, 37,405 locations fall inside the selected neighborhoods. Grid construction produces 446 residential origins.

The primary routing analysis includes:

- 443 residential origins; three remain unresolved.
- 6,677 destinations; 51 remain unresolved.

Unresolved connections are preserved and reported separately, rather than treated as zero access.

Detailed cleaning decisions, reasons, and affected counts are stored in `outputs/tables/`.

## Walking and opening-hours assumptions

The baseline uses a 15-minute walking budget at a constant 4.8 km/h, equivalent to 1,200 meters.

Modeled distances include pedestrian-network travel and straight approach links between source locations and their selected network edges. Approach links are not verified building entrances.

Schedules are evaluated every 30 minutes from 06:00 through 24:00 on:

- Wednesday, October 21, 2026.
- Saturday, October 24, 2026.

Times use `America/Los_Angeles`. The 24:00 observation represents midnight at the start of the following day.

Opening states describe the selected reference time, not an arrival time calculated separately for each journey.

Missing, ambiguous, or unresolved schedules remain unknown. Only explicitly recorded-open states contribute to the main recorded-open counts.

Neighborhood summaries use unweighted medians across sampled origins. They are not population- or dwelling-unit-weighted estimates.

## Validation and sensitivity checks

Internal checks confirm that extracted sample-route lengths agree with the distance matrix.

Ten sample journeys were also inspected using Google Maps walking directions. Comparisons supported broadly plausible walking corridors while identifying differences in street alternatives, endpoint connections, and travel-time estimates.

These are browser-assisted external spot checks, not field verification. Exact building entrances, physical access conditions, and business opening status were not verified. Google's displayed distances are rounded.

The review is recorded in:

`outputs/tables/walking_manual_route_review.csv`

Sensitivity analyses compare:

- Walking budgets of 10, 15, and 20 minutes.
- Walking speeds of 3.6, 4.8, and 6.0 km/h.
- Recorded-open counts with a scenario assuming unknown hours are open.
- Extreme inclusion scenarios for unresolved network connections.

Scenario gaps are not confidence intervals. They do not account for all businesses absent from OpenStreetMap or excluded through unresolved classification decisions.

## Outputs

- `data/raw/`: source snapshots, query metadata, and the downloaded pedestrian network.
- `data/processed/`: cleaned inventories, residential origins, routing attachments, recorded opening states, and distance checkpoints.
- `outputs/tables/`: cleaning logs, review decisions, accessibility summaries, and sensitivity results.
- `outputs/figures/`: preliminary figures, routing diagnostics, and final charts.
- `outputs/maps/`: interactive HTML maps.

### Final charts

The following figures are saved as PNG and PDF:

- `final_walking_noon_comparison`
- `final_walking_availability_by_time`
- `final_walking_access_by_category`
- `final_walking_missing_hours_sensitivity`
- `final_walking_time_speed_sensitivity`

Additional figures show residential origin coverage, the walking network, and sample routes.

### Interactive maps

- `outputs/maps/final_walking_neighborhood_noon.html`: neighborhood comparison with Wednesday and Saturday noon layers and detailed popups.
- `outputs/maps/final_walking_access_through_time.html`: origin-level animation with a day selector, time slider, and playback controls.

To preview the maps locally from the project folder:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory outputs/maps
```

Then open:

- http://127.0.0.1:8000/final_walking_neighborhood_noon.html
- http://127.0.0.1:8000/final_walking_access_through_time.html

Leave the server running while previewing. Press Control+C to stop it. These local addresses are not public sharing links.

## Limitations

Household allocation assumes uniform distribution within the neighborhood-covered portion of each tract. Renormalization conserves household totals but does not verify household locations.

The six neighborhoods are purposively selected cases, not a representative sample establishing a causal income effect. Differences within income groups can be substantial.

Residential source centroids and grid representatives approximate starting locations. Origin summaries are unweighted, and reported dwelling counts are not occupied-household or population counts.

OpenStreetMap destination coverage, classification, network connectivity, and opening-hours completeness vary geographically. Recorded-open counts therefore reflect both modeled access and documentation coverage.

Source points and polygon interior points are not verified entrances. Straight approach links may overlook physical barriers. The walking model does not explicitly account for slope, crossing delays, temporary closures, or individual mobility differences.

Destination categories can overlap. A multi-category destination may contribute to more than one category, while all-destination totals count distinct records.

Unknown schedules and unresolved connections remain documented separately. Sensitivity scenarios illustrate selected assumptions; they do not remove the underlying uncertainty.

The source snapshots have different dates, and the evaluated schedules are not observations of actual openings on the reference dates.