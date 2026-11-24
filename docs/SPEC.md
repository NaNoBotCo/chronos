<!-- stylecheck: allow-start -->
# Build Specification: Acoustic Time Crystal

**Project name:** Chronos — Tabletop Time Crystal
**Version:** 1.0
**Project type:** Experimental physics / open-source scientific instrument
**Reference experiment:** Morrell, Elliott & Grier, *Physical Review Letters* 136, 057201 (2026)

## 1. Project scope

Develop a compact, computer-monitored laboratory instrument that uses ultrasonic standing waves to suspend two expanded-polystyrene (EPS) spheres in air.

The system must permit controlled experimentation with particle size, acoustic excitation, and interparticle interactions, with the aim of reproducing a classical continuous time-crystal state.

This is not a quantum time crystal. The project concerns an experimentally demonstrated classical phenomenon.

### Project success levels

| Level | Demonstration | Outcome |
|---|---|---|
| 1 | Suspend a single bead in air | Successful acoustic levitation |
| 2 | Suspend two beads in separate acoustic nodes | Two-particle experimental platform |
| 3 | Record and measure persistent collective oscillations | Working quantitative experiment |
| 4 | Identify a sustained antisymmetric mode consistent with the published model, supported by control experiments | Credible time-crystal replication |
| 5 | Reproduce results across multiple bead pairs and document uncertainties | Science-fair research demonstration |

Level 4 is the primary scientific target. Levels 1–3 are valuable intermediate achievements but do not establish a time crystal.

## 2. Hardware requirements

### A. Acoustic levitation system

| Component | Requirement |
|---|---|
| Ultrasonic emitters | 72 matched 40 kHz transmitting transducers, 10 mm diameter |
| Transducer spares | Approximately 4–10 additional units |
| Frame | Rigid, 3D-printed dual-array TinyLev-compatible structure |
| Controller | Arduino Nano or equivalent |
| Driver | Suitable dual H-bridge transducer driver, such as L298N in the original design |
| Power | Regulated DC supply matched to the chosen drive circuit |
| Controls | Power switch, adjustable drive settings, emergency shutdown |
| Mechanical base | Rigid, vibration-resistant mount |
| Acoustic field | Stable standing wave along a vertical axis |

The design should be compatible with the published TinyLev architecture, but the final geometry and driving circuit must be checked against the time-crystal experiment. Generic levitation kits are not guaranteed to reproduce the same conditions.

**Important design targets:**

- Operating frequency near 40 kHz.
- Adjacent acoustic traps approximately 4.3 mm apart.
- Stable suspension of two appropriately sized spheres.
- Adjustable acoustic drive amplitude.
- Constant drive conditions during the principal experiment.
- No deliberate low-frequency modulation intended to produce the observed bead oscillations.

### B. Experimental particles

Use approximately spherical EPS beads with controlled diameters and reasonably consistent material density.

Requirements:

- A collection of beads spanning approximately 2–4 mm diameter.
- Pairs with similar and dissimilar diameters.
- Diameter measurement or image-based sizing.
- Unique identifiers for tested bead pairs.
- A record of particle sizes and estimated measurement uncertainty.

**Initial target pair:** approximately 2.9 mm and 3.3 mm diameter, based on one of the reported experimental regimes. These are starting values, not a guaranteed recipe.

### C. Measurement and imaging system

The measurement system is essential. Visual observation alone cannot establish the target behavior.

| Component | Minimum requirement |
|---|---|
| Camera | At least 200 frames per second |
| Recording duration | Approximately 100 seconds continuously |
| Resolution | Sufficient to locate bead centers accurately |
| Camera mount | Rigid tripod or optical mount |
| Lighting | Stable, flicker-controlled illumination |
| Background | High contrast, preferably matte black |
| Computer | Capable of storing and processing full recordings |
| Calibration | Known length scale and verified frame timestamps |

A smartphone capable of 240 fps can be used for initial experiments, provided it can record long enough with reliable timing. A machine-vision camera is preferable for final data collection.

### D. Safety requirements

- Use a properly enclosed low-voltage power system with appropriate circuit protection.
- Secure the transducer arrays and shield exposed electronics.
- Prevent direct contact with energized components.
- Use a guarded experimental area and minimize exposure to the concentrated ultrasonic field.
- Evaluate both ultrasonic and audible noise, using appropriate measurement equipment rather than assuming inaudibility means safety.
- Keep animals and spectators away from an operating apparatus until exposure has been assessed.
- Turn off acoustic power before adjusting beads or reaching into the apparatus.
- Provide an immediate shutdown control.

The science-fair exhibit should be operable without requiring spectators to approach the acoustic field.

## 3. Software requirements

The software system should consist of four modules.

**Module A: Instrument control**

- Set acoustic drive parameters.
- Record drive frequency and settings.
- Display instrument status.
- Support controlled experimental runs.
- Record run metadata.

**Module B: Particle tracking**

- Import high-frame-rate video.
- Locate each bead in successive frames.
- Estimate bead center positions.
- Convert pixel positions to millimeters.
- Produce synchronized position-versus-time data.
- Flag dropped frames and failed detections.
- Export CSV files.

**Module C: Physics analysis**

- Calculate individual particle trajectories.
- Separate common (symmetric) and relative (antisymmetric) motion.
- Perform Fourier and power spectral analysis.
- Estimate oscillation frequencies and amplitudes.
- Compare the measured spectrum with a one-particle control.
- Estimate persistence, spectral linewidth, and uncertainty.
- Compare results with the published theoretical model.

The initial software stack should use Python, NumPy, SciPy, OpenCV, Matplotlib, and optionally scikit-learn.

**Module D: Visualization**

Create an approachable interactive exhibit dashboard showing:

- Live or recorded bead positions.
- Slow-motion playback.
- Time-series graphs.
- Oscillation frequency spectra.
- An animated model of the physical system.
- An explanation of why the resulting motion is scientifically interesting.

The dashboard should distinguish actual measurements from simulation and illustrative animations.

## 4. Experimental methodology

### Experiment 1 — Establish acoustic levitation

Suspend a single EPS bead and measure its equilibrium position, stability, and response to changes in driving amplitude.

**Acceptance criterion:** The bead remains trapped long enough to perform repeatable measurements without uncontrolled drift.

### Experiment 2 — Establish two-particle coupling

Place two beads in neighboring acoustic nodes.

Measure their equilibrium positions and motion while varying the particle diameter combination.

**Acceptance criterion:** Both particles remain trapped and produce independently trackable trajectories.

### Experiment 3 — Find the active oscillation regime

Systematically vary bead size combinations under stable acoustic drive conditions.

Search for oscillatory behavior that persists without deliberate low-frequency forcing.

**Acceptance criterion:** Sustained oscillations are recorded and can be distinguished from camera artifacts, environmental vibrations, and externally imposed modulation.

### Experiment 4 — Test time-crystalline behavior

Use image tracking and spectral analysis to characterize the two-particle motion.

Evaluate whether the particles show the antisymmetric dynamical mode predicted by the research model, rather than only ordinary common-mode oscillation.

The published experiment observed characteristic collective motion near 67 Hz. Exact matching is not required because apparatus parameters can differ.

**Acceptance criterion:** Repeated measurements show a persistent antisymmetric spectral feature in the predicted regime, above the measurement noise floor, consistent with the published model.

### Experiment 5 — Controls and replication

Perform:

1. Single-particle measurements to establish a noise baseline.
2. Control pairs in a predicted non-time-crystalline regime.
3. Repeated experiments using the same particle pair.
4. Additional experiments using different pairs of comparable dimensions.
5. Checks for periodic variations in drive amplitude, supply power, illumination, and mechanical vibration.

**Acceptance criterion:** The observed behavior depends reproducibly on experimental particle parameters, and plausible alternative explanations have been investigated.

A visually striking oscillation by itself does not constitute scientific confirmation.

## 5. Data and documentation

Each experiment must produce:

- An experiment identifier and date.
- Particle dimensions and conditions.
- Instrument configuration and drive parameters.
- Original video footage.
- Particle tracking data.
- Analysis results and plots.
- Notes about unexpected behavior or failures.

All software should be version-controlled. Raw data should be preserved separately from derived results.

The published research data and notebooks should be used to validate our analysis pipeline before interpreting measurements from the new apparatus.

## 6. Planning budget

Approximate procurement allowances in Thai baht. These are preliminary planning ranges, not verified supplier quotations.

| Category | Allowance |
|---|---:|
| Levitator, electronic components, fabrication | ฿3,000–8,000 |
| Beads, mounts, lighting, calibration accessories | ฿1,000–3,000 |
| Camera and optical accessories, if purchased | ฿10,000–25,000 |
| Miscellaneous testing and contingency | ฿1,000–4,000 |
| **Estimated total** | **฿15,000–40,000** |

An existing suitable camera or borrowed equipment could reduce the budget substantially.

No expensive imaging equipment should be purchased before the two-bead levitation milestone.

## 7. Deliverables

The completed project should include:

- One operational acoustic levitation instrument.
- A tested electronics design and complete bill of materials.
- An experimental protocol.
- A documented collection of particle-pair trials.
- An open-source Python analysis pipeline.
- A visual dashboard suitable for public demonstration.
- A short scientific report comparing predictions and observations.
- A safety and operating guide.
- A public repository containing reproducible results where possible.

## 8. Milestones and decision gates

**Gate 1 — Research and design**

Review original apparatus details, inspect the released experimental data, finalize the circuit and frame design, and prepare a bill of materials.

**Gate 2 — Functional levitator**

Confirm repeatable single- and dual-bead levitation.

**Gate 3 — Instrumented experiment**

Demonstrate reliable particle tracking and quantitative frequency measurement.

**Gate 4 — Scientific replication**

Conduct controls and evaluate evidence for the target time-crystalline behavior.

**Gate 5 — Public exhibition**

Package the instrument, results, and explanatory visuals into a reproducible demonstration.

Each gate should have a documented pass/fail result. Failure to observe the time crystal must be reported as such rather than interpreted as proof from visual behavior alone.

## 9. Reference materials

1. [Morrell, Elliott & Grier, *Nonreciprocal Wave-Mediated Interactions Power a Classical Time Crystal*](https://arxiv.org/html/2504.15495) — Primary research, mathematical model, apparatus description, and experimental parameters. Published as [Phys. Rev. Lett. 136, 057201 (2026)](https://doi.org/10.1103/zjzk-t81n).
2. [Original TinyLev construction tutorial](https://www.instructables.com/Acoustic-Levitator/) — Frame, electronics, assembly instructions, and component specifications.
3. [Original research dataset and analysis files — OSF](https://osf.io/sx7ug/) — Reference recordings, tracking data, and analysis notebooks.

## 10. Project completion criteria

The project is successful as an engineering project if the apparatus reproducibly levitates and measures two interacting particles.

It is successful as a time-crystal replication only if quantitative evidence and control experiments support the particular emergent dynamical state described in the reference research.

The final demonstration should communicate both the physical phenomenon and the evidence supporting its interpretation.
<!-- stylecheck: allow-end -->
