# Agent allocation model — protocol frozen before the run

**Status:** Tier 2 support for the structural interpretation. The model is a
transparent two-agent decision model, not a causal identification. It is
labelled "model-reproduced, not identified" wherever it appears.

## Purpose

Show that one simple parameterisation of how a coach allocates role and a GM
sets pay reproduces the observed moments, and that the difference between the
two agents' performance weights is the lever. The model is subordinate to the
measured levers; it is not a new headline.

## Agents and rules

- **Coach (role):** `role_z ~ perf_z + B_draft + prestige_nodraft + position + season`.
  Calibrate the performance and draft/status coefficients to the observed
  concurrent-role model.
- **GM (pay):** `log cap ~ perf_z + snap_share + age + experience + position`
  on the full 909-player ledger. Calibrate the performance coefficient.
- **Player/scout:** the Combine signal is position-specific; the model uses the
  position-specific Combine result as a descriptive input, not a simulated
  outcome.
- **League:** the rookie wage scale is a descriptive status term; it is not
  simulated.

## Calibration moments

1. Coach performance coefficient (concurrent role).
2. Coach draft/status coefficient.
3. GM performance coefficient (full ledger).

## Validation moments (not used to calibrate)

1. Allocation gap by draft quartile (late positive, early negative).
2. Strict-tail current role (the top-performance/bottom-role quartile).
3. Cap performance coefficient with role (the 909-ledger role-controlled model).
4. Lever monotonicity: a higher coach performance weight raises the top
   performance group's role and lowers the allocation gap; a lower status
   weight does the same.
5. Negative control: shuffle performance within position and season; the wedge
   and lever effect should vanish.

## Levers

- Coach performance weight from the observed value to the GM's value.
- Coach status weight from the observed value to half.

## Failure criteria

- A calibration coefficient outside the observed 95% CI.
- A validation moment with the wrong sign or a magnitude outside the stated
  tolerance (allocation gap: ±0.15 SD; strict-tail role: ±0.15 SD).
- A non-monotonic lever.
- The negative control reproduces the lever effect.

If any failure occurs, report it and do not use the model as support; the
entry falls back to the assumption layer and the measured levers.

## Labelling and limits

- "Model-reproduced pattern, not causal identification."
- The model does not simulate wins, contracts, or careers.
- The model is one paragraph, one figure, and one notebook cell.
- Deterministic; the only random element is the negative-control shuffle, with
  a fixed seed.
