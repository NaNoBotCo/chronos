# Hardware

## Levitator

Build the TinyLev from its kit or from the files in the supplement to Marzo, Barnes & Drinkwater, [Rev. Sci. Instrum. 88, 085105 (2017)](https://doi.org/10.1063/1.4989995). The supplement has the STL frame and the Arduino code. The design uses:

- 72 transducers, 36 on each side, 10 mm, 40 kHz;
- an Arduino Nano for the square waves;
- an L298N dual H-bridge to drive them.

The transducers see twice the driver's input voltage, peak to peak. They are rated to 20 Vpp, so the driver input stays at 10 V or less.

Match transducer polarity before gluing, as the TinyLev instructions describe. One reversed transducer weakens the trap.

## Drive adjustment

Put the LM2596 step-down board between the DC adapter and the L298N's power input:

```
9 V adapter -> fuse -> switch -> LM2596 (set 5-9 V) -> L298N +12V/GND
Arduino Nano  <- USB power (separate)
```

When the L298N runs below about 7 V, its own 5 V regulator sags. For that reason the Nano is powered from USB, not from the L298N's 5 V pin. Turn the LM2596 down to weaken the trap, and up to strengthen it.

Record the LM2596 output voltage for every run. During a principal run the drive stays constant.

## Bead gauge

`bead-gauge.scad` is a plate with 21 holes, 2.0 to 4.0 mm in 0.1 mm steps. A bead's size is the smallest hole it drops through.

Printers make small holes undersize. Print the gauge once and measure three holes with calipers. Then set `clearance` in the file so the printed holes match their labels, and print it again.

```bash
openscad -o bead-gauge.stl bead-gauge.scad
```

## Camera rig

Put the camera on a tripod, side-on to the levitator, with the black card behind the beads and the LED lamp lighting them from the front. Tape a ruler in the plane of the beads for scale. Film about 100 s at the phone's highest frame rate (240 fps is enough: the swing near 67 Hz needs at least 134 frames a second).
