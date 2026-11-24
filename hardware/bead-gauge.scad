// Chronos bead gauge: 21 holes, 2.0 to 4.0 mm in 0.1 mm steps.
// A bead's size is the smallest hole it drops through.
// Print, measure three holes with calipers, set `clearance` so printed holes match their labels, print again.

clearance = 0.15;    // mm added to every hole; printers make small holes undersize
plate_t   = 2.0;     // plate thickness, mm
pitch     = 9.0;     // hole spacing, mm
cols      = 7;
rows      = 3;
margin    = 6.0;
label_h   = 0.6;     // engraved label depth

w = margin * 2 + pitch * (cols - 1);
h = margin * 2 + pitch * 1.6 * (rows - 1) + 4;

function size_at(i) = 2.0 + 0.1 * i;
// "2.0", "2.1" ... "4.0": OpenSCAD prints 2.0 as "2", so build the label by hand
function label(i) = let(t = 20 + i) str(floor(t / 10), ".", t % 10);

difference() {
  cube([w, h, plate_t]);
  for (i = [0 : cols * rows - 1]) {
    c = i % cols;
    r = floor(i / cols);
    x = margin + c * pitch;
    y = h - margin - 2 - r * pitch * 1.6;
    translate([x, y, -1]) cylinder(d = size_at(i) + clearance, h = plate_t + 2, $fn = 64);
    translate([x, y - 4.6, plate_t - label_h])
      linear_extrude(label_h + 1)
        text(label(i), size = 2.2, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
  }
  translate([w / 2, h - 3.6, plate_t - label_h]) linear_extrude(label_h + 1)
    text("CHRONOS bead gauge, mm", size = 2.4, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
}
