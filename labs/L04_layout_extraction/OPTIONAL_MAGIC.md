# Optional extension: genuine layout extraction with Magic

**Status: not executed for this lab.** The shipped networks and results come from the analytical estimator and ngspice, not from this extension. No Magic executable, installed SKY130 technology, labeled `.mag` layout, DRC report or LVS report is bundled here.

## Required inputs

Use a compatible Magic build and a properly installed SKY130 PDK. Start Magic with the installed `sky130A.magicrc` (or the equivalent for your selected variant), not a raw source `.tech` file or a GDS-viewing-only configuration. The [Magic project-setup guide](https://www.opencircuitdesign.com/magic/howto.html) explains startup configuration. Pin the installation and record its revisions.

For a reproducible reference, the inspected open-pdks source revision was `c6df28c1fccb05c286aa0a15e9c4c7dcd8502607`. Its [unprocessed SKY130 technology source](https://github.com/fossi-foundation/open-pdks/blob/c6df28c1fccb05c286aa0a15e9c4c7dcd8502607/sky130/magic/sky130.tech) declares a Magic 8.3.693 requirement and contains installation-time macros. It is not a ready-to-use installed technology file. Do not assume a more recent source has the same tool requirement.

Create your own genuine native layout with legal met3 paths, reference/aggressor conductors, vias, contacts and terminals as appropriate. Match the analytical cases' intended connectivity and geometry, then document the differences required for an implementable layout. The supplied JSON and SVG files are not GDS or Magic layout databases. Check DRC, confirm connectivity with LVS where applicable, and label/order the intended ports.

## Extraction template

The accompanying `optional_magic_extract.tcl` targets the modern extraction commands documented on 6 November 2026. Before using it, inspect the extraction styles provided by your installed PDK and select the intended RC corner/style. The script deliberately has no guessed default style.

Launch a new Magic session with your installed PDK configuration and your chosen cell, in a separate working copy:

```sh
L04_CELL=/absolute/path/to/your_cell.mag \
L04_EXTRACT_STYLE=your_installed_extraction_style \
magic -dnull -noconsole -rcfile /absolute/path/to/sky130A.magicrc \
  optional_magic_extract.tcl
```

Paths and style are user-supplied placeholders. This command and template are an unexecuted extension, not a tested installation recipe for arbitrary Magic versions.

The template enables capacitance, mutual coupling and detailed resistance, disables the stated small-network cutoffs, and writes ngspice-oriented SPICE. Current [extract](https://www.opencircuitdesign.com/magic/commandref/extract.html), [extresist](https://www.opencircuitdesign.com/magic/commandref/extresist.html) and [ext2spice](https://www.opencircuitdesign.com/magic/commandref/ext2spice.html) documentation must match the installed version. The resistance threshold/minimum use **milliohms**; the delay threshold uses **picoseconds**. Older `extresist tolerance` recipes should not be assumed effective in current releases.

## Check the result before simulation

Compare subcircuit port order with the testbench. Check that both ends of the signal are retained as physical nodes and that reference and aggressor remain separate. Inspect total resistance, ground capacitance and mutual capacitance against hand estimates. Do not silently ground an aggressor or a floating conductor to make simulation easier.

The current Magic reference states that ground capacitance is distributed over resistance-network nodes, while each coupling term connects to one node on each coupled net rather than being spatially distributed. Evaluate whether that representation is adequate for your experiment. Numerical agreement with a lumped estimate cannot establish spatial coupling accuracy.

Retain device models separately when needed, verify transistor/body parameters, and avoid double-counting intrinsic and extracted capacitances. Run the exported circuit in a new bench and map terminal/internal probes using the actual extraction output. Compare the same stimulus and reference at the same physical points. Record DRC/LVS outcomes, PDK/tool revisions, extraction settings and limitations alongside the waveform.

A successful tool run is not foundry signoff. Qualification and accepted tools/decks depend on the actual fabrication flow.
