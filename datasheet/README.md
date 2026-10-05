# Datasheets — composants du glitcher RP2350

Datasheets PDF officiels des composants nommés du projet (voir
[`../docs/02_BOM_MATERIEL.md`](../docs/02_BOM_MATERIEL.md) et
[`../docs/05_SCHEMAS_ELECTRONIQUES.md`](../docs/05_SCHEMAS_ELECTRONIQUES.md)).
Chaque fichier a été téléchargé depuis la source ci-dessous et **validé** (magic bytes `%PDF`) le
**2026-08-18**. Les specs listées sont **extraites du PDF téléchargé** (pas de mémoire).

| Fichier | Composant | Fabricant | Rôle dans le projet | Specs vérifiées (extraites du datasheet) |
|---|---|---|---|---|
| `RP2350_RaspberryPi.pdf` | RP2350 | Raspberry Pi | **Contrôleur de timing** (PIO) | Dual Cortex-M33 / Hazard3 @150 MHz · 3 PIO / 12 SM · IOVDD 1,8–3,3 V · cœur 1,1 V · ★ **contient l'erratum RP2350-E9** (voir encadré ci-dessous) |
| `PicoW2_RaspberryPi.pdf` | **Raspberry Pi Pico 2 W** (RP-008304-DS-3) | Raspberry Pi | ★ **Carte réellement employée au banc** — fonde deux règles de conception ADC | **24 pages**, `%PDF` ✓ · §1.2 : **30 GPIO, dont 4 utilisables en ADC** ⇒ **RP2350A QFN-60** · §2.1 : `GPIO 26-28` = entrées ADC · ★ §3.3 : **l'ADC n'a AUCUNE référence interne, il utilise sa propre alimentation** ; `ADC_AVDD` vient du SMPS par un filtre **R-C 201 Ω / 2,2 µF**, l'ADC tire ~150 µA ⇒ **offset structurel ≈ 30 mV** · §2.2 : sortie 3V3 **à charger sous 300 mA** |
| `AO3400A_AOS.pdf` | AO3400A | Alpha & Omega | **Crowbar (défaut recommandé)** | **N-channel** · 30 V · Id 5,7 A (**pulsé 30 A**) · RDS(on) typ 19 / max 32 mΩ @4,5 V · Qg 6–7 nC · Vgs(th) 0,65–1,45 V · SOT-23 |
| `IRLML2502_Infineon.pdf` | IRLML2502 | Infineon (IR) | ★ **Crowbar attesté `[corpus]` sur MCU** (O'Flynn, ePrint 2016/810 p. 3 : c'est ce MOSFET qui glitche l'ATMega328P) | **N-channel** · 20 V · RDS(on) **45 mΩ** · SOT-23 — ⚠️ O'Flynn imprime **35 mΩ** (p. 2) : **écart avec la datasheet**, non résolu ; retenir 45 mΩ (source constructeur) |
| — *(pas de datasheet téléchargé)* | **IRF7807** | Infineon (IR) | Crowbar **forte puissance** pour SoC/FPGA à rail basse impédance (O'Flynn : RPi, BeagleBone, Android, Spartan-6) | **N-channel** · RDS(on) **14 mΩ** · **88 A pulsé** — ⚠️ **valeurs citées par O'Flynn p. 2, non vérifiées sur datasheet constructeur** ; à télécharger si le composant est retenu |
| `VN2222LL_Microchip.pdf` | VN2222LL | Microchip (Supertex) | Crowbar (réf. historique Bozzato) | **N-channel** DMOS enhancement · 60 V · TO-92 |
| `IRLML6402_Infineon.pdf` | IRLML6402 | Infineon (IR) | **Load switch high-side (Bloc A)** — ⚠ P-channel, pas crowbar | **P-channel** · −20 V · RDS(on) 65 mΩ · SOT-23 |
| `2N7002_Nexperia.pdf` | 2N7002 | Nexperia | Inverseur de commande du load switch | N-channel · 60 V · SOT-23 |
| `ADP3623_AnalogDevices.pdf` | ADP3623 | Analog Devices | **Gate driver du crowbar** | Dual **4 A** MOSFET driver · 4,5–18 V |
| `THS3062_TI.pdf` | THS3062 | Texas Instruments | Ampli du glitch (Tier 2 AGW) | Dual current-feedback · high slew-rate · ~145 mA |
| `TPS22918_TI.pdf` | TPS22918 | Texas Instruments | Load switch (Bloc A, option intégrée) | Load switch · ≤ 5,5 V · 2 A |
| `TLV3501_TI.pdf` | TLV3501 | Texas Instruments | Comparateur du trigger (Bloc C) | Rail-to-rail · propagation ~4,5 ns · 2,7–5,5 V |
| `MAX4619_AnalogDevices.pdf` | MAX4619 | Analog Devices (Maxim) | ★ **Organe de glitch alternatif au crowbar** (Bloc B variante) — commute le rail cible entre `VCC` nominal et une tension basse | **Trois commutateurs SPDT** CMOS haute vitesse · **R_on max 10 Ω @ +5 V**, **20 Ω @ +3 V** · appariement **1 Ω** entre canaux · **t_ON 15 ns / t_OFF 10 ns** · **courant continu ±75 mA max par borne** |

## ★★ Erratum **RP2350-E9** — lu dans la datasheet officielle, pas sur un forum

> Source : `RP2350_RaspberryPi.pdf`, section **RP2350-E9** (*« Increased leakage current on Bank 0
> GPIO when pad input is enabled »*). ⚠ **Affecte le stepping `RP2350 A2`** — la datasheet le dit
> explicitement, et signale par ailleurs que le silicium corrigé *« Fix RP2350-E9: … The pad circuit
> is modified »*. **Vérifier le stepping de la puce réellement employée.**

Texte officiel, en substance : pour les pads GPIO 0 à 47, **quand le pad est configuré en ENTRÉE et
que sa tension se trouve dans la région logique indéfinie** (entre `VIL` et `VIH`), le courant de
fuite dépasse la spécification `IIN` — *« typically around **120 µA** »* — et **maintient le pad
autour de 2,2 V**. ★ **Le pull-down interne est nettement plus faible que cette fuite et ne suffit
pas** à tirer le pad au bas. À `IOVDD` = 1,8 V, la fuite tombe à **~30 µA**.

★ **Ce que la datasheet recommande, et pourquoi ça ne suffit PAS pour une grille de MOSFET.** Elle
écrit qu'*« un tirage bas de **8,2 kΩ ou moins** vainc la fuite »* — c'est vrai **au sens
logique**, c'est-à-dire pour ramener le pad sous `VIL`. Mais une grille de MOSFET ne se juge pas à
`VIL` :

| `R_pd` | Tension retenue (120 µA × R) | Verdict pour une **grille** (AO3400A, `V_GS(th)` min **0,65 V**) |
|---:|---:|---|
| 10 kΩ (le réflexe) | **1,20 V** | ❌ **allume le MOSFET** |
| 8,2 kΩ (le workaround datasheet) | **0,98 V** | ❌ vise `V_IL`, **pas une grille** |
| 4,7 kΩ | 0,56 V | ⚠ 14 % de marge seulement — et `V_GS(th)` dérive de ~−2 mV/°C |
| ★ **1 kΩ** | **0,12 V** | ✅ **retenu** — facteur 5 de marge |
| 100 Ω | 0,012 V | ✅ mais inutile derrière un GPIO nu (il ferait diviseur) |

⇒ **Tout GPIO RP2350 pilotant une grille de MOSFET doit porter un pull-down de 1 kΩ**, monté **sur
la carte MOSFET, entre grille et source, au ras du transistor** — pas côté contrôleur : un fil de
grille arraché doit laisser la grille au repos. Voir
[`../docs/05_SCHEMAS_ELECTRONIQUES.md`](../docs/05_SCHEMAS_ELECTRONIQUES.md) §4 et
[`../docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md`](../docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md) §4.2.

⚠ **Conséquence secondaire, moins évidente** : un firmware qui **force une broche à 0 V** plutôt que
de la laisser en entrée le fait souvent **à cause de cet erratum**. Une telle broche est alors une
**sortie pilotée**, jamais de la haute impédance — la poser sur un rail alimenté à travers quelques
ohms y fait passer des **centaines de mA** dans une broche prévue pour 12 mA.

---

## Choix de l'organe de glitch — MOSFET crowbar ou MUX analogique

★ **Le corpus documente deux topologies, pas une.** Le **crowbar** (MOSFET N vers la masse) est celle
de Bozzato et O'Flynn ; le **MUX analogique MAX4619** est celle de **Gerlinsky** (origine, deck RECON
BRX 2017 sl. 27-28/33) et de **chip.fail** (sl. 65-66) — et c'est avec elle que chip.fail casse un
**STM32F2**. Voir [`../docs/05_SCHEMAS_ELECTRONIQUES.md`](../docs/05_SCHEMAS_ELECTRONIQUES.md) §4.2.

⚠️ **Le contrôle de courant du MAX4619 décide de son domaine d'emploi.** Datasheet vérifiée :
**±75 mA continus par borne** et **R_on 10–20 Ω**. C'est adapté à un MCU dont la consommation reste
sous **100 mA** — ce que Bozzato donne justement comme courant cible typique — mais **rédhibitoire
pour un rail de cœur basse impédance de SoC rapide**, exactement le même critère de sélection que le
RDS(on) du MOSFET ci-dessous. **t_ON 15 ns / t_OFF 10 ns** situent par ailleurs son plancher de
commutation dans le même ordre de grandeur que la chaîne driver + MOSFET.

## Choix MOSFET crowbar — récapitulatif

Le crowbar exige un **canal N** (court-circuit du rail vers la masse, côté bas). L'**AO3400A** reste le
**défaut recommandé** : RDS(on) la plus basse (glitch plus profond) et courant crête le plus élevé
(pulsé 30 A), pour un Qg bas suffisant — la différence de Qg avec l'IRLML2502 est noyée par le chemin
gate driver + parasites PCB. L'**IRLML6402 est un canal P** : à réserver au **load switch (Bloc A)**,
jamais au crowbar.

★ **Critère de sélection désormais sourcé `[corpus]`** — O'Flynn, *Fault Injection using Crowbars on
Embedded Systems* (ePrint 2016/810, entré au corpus) tranche par **l'impédance du rail visé** (p. 2) :
un RDS(on) de l'ordre de **35–45 mΩ** *« would be **less effective against low-impedance power rails**
likely to be found on **high-speed processor boards** »*, d'où son usage de l'**IRF7807** (14 mΩ,
88 A pulsé) sur SoC/FPGA et de l'**IRLML2502** sur MCU. Transposé à ce projet : l'**AO3400A**
(19–32 mΩ, 30 A pulsé) est **bien dimensionné pour un STM32**, mais **marginal pour un rail cœur de
SoC rapide** — si une telle cible est visée, passer à un MOSFET de classe IRF7807.

⚠️ **Le gate driver n'est PAS re-sourçable sur O'Flynn** : il ne nomme aucun circuit de driver
(commande par l'électronique du ChipWhisperer, renvoi à Balogh/TI pour les impulsions étroites).
L'**ADP3623 reste attribuable à Bozzato seul**.

## Sources (téléchargées le 2026-08-18, sauf mention contraire)

- RP2350 — https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf
- **Pico 2 W** *(téléchargée le **2026-09-16**)* — https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf · archive : https://web.archive.org/web/20250913034839/https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf
  (`%PDF` ✓, **24 pages** ✓, réf. imprimée **RP-008304-DS-3**). ⚠ Il n'existe **pas** d'errata
  RP2350 en PDF séparé : `rp2350-errata.pdf` répond **404** — l'erratum **E9 est une section de
  la datasheet RP2350 elle-même**, déjà présente ici.
- AO3400A — https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf
- IRLML2502 — https://www.infineon.com/dgdl/Infineon-IRLML2502-DataSheet-v01_01-EN.pdf
- VN2222LL — https://ww1.microchip.com/downloads/en/DeviceDoc/VN2222LL-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005987A.pdf · archive 2026-10-05 : https://web.archive.org/web/20261005002021/https://ww1.microchip.com/downloads/en/DeviceDoc/VN2222LL-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005987A.pdf
- IRLML6402 — https://www.infineon.com/dgdl/Infineon-IRLML6402-DataSheet-v01_01-EN.pdf
- 2N7002 — https://assets.nexperia.com/documents/data-sheet/2N7002.pdf
- ADP3623 — officiel https://www.analog.com/media/en/technical-documentation/data-sheets/adp3623_3624_3625_3633_3634_3635.pdf
  (⚠ analog.com injoignable depuis l'environnement de build → PDF récupéré via le miroir
  archive.org `manuallib-id-2596370` ; **remplacer par la version officielle ADI si besoin**)
- THS3062 — https://www.ti.com/lit/ds/symlink/ths3062.pdf
- TPS22918 — https://www.ti.com/lit/ds/symlink/tps22918.pdf
- TLV3501 — https://www.ti.com/lit/ds/symlink/tlv3501.pdf
- MAX4619 *(téléchargée le **2026-08-28**)* — officiel
  https://www.analog.com/media/en/technical-documentation/data-sheets/MAX4617-MAX4619.pdf
  (⚠ analog.com injoignable depuis l'environnement de build, comme pour l'ADP3623 → PDF récupéré via
  **archive.org** ; `%PDF` et 16 pages vérifiés, titre imprimé *« MAX4617/MAX4618/MAX4619 —
  High-Speed, Low-Voltage, CMOS Analog Multiplexers/Switches »*. **Remplacer par la version officielle
  ADI si besoin.**)

> Composants **génériques** non inclus (pas de référence unique) : DAC ≥ 12 bits (Tier 2), relais
> reed, résistances/condensateurs, connecteurs SMA/headers. Le générateur DDS **FeelTech FY3200S**
> (option Tier 2) est un instrument, pas un composant à datasheet.

---

## Documents de la **cible** (pas du glitcher) — `cible_BAT32G135/`

Documentation officielle **Cmsemicon** du MCU attaqué dans
[`../docs/07_BAT32G135_FAULTYCAT.md`](../docs/07_BAT32G135_FAULTYCAT.md). Archivée ici parce que la
source amont est fragile : le manuel utilisateur n'est **pas** distribué en direct par
`mcu.com.cn` (liens JS + réécriture d'URL) — il n'a été trouvable que dans un **pack CMSIS déposé
sur GitHub par un tiers**. Téléchargés et validés le **2026-08-30**.

| Fichier | Document | Validation |
|---|---|---|
| `BAT32G135_Datasheet_V1.40_Cmsemicon.pdf` | Datasheet officielle V1.40 | `%PDF` ✓ · **71 pages** ✓ |
| `BAT32G135_UserManual_V0.11_Cmsemicon.pdf` | 用户手册 (manuel utilisateur) officiel V0.11 | `%PDF` ✓ · **746 pages** ✓ |
| `BAT32G135.svd` | Description CMSIS-SVD officielle (pack Cmsemicon 0.2.1) | XML, 405 ko |

**Ce qu'ils tranchent** (détail et citations dans `docs/07`) :
- **Manuel §28.3, fig. 28-4, p. 735** — tableau de vérité de la protection en lecture :
  `OCDEN` (`0x0000_00C3`) et `OCDM` (`0x0050_0004`). ★ `OCDEN` doit valoir **exactement `0xC3`**
  pour qu'une protection existe ; les **255 autres valeurs donnent le Level 0**.
- **Manuel §28.3, p. 735** — `BTEN` (`0x0050_0005` bit 0) : **boot swap** `0000H~0FFFH` ↔ `1000H~1FFFH`.
- **Manuel p. 6 + SVD** — `DBGSTOPCR` (`0x4001_B004`) bit 24 `SWDIS` : **désactivation logicielle du SWD**.
- **Manuel §29.3** — contrôleur flash, base `0x4002_0000` (`FLSTS`/`FLOPMD1`/`FLOPMD2`/`FLERMD`/`FLPROT`).
- **Datasheet §1.3, p. 6-9** — brochages : SWDIO = `P40`, SWCLK = `P137`, **aucune broche `VCAP`/`REGC`**.
- **Datasheet §6.8.5, p. 61** — POR : `VPDR` 1,37–1,45 V et **largeur minimale de 300 µs**.

> Sources amont : datasheet — `https://www.axtekic.com/web/uploads/file/20230506/UK39o0N9kBX7I98V37u0g3A6r1J2FbY4.pdf`
> (archive 2026-10-05 : https://web.archive.org/web/20261005002033/https://www.axtekic.com/web/uploads/file/20230506/UK39o0N9kBX7I98V37u0g3A6r1J2FbY4.pdf) ;
> manuel + SVD — pack CMSIS `Cmsemicon.BAT32G135.0.2.1` via `github.com/Gnailliang/BAT32G135-ADC`.

---

## Documents de la **cible nRF52820** (pas du glitcher) — `cible_nRF52820/`

Documentation officielle **Nordic Semiconductor** du MCU visé par
[`../docs/08_NRF52820_APPROTECT.md`](../docs/08_NRF52820_APPROTECT.md) (playbook complet), et cité
dans la §9.3 de [`../docs/03_METHODOLOGIE_CAMPAGNE.md`](../docs/03_METHODOLOGIE_CAMPAGNE.md) et la
§11bis de
[`../knowledge_base/by-domain/microcontrollers-mcu.md`](../knowledge_base/by-domain/microcontrollers-mcu.md).
Archivée ici parce que la source amont est **inaccessible en direct** : `docs.nordicsemi.com`,
`infocenter.nordicsemi.com` et `www.nordicsemi.com` répondent tous **HTTP 403** derrière un challenge
Cloudflare depuis l'environnement de build — même situation que pour l'ADP3623 et le MAX4619
ci-dessus. Téléchargée et validée le **2026-09-15**.

| Fichier | Document | Validation |
|---|---|---|
| `nRF52820_PS_v1.3_Nordic.pdf` | *nRF52820 Product Specification* officielle **v1.3** (réf. interne `4463_156 v1.3`) | `%PDF` ✓ · **452 pages** ✓ · titre PDF `nRF52820` ✓ |

**Ce qu'elle tranche** (détail et citations dans les deux documents ci-dessus) :

- ★★ **§4.8.2, p. 41 — deux régimes d'Access Port Protection selon le *build code* de la puce** :
  `Cxx` et antérieurs = *« controlled by hardware »*, **protection désactivée par défaut** (le régime
  contourné par LimitedResults) ; `Dxx` et ultérieurs = *« controlled by hardware **and software** »*,
  **protection activée par défaut**, exigeant `UICR.APPROTECT = HwDisabled` **et** une écriture
  firmware `APPROTECT.DISABLE = SwDisable`. Registres : base `0x40000000`, `FORCEPROTECT` offset
  `0x550`, `DISABLE` offset `0x558`.
- ★★ **Figure 166, §10.1, p. 446 — le régime se lit sur le boîtier.** Le marquage porte
  `<PP><VV><H><P>` et *« only the **first two characters** of the function variant code are used »* ⇒
  **la lettre `<H>` (build code) est lisible à la loupe, le suffixe `-D` ne l'est pas**.
- **Table 144, §10.4, p. 448 — code de variante fonctionnelle** : `AA` = *controlled by hardware*,
  `AA-D` = *controlled by hardware and software* (références `nRF52820-QDAA-D-R7`,
  `nRF52820-CFAA-D-R7`). ⚠️ **La PS ne relie jamais explicitement `AA-D` au build code `Dxx`** — deux
  identifiants distincts, la corrélation reste une inférence.
- **Brochage — la broche d'injection existe** : **QFN 5×5 mm / 40 broches / pas 0,4 mm → broche 1 =
  `DEC1`, « 1.1 V Digital supply decoupling »** · **WLCSP 2,531 × 2,531 mm / 44 billes / pas 0,35 mm →
  bille A7 = `DEC1`** · `DEC4` = 1,3 V (broche 38 / bille A5, à relier à `DEC6`) · `DEC5` **non
  connecté sur les build codes `Dxx` et ultérieurs**.
- **Mémoires** : 256 kB Flash / 32 kB RAM.

> Source amont (403 depuis l'environnement de build) :
> `https://infocenter.nordicsemi.com/pdf/nRF52820_PS_v1.3.pdf` — PDF récupéré via **archive.org**
> (`https://web.archive.org/web/20231225001418if_/https://infocenter.nordicsemi.com/pdf/nRF52820_PS_v1.3.pdf`).
> **Remplacer par la version officielle Nordic si elle redevient accessible.**

