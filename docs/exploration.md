# Data exploration (train)

Summary of the notebooks in [`notebooks/`](../notebooks/). Each finding points to the notebook that shows it. Only the **train** set was explored; `rank` and `final` are still to check.

## The storyline

The goal is to predict `fuel_kg` for each interval. The exploration followed four questions, each one leading to the next:

```
What do we predict?  →  Is it reliable?  →  What explains it?  →  Do we have that info for every interval?
    (target)             (cleaning)          (features)            (strategy for gaps)
```

1. **The target** ([`explore_fuel`](../notebooks/explore_fuel.ipynb)): fuel burnt during a time window. It is noisy (rounding, pounds converted to kg) and contains impossible values.
2. **What explains it** ([`explore_flight_list`](../notebooks/explore_flight_list.ipynb), [`explore_airport`](../notebooks/explore_airport.ipynb)): aircraft type first, then duration, route and airports.
3. **What the aircraft does** ([`explore_flight`](../notebooks/explore_flight.ipynb)): the trajectory gives altitude, speed and climb rate, but has large gaps.
4. **Putting it together** ([`explore_links`](../notebooks/explore_links.ipynb)): tables join without loss, but about **40% of intervals have no usable trajectory**. This is the finding that drives the modelling strategy.

## Tables

| Table | One row = | Rows | Key |
|---|---|---|---|
| `fuel_train` | one interval of a flight | 131,530 | `idx` |
| `flightlist_train` | one flight | 11,037 | `flight_id` |
| `flights_train` | one trajectory point | 123,587,596 (3 GB of Parquet) | — |
| `airports` | one airport (worldwide) | 8,787 | `icao` |

The three `*_train` tables share **exactly the same 11,037 `flight_id`**: joins on `flight_id` lose no flight.

### Units

| Column | Unit | How we know |
|---|---|---|
| `start`, `end` (fuel), `timestamp` (flights) | integer, **nanoseconds** since 1970-01-01 UTC | 19 digits; converting gives dates in 2025 |
| `takeoff`, `landed` (flightlist) | already UTC timestamps | — |
| `fuel_kg` | kg burnt during the interval | — |
| `elevation` (airports), `altitude` (flights) | feet | in metres, Afghan airports would be above 6,000 m |
| `groundspeed`, `TAS`, `CAS` | knots | aviation convention |
| `vertical_rate` | feet per minute | aviation convention |
| `track` | degrees (0 = north) | aviation convention |

In SQL, `TIMESTAMP_MICROS(DIV(x, 1000))` converts nanoseconds to a timestamp. `end` is a reserved word and must be written `` `end` ``.

## Findings per table

### `fuel_train`: the target

- About 12 intervals per flight, from 2025-04-12 to 2025-09-01 (4.5 months, spring and summer).
- **Interval duration**: 1.6 s to 1 h, median 5 min, middle half between 5 and 10 min.
- **`fuel_kg`**: median 200 kg. No null and no negative values.
- **Several measurement sources**: some values are round numbers in pounds (min = 0.4536 kg = 1 lb; Q3 = 544.31 kg = 1,200 lb), others are rounded to 100 kg. Target precision therefore varies from one flight to another.
- **Average fuel rate per flight** (total fuel / total interval duration): median 0.65 kg/s, with abnormal values on both sides (0.04 to 13.1 kg/s).
- **Two kinds of extremes**:
  - very short intervals with round values (100 kg in 7 s): a rounding artefact of the fuel gauge, very noisy;
  - whole flights with impossible rates on every interval: a systematic issue for those flights (see [Outliers](#outliers)).

### `flightlist_train`: the flights

- 273 origin airports, 260 destination airports, 26 aircraft types, no missing values.
- **Very unbalanced aircraft types**: A20N + A320 = 57% of flights. 13 types have fewer than 30 flights, 3 have a single one (MD11, B39M, A318).
- **Flight duration**: 20 min to 17 h 30, median 4 h.
  - A320 / B737 family: 3 to 4 h, rather long medium-haul.
  - Widebodies (A359, B77W, B789…): 9 to 11 h.
- **Not a Europe-centred dataset**: the most frequent routes link Central and South America, the US, China and Oceania.

### `airports`

- `icao` is a unique key (checked). 219 airports have no elevation.
- Extremes are real: −1,266 ft (Bar Yehuda, Dead Sea) and 14,472 ft (Daocheng Yading, China).
- The 320 airports used in train all exist in the table, all with an elevation. The table is kept as is, since `rank` and `final` also use it.

### `flights_train`: the trajectories

- The trajectory starts **in the air**, about 1 min after takeoff, and ends on the runway. Taxiing on the ground is not covered.
- `altitude` is **barometric**: on the runway at Amsterdam (−11 ft) it reads 375 ft. It is not the true height.
- **Missing values**:
  - `altitude`, `latitude`, `longitude`: ~0% (position message);
  - `groundspeed`, `vertical_rate`, `track`: 31.6% each, always together (velocity message). Easy to fill, points being 1–2 s apart;
  - `mach`, `TAS`, `CAS`: > 99.9%. They only come from `acars` messages (0.1% of points). Airspeed will have to be estimated.
- **Gaps** (more than 10 min between two consecutive points, measured with `LAG`):
  - at least 25% of flights are fully covered, but half lose at least 24% of their trajectory, and a quarter more than 57%;
  - **longer flights have more gaps**: no flight above 6 h 30 is fully covered;
  - **gaps depend on the route**: within a route the gap ratio is stable (Bogotá → Madrid: ~78%; Guatemala → Los Angeles: ~50%). Flights within North America have none. Gaps come from oceans and areas without ADS-B receivers.

## Links between tables

### Interval coverage

- Intervals are **selected windows** of the flight, not a full split. In median, the first one starts 81 min after takeoff and the last one ends 52 min before landing.
- About 7% of flights have an interval extending **onto the ground** (before takeoff or after landing). In 86–90% of these cases it is by less than 30 min: taxi fuel burn. About 1% of flights go beyond 30 min, which is suspicious.

### Intervals without trajectory

Measure: **density**, the number of trajectory points per second within the interval.

- A fully covered interval has about **2 points/s**: the broadcast rate of ADS-B position messages, and the peak of the histogram.
- The histogram shows two populations: a huge peak at 0 and a peak at 2.
- Threshold: the valley of the histogram, around **0.5 points/s** (~25% of the interval covered).

| Criterion | Intervals | Share |
|---|---|---|
| 0 points | 3,051 | 2.3% |
| density < 0.08 (first bar) | 48,194 | 36.6% |
| density < 0.5 (valley) | 54,808 | 41.7% |

The result barely depends on the threshold. **About 4 intervals out of 10 have (almost) no trajectory.** The "0 points" criterion strongly underestimates the issue, because an interval inside a gap often has 1 or 2 points at its edges.

### Outliers

Method: each flight's average fuel rate is compared with the other flights **of the same aircraft type**, using Tukey's "far out" rule: above Q3 + 3 × IQR or below Q1 − 3 × IQR. Reasoning per type is required because rates differ a lot: about 0.3–0.7 kg/s for the A320 family, 1.3–2.3 for big twins, 2.7–5 for quads.

- **205 flights** flagged (1.9%): 115 too high, 90 too low. The issue exists in both directions.
- **Obvious errors**, 4 to 12 times the type's median:
  - `prc790175280` and `prc784170877` (B744, ~13 kg/s);
  - `prc783282112` (A333, 11.1 kg/s);
  - `prc788278172` (A332, 6.6 kg/s);
  - `prc780561659` (A359, 0.14 kg/s).
- The A320 family is almost clean (0.2–0.3% of flights). Widebodies are more affected: B744 14%, B788 11%. For the B788 the distribution is very narrow: the rule may be too strict, or there is a real subgroup.
- **Limits**: Tukey flags candidates, not proven errors. Types with very few flights cannot be judged, and the lower bound can be negative (A333).

## What it means for the model

| Finding | Decision |
|---|---|
| The target is fuel per time window | Predict `fuel_kg` per interval. Interval duration is a key feature |
| Fuel burn depends strongly on aircraft type | Aircraft type is a feature. Rare types will need grouping (by family or engine count) |
| Outliers (Tukey) | Drop obvious errors from training. Decide case by case for the other candidates |
| ~40% of intervals without trajectory | Always-available features: duration, aircraft type, route, time since takeoff and before landing (to infer the flight phase) |
| Gaps are predictable by route | Idea: fill gaps using other flights of the same route |
| No airspeed | Use `groundspeed`, `altitude`, `vertical_rate` |
| Intervals extending onto the ground | The trajectory does not cover the ground: handle this case |

### Next steps

1. **Baseline**: a first simple model without trajectory (duration, aircraft type…), to get a reference score.
2. **Trajectory features** on covered intervals, measuring the gain over the baseline.
3. **OpenAP**: a physics-based fuel estimate used as a model feature (hybrid approach). Mass is unknown and will have to be assumed.

## Open questions

- `rank` and `final` sets not explored: same structure? New airports or aircraft types? Comparable trajectory coverage?
- Expected format of `fuel_submit_rank` / `fuel_submit_final`.
- The B788 case (11% of flights flagged): rule artefact or real subgroup?
