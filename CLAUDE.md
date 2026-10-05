# Project Identity

**voltage_glitch** — compiles fault-injection research (`docs_pdf/`) into engineering
recommendations, a bill of materials, and schematics for an **RP2350-based voltage glitcher**
targeting **STM32**, plus an **EMFI-injector** extension. Type: **documentation & hardware-design —
no source code**. Deliverables: French Markdown in `docs/`, PNG schematics in `assets/schemas/`,
datasheets in `datasheet/`. The board is family-agnostic (glitch output selectable VDD or VCAP).

## Core Principles

- **Five provenance labels, always visible.** `[corpus]` = sourced from a `docs_pdf/` PDF (cite
  file + page); `[ref]` = external public source (cite the URL); `[reco]` = my engineering
  recommendation; **`[fait]`** = **measured on the real bench** (cite the date **and** the log file
  inside the archive); **`[fw]`** = **read in a firmware's source** (cite file + line). Never let a
  `[reco]`/`[ref]` read as if it were `[corpus]`.
  ★ **`[fait]` outranks `[corpus]`** — a first-hand measurement on the actual part beats a paper
  about a different part. ⚠ But **a `[fait]` derived from a software readout is only as solid as the
  decoding that produced it**: the bench's raiden board was labelled `[fait]` "RP2350B/QFN-80" from
  `PACKAGE_SEL`, and the silkscreen plus the Pico 2 W datasheet later proved it an **RP2350A**
  (firmware misreads `package_sel`). Prefer a measurement whose *instrument* is independent.
  ⚠ **`[fait]` is never assumed from a model.** Anything produced by SPICE/scipy is `[reco]`, even
  when two independent solvers agree — *concorder n'est pas être juste*.
- **Verify before stating** — component specs against `datasheet/`, RP2350 against the official
  brief/datasheet, external claims via WebSearch/curl. **Never from memory in a BOM or schematic.**
- **Invent no parameters.** Any glitch value (voltage/width/offset/success) not sourced is marked
  **"à caractériser"**.
- **`docs_pdf/` is read-only** — never modify or reorganize it *unless the user explicitly asks*
  (then validate before deleting; see Working Protocols).
- Correctness > completeness > brevity.

## Routing & Delegation

- **Direct**: single-doc edits, count/label fixes, one schematic regen, a targeted extraction whose
  location you already know.
- **Delegate to sub-agents** (keep main context clean): reading/extracting across many PDFs, a
  multi-paper analysis, broad corpus sweeps. Give each agent a precise extraction target and have it
  return **page-cited facts**, not prose.
- **Ask the user first**: destructive actions (deleting/overwriting in `docs_pdf/` or elsewhere),
  scope expansions (integrating newly-added sources, restructuring), or a genuine design fork.

## Operational Protocols

- Run independent extractions/renders **in parallel**; sequence only true dependencies.
- **Call the advisor** before committing to an approach and before declaring a multi-step task done;
  make the deliverable durable (write the file) *before* the advisor call.
- Give a **brief status update** before each major step, and lead every wrap-up with the outcome.
- On session/context limits, checkpoint progress rather than stopping after a plan.

## Working Protocols

- **Corpus extraction**: delegate PDF reading to sub-agents. Scanned/image PDFs (`pdftotext` returns
  nothing) → read via the image-rendering `Read` tool, page by page.
- **User-added corpus files**: the user sometimes drops new PDFs into `docs_pdf/` mid-task. On
  noticing (e.g. the file count changed), **identify them and offer to integrate** — never silently
  ignore, never silently rework docs. Re-check the corpus count after any change.
- **Schematics**: edit the generators in `assets/schemas/src/` (`gen_schemas.py`/schemdraw, `*.dot`/
  graphviz), run `assets/schemas/src/generate.sh` to regenerate the PNGs **in place** (same path so
  doc embeds keep working), then **visually inspect** each PNG before declaring done.
- **Datasheets**: `curl` official manufacturer URLs; **validate `%PDF` magic bytes** + a plausible
  page count. If a host blocks curl (e.g. `analog.com`), use a reachable mirror (archive.org) and
  note the substitution in `datasheet/README.md`.
- **Cross-doc consistency**: when a component or fact changes, update **every** doc that references
  it (BOM, architecture diagram, schematic ASCII + netlist, regenerated PNG) and the `datasheet/`
  index in the same pass — then grep for stale mentions (old part names, counts).

## Documentation Standards

- Docs are **French** with correct accents; this `CLAUDE.md` and `README` links stay as-is; never
  translate `docs_pdf/` filenames.
- Numbered doc set `docs/NN_*.md` (00 synthèse … 06 EMFI); keep the numbering and the cross-links.
- Sourced docs (`00`, `03`, `04`, `06`) carry `[corpus]` + page cites; recommendation docs (`01`,
  `02`, `05`) are labelled `[reco]`/`[ref]`. Each doc states its provenance in its header.
- Only `README.md` and `CLAUDE.md` may be `.md` at the project root; every other `.md` → `docs/`.

## Quality Gates

- `[corpus]` vs `[ref]` vs `[reco]` vs `[fait]` vs `[fw]` boundary explicit; page, URL, date+log
  or file+line on every sourced claim. **A doc that uses `[fait]`/`[fw]` must define them where a
  reader will meet them** — in its header, or in the opening block of the section that uses them
  (the `knowledge_base/` pattern). They are never assumed known.
- **Corpus count never moves for a bench measurement.** `[fait]`/`[fw]` material is not a
  `docs_pdf/` PDF: adding it leaves the count at **68**. (The 59→68 jump came from *published PDFs* —
  the Werner thesis plus 8 papers mined from its bibliography — not from any bench measurement.)
- Component specs traceable to `datasheet/` (or flagged "à vérifier").
- PNG links resolve (`../assets/schemas/…`); regenerated PNGs visually verified.
- Downloaded PDFs: `%PDF` header + plausible page count.
- French orthography/accents throughout `docs/`.
- Corpus count consistent across `docs/00`, `docs/01`, `docs/04`, `docs/06`, `README`, and this file.
- `docs_pdf/` unchanged unless the user asked for a specific edit.

## Load-bearing facts (do not re-derive)

These prevent concrete mistakes; the full sourced detail lives in the `@import`ed docs.

- **IRLML6402 is P-channel** → load switch only, **never the crowbar**. Crowbar default = **AO3400A**
  (N-channel, verified); VN2222 = historical ref, IRLML2502 = alt.
- **PIO tick (6.67 ns @150 MHz) is command resolution, not glitch width** (floor set by MOSFET +
  gate drive + PCB parasitics). Never sell it as glitch resolution.
  ★ **Now demonstrated in firmware source, not just argued** `[fw]` (`docs/07` §9septies):
  `glitch.c:376-378` does `if (w > 5) w -= 5;` while `glitch.pio:92-104` holds the pad high for
  **`W + 3` cycles** ⇒ **`WIDTH` 6–9 deliver strictly LESS than `WIDTH` 5**, and `WIDTH` 10 merely
  equals it. A naive 0→15 sweep is **non-monotonic**. Real minimum = **3 cycles ≈ 20 ns** (the
  raiden README's "6.67 ns" was wrong). Two floors, and only the second bounds a sweep:
  **instrumental 133 ns** vs ★ **useful ≈ 673 ns** (where the rail actually crosses `VPDR`).
- ★★ **Three RP2350 hardware defects that hit THIS project's own board** (`docs/01`/`02`/`05`):
  (1) **Erratum RP2350-E9** — *official*, in `datasheet/RP2350_RaspberryPi.pdf` §RP2350-E9, **not a
  forum**: a Bank-0 pad **configured as an input** whose voltage sits in the undefined logic region
  leaks *"typically around **120 µA**"* and **holds the pad near 2.2 V**; the internal pull-down is
  **too weak to overcome it**. ⚠ **Announced on stepping `RP2350 A2`**, with fixed silicon
  mentioned — **check the stepping**. ⇒ a crowbar gate needs a **mandatory pull-down of 1 kΩ**,
  mounted on the MOSFET board between gate and source, **not the reflex 10 kΩ**: 120 µA × 1 kΩ =
  0.12 V (well under AO3400A `V_GS(th)` min 0.65 V) vs 120 µA × 8.2 kΩ = 0.98 V, which turns it
  **on**. ⚠ The datasheet's own *"8.2 kΩ or less"* advice targets **`V_IL`, not a power gate**. (2) **The RP2350 ADC has no internal reference — it uses
  its own supply**; on Pico 2 W `ADC_AVDD` comes from the SMPS through an **R-C 201 Ω / 2.2 µF** and
  the ADC draws ~150 µA ⇒ a structural **~30 mV offset**, so `ADC_VREF = rail − 30 mV` and **an
  input on the raw 3.3 V rail reads 4095 with σ = 0** (Pico 2 W datasheet RP-008304-DS-3 §3.3).
  (3) **The glitch node swings below 0 V — to −2.37 V** without drain damping, against an RP2350 I/O
  absolute max of **−0.3 V** ⇒ **1 kΩ in series on every ADC input on that node, fitted first**
  (internal clamp then takes ~1.7 mA). ⚠ **Never a capacitor there** — 1 nF = 1 µs time constant,
  which kills `TRACE` at 500 ksps.
  ⚠ Also: `adc_gpio_init()` **latches the pin HIGH** (4092 σ=7.9 before a `TRACE`, **4095 σ=0.00**
  after, released only at reboot) ⇒ **all ADC measurement must precede the session's first
  `TRACE`**. And a Pico 2 W's `3V3` output is rated **< 300 mA**: grounding the node through 9.4 Ω
  draws **351 mA** and trips the SMPS, dropping both boards off USB.
- ★ **`R_damp` — drain damping — is a real component, not a refinement.** With a modern low-`R_on`
  MOSFET the crowbar mesh is strongly under-damped. Rule: **`R_damp ≈ Z0 = √(L_loop / C_resid)`**
  (0.15 Ω at 10 µF · **0.47 Ω at 1 µF** · 1.2 Ω at 100 nF) ⇒ it is chosen **after** `C_resid` is
  measured. ⚠ The convenient `τ = R_on × C` model **does not transport** — it only worked on the
  IRLML0060 by coincidence (`R_on ≈ Z0`). And shortening the loop is **not** a substitute: 10 cm →
  3 cm (150 → 30 nH) moves `ζ` from 0.05 to 0.055 only. `[reco]`, cross-checked by ngspice to 0.7 %.
- ⚠ **`Rs` is measured, never chosen** (`docs/05` §4). Between ~2 and ~22 Ω the floor is **always
  far below `VPDR`**, so depth is never the limiting factor; what decides is the rail's **residual
  capacitance**, via `C_resid = τ_rise / R_series`. `C_resid ≲ 1 µF` ⇒ **10 Ω**; `≳ 5 µF` ⇒ **4.3 Ω**
  plus strip more capacitors; **above 22 Ω, don't**. Hard ceiling: `3τ ≪ TPW = 300 µs`.
  ⚠ **`3.3/R_series` is a STEADY-STATE current, not a peak** — the real LC-mesh peak is **≈ 8 A**,
  which is what decides the MOSFET (AO3400A `I_DM` 30 A pulsed vs IRLML0060 1.2 A continuous).
- **Voltage-glitch fault model = set/reset (stuck-at), not bit-flip**; **EMFI = sampling faults**
  (bitset/bitreset, local, polarity-dependent).
- **Voltage glitch is the primary vector on STM32** (the PLL defeats clock glitching unless HSE boot).
- Reference paper = **Bozzato, *Shaping the Glitch* (TCHES 2019)**; EMFI 1 kV reference =
  **SiliconToaster**; EMFI x86 reference = **Fraunhofer, *EM-Fault It Yourself*** (`2209.09835v1.pdf`).
  Corpus = **68 papers** (37 original + **12 mined from the corpus's own
  bibliographies** + **10 from the curated `dev-zzo` gist** + **1 PhD thesis — Werner, HAL
  `tel-03719660`, VERIMAG 2022 — added directly** + **8 mined from its bibliography**, `docs/04`
  §A/C/E/I). Counted sections in `docs/04` are
  **A–G + I**; **H** (6 video talks) and **J** (27 web write-ups) are `[ref]` and **not counted**.
- **The crowbar is no longer un-sourced.** O'Flynn, *Fault Injection using Crowbars on Embedded
  Systems* (ePrint 2016/810, `2016-810.pdf`) is the root reference for Bloc B — it predates Bozzato by
  3 years and states a simple microcontroller suffices to drive the MOSFET (p. 8). **`Rs` is still
  unquantified** by both papers → stays "à caractériser". Only the **RP2350 itself** remains outside
  the corpus — its **PIO no longer does** (see the GD32/OFFZONE entry below).
- **`docs_pdf/writeups/` is `[ref]`, never `[corpus]`.** 27 practitioner write-ups converted to PDF
  by us. **Their pagination is an artefact of our conversion** → cite them **by URL, never `p. N`**,
  and never count them in the 59.
- **VCAP is no longer an inference — on STM32.** Anvil Secure (`[ref]`,
  `docs_pdf/writeups/STMicro_STM32F401CC_…`) states it soldered to **`VCAP_1`** and desoldered the
  bypass capacitors on a STM32F401CC. `docs/03` §2.2/§3.4. It **confirms a practice**; the exact pinout
  still varies by package. **It is no longer the only write-up naming a core rail** — see nRF52 below,
  so never write "the only document to name the injection rail" unqualified.
- **nRF52 (LimitedResults ×2, `[ref]`, read in full) — the second named core rail, and a target with
  NO bootROM.** Injection point is **`DEC1`** (*"definitively the CPU power line"*, 0,8–0,9 V on
  nRF52840); `DEC4` is the trigger. Because there is no bootROM, AP init is **pure hardware** ⇒ the
  window is **not code**, cannot be disassembled, and is found **only by power analysis**. Decoupling
  removed **then a 100 nF re-soldered** — a third position in the decoupling debate.
  ⚠️ **Only nRF52840 / 52832 / 52833 were actually glitched.** The six-part vulnerable list (incl.
  **nRF52820**) carries a **Nordic claim**, not a measurement — and **no CVE exists**.
  ★ **nRF52820 has two protection regimes** (official PS v1.3 §4.8.2, archived in
  `datasheet/cible_nRF52820/`): *build codes* `Cxx`- = hardware only, **default open** (the glitched
  regime); `Dxx`+ = hardware **and** software, **default closed**, needing `UICR.APPROTECT=HwDisabled`
  **and** firmware `APPROTECT.DISABLE=SwDisable` ⇒ **two faults**. The regime is read on the package
  via the `<H>` letter — the `-D` order-code suffix is **not** marked on the die. `<H>` (§4.8.2) and
  `<VV>`=`AA-D` (Table 144) are **two identifiers the PS never links** → `[reco]`.
  ★ This gives the `docs/07` fail-safe hypothesis **one precedent each way** (Cxx fails open, Dxx+ was
  redesigned closed) — it stays `[reco]`; **write both branches or neither**.
  ★★ **Best concrete target = a Logitech CU0021 USB dongle** (`docs/08` §1bis) — the **only one whose
  regime is read, not assumed**. Marking `N52820 / QDAACA / 2011AA` decoded off the **FCC internal
  photos** (FCC ID `JNZCU0021`, Bureau Veritas 200615E03): `<H>`=**C** ⇒ **regime A, one fault**;
  `<PP>`=**QD** ⇒ **QFN40, `DEC1` = pin 1**, hand-solderable; produced **week 11 / 2020**.
  ⚠️ That is the **unit the lab photographed** — always re-read `<H>` on the actual part.
  ⚠️ A USB dongle is probably in **High Voltage mode** (`VDDH` only) ⇒ do **not** blindly tie
  `VDDH` to `VDD`; probe first.
  ★ **Second concrete target = a Logitech Signature M650 / M650 L mouse** (`docs/08` §1ter). The nRF52820 is
  attested `[ref]` by iFixit **on the Signature variant only** — the **M650 L teardown names no part
  at all**, so never state the L's MCU as established. Package type (QFN40 vs WLCSP) is **undocumented**
  ⇒ default plan is the **`DEC1` decoupling cap on the PCB**, not the pin. Launched **Jan 2022**, i.e.
  after both hardening milestones ⇒ **probably `Dxx`**; the compensation is the **~40 $ price**, so buy
  several units and read `<H>` on each.
- **The PIO is now `[corpus]`, the RP2350 is not.** The GD32/OFFZONE deck (sl. 35-38) uses an
  **RP2040 + PIO** because USB gives *« large floating delays »* — but for **synchronised SWD+NRST**,
  **not** to generate a glitch. Never inflate this into RP2350 sourcing.
- **A crowbar is not the only topology.** Gerlinsky (origin) and chip.fail glitch with a **MAX4619
  analog MUX** switching the rail between two levels — that is how chip.fail broke a **STM32F2**.
  `docs/05` §4.2.
- **Never budget a multi-glitch by multiplying single-glitch rates**: *Fill your Boots* measures
  **0,0001 %** where the product predicts 0,0036 % (3-stage pipeline, p. 13). A STM32 is also a
  3-stage Cortex-M.
- **The GD32/OFFZONE deck's own voltage glitcher FAILS** (sl. 57). Its three vulnerabilities are
  **race conditions, not FI**. Never cite it as a successful FI attack.
- **Two factual corrections already applied — do not reintroduce them**: Trouchkine (JCEN 2021)
  targets the **BCM2837 / Raspberry Pi 3 bare-metal**, *not* an Intel Core i3 under Linux (the x86
  work is WISTP 2019, `[ref]`); and *Controlling PC on ARM* (FDTC 2016) is **in** the corpus now — as
  the **deck**, not the paywalled IEEE paper.
- **Decks cite `sl. N`, papers cite `p. N`.** `woot17-paper-cui.pdf` (BADFET) has **no printed page
  numbers** → cite the PDF page index.

### First concrete target: Cmsemicon **BAT32G135** (`docs/07`) — **now a MEASURED target**

- ★★★ **This target has been on a real bench (2026-08-31 → 09-07). `docs/07` is no longer a plan,
  it is a campaign report** — read §0bis, §2bis and **§2ter** before anything else. The physical
  part is a **TP-Link Tapo T310** sensor. Artefacts (dumps, logs, the raiden fork, the host tooling)
  live **only** in `tplink_tapo-20260909.tgz` (md5 `710552fd8478250644d69eb233fddb1e`) — the
  original working directory no longer exists. Bench wiring, crowbar board and console paths:
  `docs/09`.
- ★★ **The bench chip turned out to be in Level 0**: 64 kB dumped with **no glitch and no race**
  (`md5 6f37bd86c41a75c19db65cc5824f7199`, re-verified from the archive). The apparent lock was the
  `SWD SPEED 0` artefact (see the raiden entry above).
- ⛔⛔ **`docs/07` §2bis.5 — the "SRAM payload" route — is CLOSED, and so is its "free `.data`
  leak" fallback** (§2ter, 2026-09-07). At Level 1 `RAMREAD` ends in `LOCKUP`; a differential probe
  with `VTOR` relocated to SRAM **falsified** the "handler lives in flash" explanation, because an
  **unmapped address locks identically** ⇒ *this core escalates ANY bus error to LOCKUP*, and a
  flash read **by the core** is a bus error at Level 1. **The protection does not target only the
  debugger** ⇒ **the crowbar is back as the route.** The `.data` fallback does not exist either: at
  Level 1 with a probe attached the core **does not boot at all** (SRAM painted `0xA5A5A5A5`
  survives a reset **255/256 words**). ⚠ An earlier draft claimed "104, then 187 readable bytes" —
  **that was false**, it was Level-0-era SRAM residue.
- ★ **Open, untested, and it matters**: *how does a T310 sold in Level 1 boot at all?* Most likely
  the lock is conditioned on **debugger presence** (`C_DEBUGEN` / `CDBGPWRUPREQ`). Test costs
  nothing: `TARGET RESET` **without ever** `SWD CONNECT`, then watch consumption.

- **Its readout protection inverts the STM32 polarity, in the attacker's favour.** `OCDEN`
  (`0x0000_00C3`) must equal **exactly `0xC3`** for *any* protection to exist; `OCDM`
  (`0x0050_0004`) `== 0x3C` then selects L2 over L1. **The other 255 stored values of `OCDEN` are
  Level 0.** Source: official **User Manual V0.11 §28.3, fig. 28-4, p. 735** (archived under
  `datasheet/cible_BAT32G135/`). **Glitch `OCDEN`, never `OCDM`** — faulting `OCDM` only gives L1,
  which still blocks reads.
  ⚠️ **Keep the seam visible**: the table is about **stored values**. That a **faulted read** lands
  in the Level-0 row rather than on a **fail-safe closed default** is **`[reco]`, not `[UM]`** — the
  option-byte load is hardware and may latch closed on a malformed fetch. It is this project's
  working hypothesis and the **first thing to disprove** if a campaign never scores a success.
  Never restate it as sourced fact.
- **Skin ST, bones Renesas.** L0/L1/L2 naming and the datasheet template are ST-shaped; the option
  bytes (`000C0`=WDT, `000C1`=LVD, `000C2`=HOCO, `000C3`=OCD, mirrored at `010Cx` for boot swap),
  the safety-function set and the `P40`/`P137` pin naming are **RL78-shaped**. For undocumented OCD
  behaviour, read Renesas RL78 docs, not ST's.
- **Three independent locks, not two**: `OCDEN`, `OCDM`, and **`DBGSTOPCR.SWDIS`**
  (`0x4001_B004` bit 24) which lets *firmware* kill SWD at runtime. The third is a **race**, not a
  glitch — `DBGSTR` even exposes `CDBGPWRUPREQ`/`CDBGPWRUPACK`, the GD32/OFFZONE race signals.
- **No BOOT0, no documented ISP, no VCAP/REGC pin** → inject on **VDD**; raiden-pico's headline
  `TARGET GLITCH BYPASS` (SRAM boot + FPB) **does not transpose**; `SWD CONNECTRST` does.
- **POR needs a 300 µs minimum dip** below `VPDR` (1,37–1,45 V) → big depth headroom, *unless* LVD
  is armed (12 levels, 1,88–4,06 V). Measure the supply floor before budgeting depth.
- **FaultyCat v3 crowbar**: `width_ns` 8–50 000, `delay_us` 0–1 000 000 at **1 µs granularity**.
  That grid is **not** a blocker here — the internal LDO forces wide pulses anyway, so sweeping
  `width_ns ≥ 1 µs` makes the delay grid contiguous.
- ★ **Level 2 is the *most* attackable level, not the least** — and the doc's §9bis says why.
  The option bytes are **re-read on every reset**, not just POR (`[UM]` §28.1 p. 727; 7 reset sources
  §23 p. 677; `tRSL` = **10 µs** `[DS]` p. 49) ⇒ high campaign cadence, **no power-cycle needed**.
  At L2 only **`OCDEN`** must be faulted (`OCDM` becomes irrelevant) ⇒ **no multi-glitch**, so
  *Fill your Boots*' 36× penalty does not apply. And a hit lands in **L0**, where STM32 would only
  reach L1. ★ **One successful fault suffices for the chip's lifetime**: dump first, then rewrite
  `OCDEN` via `FLPROT`/`FLOPMD` to make it permanent — so a **0,01 % rate is still workable**.
  ⚠ There is **no documented recovery path** from L2 (chip erase is L1-only): FI is the only way in.
- ⚠⚠ **raiden-pico: ALWAYS say which raiden you mean — upstream or the local fork.** The two
  diverge sharply, and conflating them is how a session ends up hunting a command in the wrong repo.
  - **Upstream `AdamLaurie/raiden-pico`**: no BAT32 support of any kind. `GLITCHING_GUIDE.md` there
    is STALE (µs @ 1 MHz, `GP2`=ERROR flag); `README.md` + `CHANGELOG.md` are authoritative —
    **cycles @ 150 MHz**, `GP2` = glitch output.
  - ★ **The local fork, v0.14** (in `tplink_tapo-20260909.tgz`, `raiden-pico/`): **`TARGET BAT32`
    DOES exist** (v0.8, read-only target type; it enables `SWD RACE`'s `SUCCESS` plausibility test,
    SP-in-SRAM + PC-in-flash), and **`SWD OPT` decodes `OCDEN`/`OCDM`/`BTEN` — both clusters,
    boot-swap mirror `0x0000_01C3` included (`bat32_target.c:21-23`) — plus `DBGSTOPCR.SWDIS`**.
    `SWD RDP` **is** refused under `TARGET BAT32` — correctly. Milestones: `SWD RACE` + `TARGET
    BAT32` + `SWD OPT` decode (**v0.8**) · `SWD PHY PIO` (**v0.10**) · `SWD BAT32
    ARM/CHIPERASE/WRITE` (**v0.11**) · `SWD RACE PERSIST` (**v0.12**) · `SECTORERASE` + `RAMREAD`
    (**v0.13**) · UART0 console (**v0.14**).
  ⚠ **`TARGET GLITCH BYPASS` still does not transpose** (needs a BOOT0 the BAT32 lacks).
  ★ **Three raiden gotchas, all RE-VERIFIED at v0.14, not assumed** (`src/command_parser.c`):
  (1) **`TARGET RESET` with arguments only CONFIGURES** — `target_reset_execute()` runs *only* when
  no argument is given (`:1320`). Configure once (`TARGET RESET PERIOD <ms>`), then loop on bare
  **`TARGET RESET`**; otherwise the trigger never fires and the sweep shoots **zero glitches** in
  silence. Defaults: **GP15, 300 ms, active low**. (2) **`SWD READ` dumps BYTE-wise**
  (`0xAAAAAAAA: 00 11 22 …`, 16 bytes + ASCII per line) — the only 8-hex group per line is the
  **address**, so a word-oriented parser reads addresses, never data. The count argument **is** in
  words (`bytes = cnt * 4`, `:2960-2999`). (3) ★ **`SWD SPEED 0` is unusable on flying leads** — see
  the next entry; it is the single most expensive trap in the whole campaign.
- ★★★ **A too-fast SWD clock imitates a locked chip PERFECTLY — the most transferable fact of the
  whole BAT32 campaign, and it is not BAT32-specific** `[fait]`. At `SWD SPEED 0`, ~7000 shots read
  as `no_dp`/`ACK=0x7` and the target looked protected. It was not: it was in **Level 0** the whole
  time. Tells: `ACK = 0x7` is **none of** the three valid codes (`OK=1`/`WAIT=2`/`FAULT=4`), and the
  captured `DPIDR = 0x1780_28EF` is exactly **a canonical ARM DPIDR shifted one bit**
  (`(0x0BC0_1477 << 1) | 1`). It even produced a **fake ~1 % "success rate" that looked like a race
  window** (a false peak at 520 µs). ⇒ **Before concluding a target is protected, slow the clock and
  re-read `DPIDR`; if it is the bit-shift of a valid one, the problem is electrical, not
  cryptographic.**
- ⚠⚠ **FaultyCat v3 cannot be the SWD oracle — its SWD sub-shell is WIP.** Only `scan swd` is public
  and it is a **pinout scanner**, not a debug client: *"the firmware responds with `ERR wip`"* on the
  F6 SWD / F8-1 JTAG verbs (`faultycat-TUI/src/faultycmd/protocols/scanner.py`). Any FaultyCat bench
  therefore needs **three** tools: FaultyCat glitches, Bus Pirate 5 powers/resets, **ST-Link+OpenOCD
  (or raiden-pico) reads**. The TXS0108EPW ACK-sampling flaw on that same header is a second reason.
- **FaultyCat host API (verified in `faultycat-TUI`)**: `CrowbarClient.discover()` →
  `.ping()/.configure(trigger, output, delay_us, width_ns)/.arm()/.fire(trigger_timeout_ms)/.disarm()/.status()`;
  CLI equivalent `faultycmd crowbar configure --trigger ext_rising --output hp --delay-us N
  --width-ns N`, then `arm` / `fire` / `disarm`, plus `faultycmd doctor`. ⚠ **`fire` blocks** until
  the trigger arrives or the timeout expires — the reset/power-cycle must be issued from another
  thread while it waits.

## Repository Layout (operational rules)

- `docs_pdf/` — 68 source PDFs, **READ-ONLY** (see Core Principles) · `docs_pdf/writeups/` — 27 web
  write-ups converted to PDF, **`[ref]`, not counted**, cited by URL only.
- `docs/` — deliverable docs · `assets/schemas/` — PNGs (+ `src/` generators) · `datasheet/` — PDFs
  + index · `knowledge_base/` — the same sourced facts re-indexed by **vector**
  (voltage/clock/EMFI/laser) and **target domain** (MCU, Linux/Android, automotive, smartcards,
  IoT, x86), for reuse beyond this specific RP2350/STM32 build. Additive only — never delete or
  reorganize `docs/` when updating it. Full map: `@README.md`.

## File References

- @README.md — project overview and doc index.
- @docs/00_SYNTHESE_CORPUS.md — sourced synthesis of the 68 papers (fault models, parameters, detectors).
- @docs/02_BOM_MATERIEL.md — bill of materials (Palier 1 crowbar / Palier 2 AGW).
- @docs/03_METHODOLOGIE_CAMPAGNE.md — attack playbook (RDP, parameter search, defeating detectors).
- @docs/04_REFERENCES.md — annotated bibliography of the 68 corpus PDFs (per-paper relevance, sections
  **A–G + I**) + video sources `[ref]` (section H) and 27 web write-ups `[ref]` (section J) —
  **neither counted** in the 68.
- @docs/05_SCHEMAS_ELECTRONIQUES.md — block + component schematics.
- @docs/06_EMI_INJECTOR_EMFI.md — EMFI injector module (5 V → 1 kV), RP2350-driven; x86 feasibility.
- `docs/07_BAT32G135_FAULTYCAT.md` — first concrete target, and **the only one that reached a real
  bench**: dumping a **Cmsemicon BAT32G135** (a TP-Link Tapo T310) via SWD. **Deliberately
  self-contained / exportable** — facts are carried inline rather than cross-linked, so do not
  "fix" it into the usual cross-ref style.
  ⚠️ **No longer `@`-imported.** It grew to **~2500 lines / 150 kB** with the bench campaign
  (§0bis, §2bis, §2ter, §5.2bis, §9quinquies–§9septies). Same treatment as `docs/08`, same reason
  (`~/.claude/rules/claude-md-paradigm.md`: `@` is for short files needed *every* session). Read it
  with `cat`/Read when that target is the question.
- `docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md` — **the bench** behind `docs/07`: four wiring variants
  (raiden = time+oracle / FaultyCat = power), the AO3400A crowbar board with its ngspice-checked
  model, the 10 electrical rules, the four console paths, and the operational runbook (phases
  A0→G). Also **not `@`-imported** (~1900 lines). ⚠ **09 is the bench, 07 is the target** — a
  target verdict belongs in 07, a wiring rule in 09.
- `docs/08_NRF52820_APPROTECT.md` — **second concrete target**: dumping a **Nordic nRF52820** by
  glitching **`DEC1`** (the 1.1 V core rail). Also **deliberately self-contained / exportable**.
  ⚠️ **Deliberately NOT `@`-imported** — it is ~1000 lines and only matters when that target is on the
  bench; an `@` would load it into every session's context (see `~/.claude/rules/claude-md-paradigm.md`).
  Read it with `cat`/Read when the question calls for it.
- @datasheet/README.md — datasheet index with verified specs.
  Target-side docs (official datasheet + 746 p. user manual + SVD) live in
  `datasheet/cible_BAT32G135/`.
- **Bench artefacts are NOT in this repo.** Dumps, logs, the raiden-pico fork and the host tooling
  cited by `docs/07`/`docs/09` live only in **`tplink_tapo-20260909.tgz`**
  (md5 `710552fd8478250644d69eb233fddb1e`), under `tplink_tapo_bootloader_dump/`. Read without
  extracting: `tar -xzOf <archive> tplink_tapo_bootloader_dump/<path>`.

## Self-Improvement

- **Sourcing lesson (second one).** Beyond `fdtc.deib.polimi.it/FDTC<AA>/slides.html`, a **third-party
  curated list** is a real retrieval channel — the `dev-zzo` gist yielded 10 corpus PDFs and 27
  write-ups in one pass. ⚠️ Such a list is **not filtered for this project**: triage by counting
  `glitch` / `fault injection` occurrences on extracted text **before downloading**, and record the
  rejects (`docs/04` §F) so the FI boundary stays honest.
- **HTML → PDF that works here**: `chromium-headless-shell --headless --no-sandbox --disable-gpu
  --virtual-time-budget=15000 --print-to-pdf=… --no-pdf-header-footer <URL>`; on a Wayback link,
  insert **`id_`** after the timestamp (`if_` and the bare form hang on some hosts). Fallback without
  figures: `curl | pandoc -f html -t ms | groff -ms -Tpdf -k` (⚠️ `-Tpdf` glued, `-T pdf` fails).
- **Sourcing lesson (third one) — vendor docs hide inside CMSIS device packs.** Cmsemicon's own site
  (`mcu.com.cn`) serves its BAT32G135 datasheet/user-manual links **only through JavaScript**, and
  direct file URLs 404 behind a `.html` rewrite. The **746-page official user manual** — the document
  that settled the whole protection model — was found instead inside a **CMSIS `.pack` committed to a
  third-party GitHub repo** (`Gnailliang/BAT32G135-ADC` → `.pack/Cmsemicon/<part>.<ver>/Documents/`).
  ⇒ **For any Chinese MCU whose vendor site is JS-only, search GitHub for its `.pack`/`.pdsc` first**;
  packs routinely ship `Documents/UserManual/`, `Documents/DataSheet/`, `SVD/` and `Flash/*.FLM`.
  Corollary: a **`.svd` resolves register addresses faster than the manual** (it gave
  `DBG 0x4001B000`, `FMC 0x40020000`, `UID 0x0050084C` in one grep).
- **Second channel for a target's flash procedure: someone's hobby-hack repo.** A working OpenOCD
  dump/erase/write recipe for the whole BAT32/CMS32 family came from a **clone-charger modding repo**
  (`DSchndr/charge-me-up`), which also quotes the manual's flash-controller sequences verbatim.
  Search the **part number plus a consumer product**, not just the part number.
- ⚠️ **Search-engine summaries invent plausible identifiers.** Two claims here — an OpenOCD symbol
  `bat32_start_erase_flash` and a JLCPCB "pin-to-pin STM32G031" line — appeared **only** in search
  result prose and **vanished on targeted follow-up**. Neither entered the docs. **Never let a fact
  reach a doc on the strength of a search summary alone; open the artefact.**
- Operational rule (applies to all work here) → this `CLAUDE.md`.
- New sourced fact → the relevant `docs/` file, with citation; component data → `datasheet/` + index.
  If the fact is vector- or domain-generic (not specific to this RP2350/STM32 build), also mirror it
  into the matching `knowledge_base/{by-vector,by-domain,cross-cutting}/` file, same citation.
- Personal or one-off preferences (not project rules) → suggest `CLAUDE.local.md`.
- No `.claude/rules/` template matched this doc-only project (everything lives under `docs/`, so a
  path-scoped rule would always apply). Add one only if code (e.g. RP2350 firmware) is introduced.

## Documentation upkeep

- After any change to a doc, schematic, or the BOM: update the affected `docs/` file, the root
  `README` index, and `datasheet/README.md` in the **same session** — do not defer.
- When a corpus addition or correction affects a fact already mirrored in `knowledge_base/`, update
  that file too, in the same session — `knowledge_base/` is additive re-indexing, not a snapshot;
  letting it drift from `docs/` defeats its purpose.
