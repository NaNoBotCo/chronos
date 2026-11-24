# Protocol

Five experiments, five gates. Each gate ends with a written pass or fail. If the time crystal does not appear, write that down as the result. A striking video is not a result.

## Every run records

- run id and date
- bead diameters, how they were measured, and the uncertainty
- levitator settings: supply voltage, step-down setting, frequency (40 kHz nominal)
- camera, frame rate, exposure, scale (mm per pixel), lighting
- the original video, untouched
- tracking CSV (`chronos track`)
- analysis output and plots (`chronos analyze`)
- notes: drift, drops, anything odd

Raw video lives apart from derived files. Version every change to the code.

## Gate 1: design

- Read the paper and its appendices (arXiv 2504.15495).
- Download the OSF data (https://doi.org/10.17605/OSF.IO/SX7UG) and run `chronos analyze` on one of the published tracking files. **Pass:** the pipeline finds the opposite-ways peak near 66.8 Hz.
- Freeze the parts list (`hardware/bom.csv`).

## Gate 2: levitation (experiments 1 and 2)

**Experiment 1, one bead.** Float one bead. Record where it sits, how still it is, and how that changes as the drive goes up and down.
**Pass:** the bead stays in its spot long enough to repeat a 100 s measurement.

**Experiment 2, two beads.** Put two beads in neighbouring spots, 4.3 mm apart. Try several size combinations.
**Pass:** both stay put, and the tracker follows each one separately.

No camera purchases before Gate 2 passes.

## Gate 3: measurement

Film at 200 to 240 frames a second for about 100 s, dark background, steady light. Calibrate mm per pixel with a ruler in the frame. Check that the frame times are even.
**Pass:** the tracker returns both beads in at least 99% of frames, and a one-bead run gives a clean noise floor.

## Gate 4: the time crystal (experiments 3 and 4)

**Experiment 3, find the active pairs.** Hold the drive constant. Work through bead pairs near 2.9 + 3.3 mm, then 3.0 + 3.2 and 2.8 + 3.3. Equal sizes make a control pair. Look for motion that starts and keeps going with no low-frequency forcing.

**Experiment 4, read the spectrum.** For each pair, compare the together mode (z1 + z2)/2 with the opposite mode (z1 − z2)/2.
**Pass:** repeated runs show a lasting peak in the opposite mode, well above the one-bead noise floor, at a frequency close to the paper's (66.8 Hz there; your apparatus may differ a little). Coherence time is reported with its uncertainty.

## Gate 5: controls and replication (experiment 5)

1. One bead alone: the noise baseline.
2. A pair the model says should sit still (equal sizes, or a 1.5 size ratio).
3. The same pair, run again on another day.
4. Other pairs of similar sizes.
5. Look for anything else that could make a 67 Hz signal: ripple in the supply, flicker in the lamp, building vibration, the camera's own timing.

**Pass:** the effect follows the bead sizes, repeats, and survives the checks in item 5.

## Exhibit

The audience watches a screen, not the levitator up close. The screen shows:

- live or recorded bead heights,
- slow motion,
- the two-mode spectrum,
- the cartoon toy.

Each one is labelled as measurement, simulation or illustration.
