# CellForge AI Human Validation Checklist

This checklist is the gate between an evidence-backed research proposal package and a manuscript draft. Do not treat extracted claims as publication-ready until a human validates them against the source PDFs.

## Summary

- **items:** `10`
- **critical:** `3`
- **high:** `2`
- **medium:** `5`
- **low:** `0`
- **lead_hypothesis_id:** `real:H003`
- **manuscript_gate:** `only validated items with allowed_in_manuscript=true should be used in manuscript drafting`

## Priority Queue

### val:001 | CRITICAL | real:C099_01

- **Source paper:** `real:P099` A green route based on pi-pi interactions to coat graphite for high-rate and long-life anodes in lithium-ion batteries
- **Extraction file:** `099_green_graphite_coating.json`
- **Hypotheses:** `real:H003`
- **Roles:** `supporting`
- **Location:** Page 1, Abstract / Page 4, Section 3.2
- **Metric:** capacity retention = `89%`
- **Condition:** 500 cycles at 2C rate, EC:DMC:EMC (1:1:1 vol%) + 1% VC electrolyte
- **Claim:** The carbon-coated graphite (G@C) prepared via a green tannic acid/formaldehyde self-assembly process achieves a higher specific capacity and stability during long-term cycling, retaining 89% capacity after 500 cycles at 2C.
- **Citation text:** After 500 cycles at 2C, the specific capacity of G@C was 103.7 mAh g^-1, with a retention of 89%. However, G exhibited only 68.7 mAh g^-1 and 85% retention under identical conditions.
- **Limitation/risk:** The initial Coulombic efficiency (ICE) of G@C drops to 84.64% compared to 87.15% for pristine graphite.
- **Review reason:** Specific rate capability values at individual rates (such as 3C and 5C) in Fig. 3c and Li+ diffusion coefficient trends in Fig. 4e are represented only in charts and require manual digitization for exact numerical values. At least one figure/table requires manual digitization or visual verification. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 1, Abstract / Page 4, Section 3.2.
- Does any chart-derived value need manual digitization before it is quoted numerically?

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:002 | CRITICAL | real:C107_01

- **Source paper:** `real:P107` Natural graphite in making ecofriendly lithium-ion batteries: Challenges, current status, and future outlooks
- **Extraction file:** `107_natural_graphite_ecofriendly.json`
- **Hypotheses:** `real:H003`
- **Roles:** `supporting`
- **Location:** Page 17, Section 4.1.7
- **Metric:** carbon purity = `exceeding 99.99%`
- **Condition:** Low bulk temperature, non-thermal plasma activation
- **Claim:** Non-thermal plasma (NTP) treatment serves as a chemical-free, low-temperature, and highly energy-efficient purification method capable of upgrading natural graphite purity to over 99.99%.
- **Citation text:** It has been reported that NTP treatment can significantly enhance graphite purity to levels exceeding 99.99%, simultaneously reducing oxygen- and sulfur-containing surface functional groups.
- **Limitation/risk:** High equipment cost and difficulty in scaling up for large volume powder processing.
- **Review reason:** This is a review paper where key performance metrics and claims are synthesized from various third-party primary research papers (e.g., studies by Miao et al. and Lu et al.), rather than representing a single internal experimental study. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- If this is review-derived evidence, can the primary source be identified before manuscript use?
- Check the cited location: Page 17, Section 4.1.7.

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:003 | CRITICAL | real:C107_02

- **Source paper:** `real:P107` Natural graphite in making ecofriendly lithium-ion batteries: Challenges, current status, and future outlooks
- **Extraction file:** `107_natural_graphite_ecofriendly.json`
- **Hypotheses:** `real:H003`
- **Roles:** `supporting`
- **Location:** Page 24-25, Section 6
- **Metric:** reversible capacity = `353 mAh/g`
- **Condition:** 0.1C charge/discharge rate, coated with conductive HOS-PFM polymer
- **Claim:** Spent graphite regenerated using a conductive polymer coating (HOS-PFM) achieves a high reversible capacity of 353 mAh/g at 0.1C with a Coulombic efficiency of 99.93% and improved capacity retention.
- **Citation text:** the polymer-coated graphite anode exhibited a reversible capacity of 353 mAh/g at 0.1C, compared to 342 mAh/g for uncoated regenerated graphite.
- **Limitation/risk:** Conductive polymer coating adds manufacturing steps and polymer costs to the recycling process.
- **Review reason:** This is a review paper where key performance metrics and claims are synthesized from various third-party primary research papers (e.g., studies by Miao et al. and Lu et al.), rather than representing a single internal experimental study. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 24-25, Section 6.

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:004 | HIGH | real:C110_01

- **Source paper:** `real:P110` Poly(hydroxybutyrate-co-hydroxyvalerate) as a biodegradable binder in a negative electrode material for lithium-ion batteries
- **Extraction file:** `110_biodegradable_phbv_binder.json`
- **Hypotheses:** `real:H002, real:H003`
- **Roles:** `contradicting, supporting`
- **Location:** Page 3, Section 3
- **Metric:** capacity retention = `99.1 %`
- **Condition:** Graphite anode with 10 wt% PHBV binder, cycled at 36 mA/g over 100 cycles
- **Claim:** Biodegradable PHBV can successfully substitute PVDF as a binder for graphite anodes in lithium-ion batteries, delivering highly stable cycling with a specific capacity of 357 mAh/g and 99.1% capacity retention after 100 cycles.
- **Citation text:** The specific capacity of TIMREX_PHBV electrode material was 357 mAh/g after 100 cycles. ... with the capacity retention of 99.1 % after the 100th cycle. On the basis of the presented results, it may be concluded that the PHBV binder is resistant to dissolution or decomposition in the electrolyte...
- **Limitation/risk:** The processing required chloroform (CHCl3) solvent, and the polymer has lower adhesion to copper than PVDF.
- **Review reason:** The green binder (PHBV) slurry requires a chlorinated solvent (chloroform) rather than a green water-based solvent system, representing a critical processing trade-off. Additionally, key rate capacity comparison values in Fig. 3 require manual digitization. At least one figure/table requires manual digitization or visual verification. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 3, Section 3.
- Should this limitation change the hypothesis wording, experiment plan, or risk controls?
- Does any chart-derived value need manual digitization before it is quoted numerically?

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:005 | HIGH | real:C075_01

- **Source paper:** `real:P075` High-energy density ultra-thick drying-free Ni-rich cathode electrodes for application in Lithium-ion batteries
- **Extraction file:** `075_drying_free_ni_rich_cathode.json`
- **Hypotheses:** `real:H001, real:H004, real:H005`
- **Roles:** `contradicting, supporting`
- **Location:** Page 1, Abstract / Page 3, Section 1
- **Metric:** capacity retention = `77.7 %`
- **Condition:** Ultra-thick loading (~30 mg cm^-2), 1C cycling, half-cell vs. Li
- **Claim:** The solvent-assisted binder (SaB) dry process using a minimal quantity of ethanol (<3 wt.%) enables the production of ultra-thick Ni-rich cathodes without active material particle fracture, achieving higher capacity retention (77.7% after 100 cycles at 1C) compared to standard solvent-free dry methods.
- **Citation text:** Over 100 cycles at 1C, the SaB dry electrode achieves 77.70% capacity retention, surpassing the standard dry electrode's 72.39% at a loading of approximately 30 mg cm-2 and is also capable of performing at ultra-high loadings up to 60 mg cm-2.
- **Limitation/risk:** High tortuosity still limits performance at high discharge rates.
- **Review reason:** The rate-capability performance metrics at varying rates (e.g., 0.2C, 0.5C) are represented in graphs in Fig. 4d and require manual digitization for exact decimal values. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 1, Abstract / Page 3, Section 1.
- Should this limitation change the hypothesis wording, experiment plan, or risk controls?

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:006 | MEDIUM | real:C044_01

- **Source paper:** `real:P044` Solvent-free processing of lithium-ion batteries via plasma treatment of electrodes for adhesive interfaces
- **Extraction file:** `044_solvent_free_plasma_processing.json`
- **Hypotheses:** `real:H001, real:H004, real:H005`
- **Roles:** `contradicting, supporting`
- **Location:** Page 4, Section 3.2
- **Metric:** adhesion strength = `~2.8 N/cm`
- **Condition:** 30 s Ar plasma treatment (450 V DC, 3-4 mA), hot pressed at 150 C and 1.6 MPa
- **Claim:** Argon plasma surface treatment of dry-rolled PTFE-containing electrode sheets successfully creates oxygen-containing functional groups on the PTFE surface, increasing its adhesion strength to aluminum foil to ~2.8 N/cm and enabling stable dry-processed cathode operation.
- **Citation text:** as shown in Fig. 3(a), the adhesive strength between the plasma-treated PTFE and aluminum foil was ~2.8 N/cm, which was confirmed to be sufficient and equivalent to that between the plasma-treated PTFE and other materials reported in previous studies
- **Limitation/risk:** The processing current was limited to 3-4 mA, and the setup operates under vacuum conditions.
- **Review reason:** Specific rate capability values in Fig. 4(c) are plotted in a chart and cannot be read with 100% exact numerical precision from the text, requiring manual digitization. At least one figure/table requires manual digitization or visual verification. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 4, Section 3.2.
- Does any chart-derived value need manual digitization before it is quoted numerically?

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:007 | MEDIUM | real:C081_01

- **Source paper:** `real:P081` Comparative thermo-electrochemical study of lignin- and starch-derived carbon electrodes modified with Zn(TFSI)2 and ionic liquids for lithium-ion battery applications
- **Extraction file:** `081_lignin_starch_thermo_electrochemical.json.json`
- **Hypotheses:** `real:H002, real:H004`
- **Roles:** `contradicting, supporting`
- **Location:** Page 2, Section 1 (Introduction) and Page 8, Table 2
- **Metric:** activation energy = `15.3 kJ mol^-1`
- **Condition:** Carbonized lignin at 900 C modified with Zn(TFSI)2 under hydrothermal conditions at 140 C for 24 h
- **Claim:** Hydrothermal modification of kraft lignin-derived carbon using Zn(TFSI)2 significantly enhances lithium-ion transport kinetics and decreases charge-transfer resistance by introducing active zinc-ion and sulfonyl coordination sites, resulting in an exceptionally low activation energy of 15.3 kJ/mol.
- **Citation text:** Notably, the Zn(TFSI)2-modified lignin-based carbon (LKN2H) exhibited the most favorable electrochemical properties, including the highest ionic conductivity and the lowest charge transfer resistance. This enhancement is attributed to the introduction of sulfonyl and Zn2+ coordination sites that facilitate ion transport.
- **Limitation/risk:** The efficacy is heavily dependent on the biopolymer precursor chemistry, as starch-derived carbons did not exhibit comparable kinetic improvements.
- **Review reason:** High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 2, Section 1 (Introduction) and Page 8, Table 2.

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:008 | MEDIUM | real:C086_01

- **Source paper:** `real:P086` Effect of carbon black properties on dry electrode processing of cathodes for lithium-ion batteries
- **Extraction file:** `086_carbon_black_dry_electrode_processing.json`
- **Hypotheses:** `real:H001, real:H004, real:H005`
- **Roles:** `supporting`
- **Location:** Page 1, Abstract / Page 9, Section 3.4
- **Metric:** capacity retention = `94 %`
- **Condition:** PTFE dry-coated cathode with 2 wt% LITX®MAX90, cycled at C/2 in single-layer pouch cells
- **Claim:** Dry-processed NMC811 cathodes utilizing carbon blacks with small primary particle sizes and high specific surface areas (such as LITX®MAX90) exhibit high mechanical compressibility and provide a cushion effect that mitigates active material particle cracking during calendering, resulting in exceptional long-term cycling stability (94% retention after 450 cycles).
- **Citation text:** Aging tests revealed a capacity retention of 94 % after 450 cycles at C/2 for the best additive but also as a process aid for the calendering step, influencing the compressibility of the composite granules, resulting in adapted process parameters.
- **Limitation/risk:** The high surface area of these carbon blacks increases electrode ionic tortuosity and can promote secondary parasitic reactions.
- **Review reason:** Specific numerical values in Fig. 6 (Minimum carbon black content vs CB type) are only presented in a chart and require manual digitization, and key trade-offs between electronic conductivity and ionic tortuosity are evaluated from multiple figures. At least one figure/table requires manual digitization or visual verification. High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 1, Abstract / Page 9, Section 3.4.
- Does any chart-derived value need manual digitization before it is quoted numerically?

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:009 | MEDIUM | real:C096_01

- **Source paper:** `real:P096` Self-healable chitosan-based polymer binder for anode in lithium-ion batteries
- **Extraction file:** `096_chitosan_binder_anode.json`
- **Hypotheses:** `real:H002`
- **Roles:** `supporting`
- **Location:** Page 1, Abstract
- **Metric:** capacity retention = `81 %`
- **Condition:** 0.5C cycling rate over 250 cycles
- **Claim:** Both coin and pouch cells fabricated with the bio-based binder achieved a specific capacity of 161.2 mAh g-1 and retained 81 % of their capacity after 250 cycles.
- **Citation text:** Both coin and pouch cells fabricated with the bio-based binder achieved a specific capacity of 161.2 mAh g-1 and retained 81 % of their capacity after 250 cycles.
- **Limitation/risk:** The dense network slightly limits the free volume for Li-ion transport.
- **Review reason:** High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 1, Abstract.

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript

### val:010 | MEDIUM | real:C123_01

- **Source paper:** `real:P123` One-step atmospheric microplasma synthesis of an NMC-type lithium-ion battery cathode
- **Extraction file:** `123_ One-step atmospheric microplasma synthesis of an NMC-type lithium-ion.json`
- **Hypotheses:** `real:H001, real:H005`
- **Roles:** `contradicting, supporting`
- **Location:** Page 1, Abstract
- **Metric:** synthesis time = `< 1 s`
- **Condition:** Hollow-tube microplasma reactor, Ar and O2 carrier gases, liquid acetate precursor vapor, 3000 V at 25 kHz
- **Claim:** One-step atmospheric microplasma synthesis can produce crystalline, electrochemically active NMC-type lithium-ion battery cathode particles in less than one second without requiring an additional calcination step.
- **Citation text:** This communication aims to highlight a nascent yet novel synthesis route: a one-step atmospheric microplasma process for synthesizing cathode particles in less than one second... all—without requiring an additional calcination step.
- **Limitation/risk:** Low discharge capacity (125 mAh/g) and contamination from electrode sputtering
- **Review reason:** High-value performance metrics and claims should be verified before use in a research brief.

**Validation questions:**
- Does the source PDF support the exact claim text without overstatement?
- Do the metric, value, condition, and page/section match the source PDF?
- Is the citation text a faithful excerpt or close paraphrase of the paper?
- Check the cited location: Page 1, Abstract.

**Checklist:**
- [ ] PDF text supports claim
- [ ] Metric/value/condition verified
- [ ] Page or section verified
- [ ] Citation text corrected if needed
- [ ] Contradiction/risk reflected in hypothesis wording
- [ ] Allowed in manuscript
