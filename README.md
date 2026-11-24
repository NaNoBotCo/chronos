# Chronos: a tabletop time crystal

Two foam beads float in a 40 kHz acoustic levitator. When their sizes differ a little, they start swinging opposite ways on their own, at about 67 Hz, and the swing lasts. Mia Morrell, Leela Elliott and David Grier reported this in *Physical Review Letters* 136, 057201 (2026) as a classical continuous time crystal. Chronos lets you try it at home. It has four parts:

- a TinyLev-style levitator,
- a printed bead gauge,
- a fast phone camera,
- Python that turns video into a spectrum.

It is a classical time crystal, not a quantum one.

Play with the cartoon first: the "One you can build" toy on [Time Crystals, Drawn](https://nanobotco.github.io/time-crystals/#beads).

## Five rungs

| Rung | What you get | What it shows |
|---|---|---|
| 1 | One bead floats | The levitator works |
| 2 | Two beads in neighbouring spots | A two-bead platform |
| 3 | Video at 240 frames a second, 100 s, turned into heights | A working measurement |
| 4 | A lasting peak near 67 Hz in the opposite-ways motion, absent with one bead alone | **The time crystal** |
| 5 | The same result from more pairs, with the misses recorded | A result others can check |

Rungs 1 to 3 give you a working levitator. Rung 4 is the target. A striking wiggle on video does not count as rung 4.

## Parts

The full list, with sources, is in [`hardware/bom.csv`](hardware/bom.csv). In short:

- a TinyLev-design levitator kit (76 × 10 mm 40 kHz transducers, Arduino Nano, L298N driver, switch, 9 V adapter), about US$70–100;
- an adjustable LM2596 step-down board to set the drive;
- expanded-polystyrene beads, 2–4 mm;
- the bead gauge in [`hardware/bead-gauge.scad`](hardware/bead-gauge.scad);
- a matte black card and a flicker-free LED lamp;
- a phone that films 240 frames a second.

Wiring notes are in [`hardware/README.md`](hardware/README.md).

## Software

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
chronos simulate --d1 2.9 --d2 3.3
chronos track run.mp4 --scale 0.139 --out run.csv
chronos analyze run.csv --control single.csv --plot run.png
```

- `chronos/model.py`: a reduced two-bead model, built on the paper's trap and pair-force terms. Those terms alone never sustain a swing in this reduced form. The model therefore adds a fitted "wave memory": a delayed pull that switches on for size ratios near 1.13. Its numbers sit in the `Coupling` dataclass. For 2.9 + 3.3 mm it settles into a limit cycle at about 66 Hz, and it rings down for equal sizes and for a 1.5 ratio. It does not reproduce the paper's 66.8 / 66.6 Hz split. Treat it as a cartoon for planning, not as the paper's model.
- `chronos/track.py`: finds two bright beads on a dark background in each frame and writes heights in mm to CSV. It flags dropped frames and missed detections.
- `chronos/analyze.py`: splits the motion into together and opposite modes and computes a Welch spectrum of each. It reports peak frequency, linewidth and coherence time, and compares against a one-bead control.

Before trusting your own runs, run the pipeline on the published recordings at [OSF](https://doi.org/10.17605/OSF.IO/SX7UG). It should find the paper's 66.8 Hz opposite-ways peak.

## Bead pairs from the paper

The paper gives bead sizes as *ka* (wavenumber × radius, k = 732 rad/m). In diameters:

| Pair | Diameters (mm) | Reported behaviour |
|---|---|---|
| Exp 2, 8, 10 | 2.92 + 3.31 | time crystal, opposite-ways peak 66.8 Hz |
| Exp 6 | 3.01 + 3.20 | time crystal |
| Exp 4 | 2.81 + 3.33 | time crystal |
| Exp 1, 5, 7, 9 | 2.19 + 2.79 | oscillator (together mode) |
| Exp 3 | 2.02 + 2.79 | oscillator (together mode) |

Equal sizes never swing. Most random pairs sit still. The paper's model at a 1.5 size ratio rings down.

## Docs

- [`docs/PROTOCOL.md`](docs/PROTOCOL.md): the five experiments, the gates, what to record.
- [`docs/SAFETY.md`](docs/SAFETY.md): power, sound, hands.
- [`docs/SPEC.md`](docs/SPEC.md): the full build specification.

## Kit

Every part can be bought separately from the links in `hardware/bom.csv`. A ready kit (levitator kit, bead bag, step-down board, shipped from the makers) is offered on the [Time Crystals, Drawn](https://nanobotco.github.io/time-crystals/#build) page.

## Credits and licences

- Physics: Morrell, Elliott & Grier, [PRL 136, 057201 (2026)](https://doi.org/10.1103/zjzk-t81n), [arXiv 2504.15495](https://arxiv.org/abs/2504.15495).
- Levitator: Marzo, Barnes & Drinkwater, "TinyLev", [Rev. Sci. Instrum. 88, 085105 (2017)](https://doi.org/10.1063/1.4989995). Frame files and Arduino code come from that paper's supplement, under its terms.
- Code in this repository: MIT ([`LICENSE`](LICENSE)). Docs and hardware files: CC BY 4.0 ([`LICENSE-docs`](LICENSE-docs)).
