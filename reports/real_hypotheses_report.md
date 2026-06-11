# Deterministic Real Hypotheses

These hypotheses are generated from the real-paper evidence corpus using deterministic templates. They are proposal candidates for audit, not validated research conclusions.

- Source corpus: `data\real_evidence_corpus.json`
- Hypotheses: `5`

## Candidates

### real:H001: Atmospheric plasma-assisted dry cathode interfaces for lower-impact manufacturing

Combining dry cathode processing with short-duration plasma surface activation will improve current-collector adhesion and cycling stability while reducing NMP solvent use and drying energy.

- Supporting claims: `real:C044_01, real:C086_01, real:C075_01`
- Contradicting/limitation claims: `real:C123_01`
- Evidence strength: `0.95`
- Novelty gap: `0.88`
- Feasibility: `0.56`
- Human validation need: `1.0`

**Proposed experiment:**

Fabricate NMC811 dry cathodes with PTFE binder and two carbon-black grades, apply 10-60 s atmospheric or low-vacuum Ar/O2 plasma before lamination, then compare adhesion, sheet resistance, tortuosity, particle cracking, rate capability, and capacity retention against untreated dry electrodes.

### real:H002: Water-compatible bio-derived binder systems for graphite anodes

A water-compatible hybrid of chitosan-derived self-healing chemistry and PHBV-like biodegradable binder design can retain graphite cycling stability while avoiding both PVDF/NMP and chlorinated-solvent processing.

- Supporting claims: `real:C096_01, real:C110_01`
- Contradicting/limitation claims: `real:C081_01`
- Evidence strength: `0.85`
- Novelty gap: `0.84`
- Feasibility: `0.7`
- Human validation need: `1.0`

**Proposed experiment:**

Prepare graphite anodes using aqueous chitosan/vanillin derivatives blended with PHBV-inspired biodegradable segments or waterborne PHBV dispersions. Benchmark against PVDF, pristine chitosan, and PHBV controls for adhesion, swelling, impedance, rate capability, capacity retention, and binder dissolution.

### real:H003: Circular natural-graphite anodes with bio-based conductive surface repair

Green-purified or regenerated natural graphite can recover high anode performance when paired with thin bio-derived carbon or conductive polymer coatings that stabilize SEI formation and electronic pathways.

- Supporting claims: `real:C107_01, real:C107_02, real:C099_01`
- Contradicting/limitation claims: `real:C110_01`
- Evidence strength: `0.95`
- Novelty gap: `0.88`
- Feasibility: `0.7`
- Human validation need: `1.0`

**Proposed experiment:**

Compare natural graphite, regenerated spent graphite, and synthetic graphite baselines after non-thermal plasma purification and tannic-acid-derived carbon coating. Measure purity, ICE, SEI impedance, reversible capacity, 2C cycling retention, and process energy/chemical burden.

### real:H004: Biomass-derived carbon additives for dry-processed cathode transport control

Functionalized biomass-derived carbons can serve as sustainable conductive/process additives in dry cathodes, improving ion-transport kinetics without increasing tortuosity as much as very high-surface-area carbon blacks.

- Supporting claims: `real:C081_01, real:C086_01, real:C075_01`
- Contradicting/limitation claims: `real:C044_01`
- Evidence strength: `0.95`
- Novelty gap: `0.88`
- Feasibility: `0.56`
- Human validation need: `1.0`

**Proposed experiment:**

Synthesize lignin-derived carbon additives with controlled surface chemistry, blend them into PTFE-based dry NMC cathodes, and compare calenderability, electrode tortuosity, charge-transfer resistance, particle cracking, and long-cycle retention against commercial carbon blacks.

### real:H005: Quality-controlled low-energy plasma synthesis for NMC cathode precursors

Stabilizing atmospheric microplasma synthesis with contamination-resistant reactor materials and downstream dry-electrode process controls can improve the viability of calcination-free NMC cathode fabrication.

- Supporting claims: `real:C123_01, real:C086_01, real:C044_01`
- Contradicting/limitation claims: `real:C075_01`
- Evidence strength: `0.95`
- Novelty gap: `0.88`
- Feasibility: `0.56`
- Human validation need: `1.0`

**Proposed experiment:**

Run a design-of-experiments study varying plasma waveform, electrode material, gas mixture, and precursor feed rate, then fabricate standardized dry cathodes to compare phase purity, Fe contamination, particle size, initial capacity, impedance, and 100-cycle retention.
