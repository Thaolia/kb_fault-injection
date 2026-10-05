# voltage_glitch — Injecteur de fautes RP2350 pour STM32

Compilation d'un corpus de recherche (`docs_pdf/`) en **préconisations d'ingénierie** et
**nomenclature matérielle (BOM)** pour construire une carte à base de **RP2350** réalisant du
**voltage glitching** (injection de fautes par perturbation de l'alimentation) sur des
microcontrôleurs **STM32**.

> **Portée.** Documentation seule (aucun code). Carte pensée **famille-agnostique** (sortie de glitch
> branchable sur VDD ou VCAP), méthodologie couvrant plusieurs familles STM32.

## Documents (`docs/`)

| Fichier | Contenu | Nature |
|---|---|---|
| [`docs/00_SYNTHESE_CORPUS.md`](docs/00_SYNTHESE_CORPUS.md) | Compilation des 68 papiers : taxonomie, modèles de faute, paramètres, détecteurs, métriques | **Sourcé** |
| [`docs/01_PRECONISATIONS_ARCHITECTURE.md`](docs/01_PRECONISATIONS_ARCHITECTURE.md) | Choix du RP2350, schéma-bloc, architecture 2 paliers (crowbar / forme d'onde arbitraire) | Recommandation |
| [`docs/02_BOM_MATERIEL.md`](docs/02_BOM_MATERIEL.md) | Nomenclature chiffrée, coûts, comparatif acheter/construire | Recommandation |
| [`docs/03_METHODOLOGIE_CAMPAGNE.md`](docs/03_METHODOLOGIE_CAMPAGNE.md) | Playbook d'attaque : cibles STM32, RDP, recherche de paramètres, contournement des détecteurs | **Sourcé** + pratique |
| [`docs/04_REFERENCES.md`](docs/04_REFERENCES.md) | Bibliographie annotée des 68 PDF (+ sources vidéo et 27 write-ups web `[ref]`), avec pertinence projet | **Sourcé** |
| [`docs/05_SCHEMAS_ELECTRONIQUES.md`](docs/05_SCHEMAS_ELECTRONIQUES.md) | Schémas de principe (PNG + netlist) : crowbar, load switch, trigger, interfaces, Palier 2 | Recommandation |
| [`docs/06_EMI_INJECTOR_EMFI.md`](docs/06_EMI_INJECTOR_EMFI.md) | Module EMFI (5 V → 1 kV) piloté RP2350 : architecture, BOM, sécurité HT, intégration FaultyCat, faisabilité x86/NUC, retour d'expérience praticien (talk Hackfest) | Mixte (corpus + reco + ref) |
| [`docs/08_NRF52820_APPROTECT.md`](docs/08_NRF52820_APPROTECT.md) | **Seconde cible concrète** : dump d'un **Nordic nRF52820** par voltage glitching sur **`DEC1`** (rail cœur 1,1 V), bypass **APPROTECT**. ★★ **Deux cibles concrètes** : un **dongle Logitech CU0021** dont le marquage, lu sur les **photos internes du dossier FCC**, donne `<H>` = **`C`** ⇒ **régime non durci attesté**, en **QFN40** ; et une souris **Logitech Signature M650 / M650 L** (nRF52820 attesté `[ref]` sur la variante *Signature*, ⚠️ **non attesté** sur la **L**, et probablement en régime durci). ★ **Deux régimes de protection selon le *build code* de la puce**, à trancher à la loupe **avant** toute campagne. **Document autonome, exportable tel quel** | Mixte (officiel + reco + ref) |
| [`docs/07_BAT32G135_FAULTYCAT.md`](docs/07_BAT32G135_FAULTYCAT.md) | **Cible concrète, et la SEULE passée sur un banc réel** : dump de la flash d'un **Cmsemicon BAT32G135** — celui d'un capteur **TP-Link Tapo T310**. Modèle de protection `OCDEN`/`OCDM`, brochage SWD des 4 boîtiers, boot swap, playbook. ★★★ **Rapport de campagne** (`[fait]`, août-sept. 2026) : puce trouvée en **Level 0** et dumpée **sans un seul glitch** (§0bis), Level 1 mesuré aller-retour (§2bis), **espace d'adressage sondé + bootloader A/B désassemblé** (§5.2bis), et ⛔ **§2ter : la voie « payload en SRAM » est CLOSE** — au Level 1 la flash est fermée **au cœur aussi**. **Document autonome, exportable tel quel** | Mixte (**`[fait]`** + officiel + reco + ref) |
| [`docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md`](docs/09_BANC_BAT32_FAULTYCAT_RAIDEN.md) | **Le banc** derrière le doc `07` : **4 variantes de câblage** (raiden = temps + oracle / FaultyCat = puissance), la **carte crowbar AO3400A** avec son modèle **recoupé par ngspice à 0,7 %**, les **10 règles électriques**, les 4 voies de console, et le **runbook opératoire** (phases A0→G). ⚠ **09 = le banc, 07 = la cible** | Mixte (**`[fait]`** + **`[fw]`** + reco) |

Les schémas en PNG sont dans [`assets/schemas/`](assets/schemas/) — **23 figures** : bloc
d'ensemble, crowbar, load switch, trigger, interfaces, Palier 2, module EMFI, les **deux bancs
BAT32G135** du doc `07`, le **banc nRF52820** du doc `08`, et les **12 figures du doc `09`**
(4 variantes de câblage, 4 schémas de carte crowbar, 4 courbes de simulation).
⚠ **Le préfixe est celui du document, pas une série continue** : `07_*` / `08_*` / `09_*`.
Leurs générateurs (`graphviz` / `schemdraw`) sont dans
[`assets/schemas/src/`](assets/schemas/src/) — régénération par `generate.sh`.

## ★★★ Le projet a désormais des faits MESURÉS, pas seulement lus

Jusqu'en septembre 2026 ce dépôt était **purement documentaire** : trois étiquettes de provenance —
`[corpus]` (un PDF de `docs_pdf/`), `[ref]` (une source publique), `[reco]` (une recommandation
d'ingénierie). **Une campagne matérielle réelle sur BAT32G135 en ajoute deux** :

| Étiquette | Sens | Où |
|---|---|---|
| **`[fait]`** | **mesuré sur le banc réel**, date et journal cités | `docs/07`, `docs/09`, `docs/03` §1.1, `docs/06` §1.8 |
| **`[fw]`** | **lu dans le code source** d'un firmware, fichier et ligne cités | `docs/09`, `docs/01` §1.2, `docs/06` §5.2 |

★ **`[fait]` prime sur `[corpus]`** pour la pièce mesurée — mais **ne se généralise pas** : ce qui
se transpose est la *question à poser*, pas la réponse. ⚠ **Et un modèle n'est jamais un `[fait]`**,
même recoupé par deux solveurs indépendants.

⚠️ **La campagne de banc ne bouge pas le compte : 68 papiers.** Rien de cette campagne n'est un PDF de
`docs_pdf/`. (Le passage de 59 à 68 vient d'**ajouts distincts** : la thèse Werner + **8 papiers minés dans sa bibliographie**, voir plus bas.)

### Ce que la campagne a changé dans les préconisations de ce projet

- ★★ **Trois composants manquaient au crowbar** (`docs/05` §4, `docs/02`) : un **pull-down de grille
  de 1 kΩ** — sans lui, l'**erratum RP2350-E9** (120 µA dans un pad repassé en entrée) peut
  **allumer le MOSFET hors firmware** —, un **amortissement de drain `R_damp`** sans lequel le nœud
  **oscille jusqu'à −2,37 V**, et **deux résistances de 1 kΩ** protégeant les entrées ADC (maximum
  absolu d'E/S : −0,3 V).
- ★ **`Rs` n'est plus « 10–100 Ω à caractériser »** : elle **se mesure** (`C_résid = τ / Rs`) et vaut
  des **unités d'ohms**, pas des dizaines.
- ★ **L'ADC du RP2350 n'a aucune référence interne** : une entrée posée sur le rail 3,3 V brut
  **sature**, par construction. `docs/05` §2 en tire les conséquences.
- ★★ **Le piège le plus coûteux du lot n'est pas électrique mais méthodologique** : une horloge de
  debug trop rapide **imite parfaitement une puce verrouillée**, et fabrique une **fausse fenêtre de
  ~1 %**. ~7 000 tirs ont été tirés contre une puce qui était **déjà ouverte**. Règle en
  `docs/03` §1.1.

## Base de connaissances réutilisable (`knowledge_base/`)

En complément de `docs/` (qui documente *cette* carte RP2350/STM32), le répertoire
[`knowledge_base/`](knowledge_base/) réorganise les mêmes faits sourcés **par vecteur**
(voltage, clock, EMFI, laser) et **par domaine cible** (microcontrôleurs, Linux/Android,
automobile, cartes à puce, IoT, x86/serveur), pour être réutilisé sur de **futures cibles**
indépendamment de ce projet. Voir [`knowledge_base/README.md`](knowledge_base/README.md)
pour la navigation ; `docs/` reste inchangé et fait toujours foi pour l'historique du corpus.

## Principe directeur

Le corpus reste **déséquilibré**, mais nettement moins qu'à l'origine : **trois** papiers traitent le
voltage FI sur STM32 — Bozzato (*Shaping the Glitch*, TCHES 2019), seul à attaquer une **protection
réelle** (RDP) ; *Controlling PC on ARM* (deck FDTC 2016, **ajouté**), qui apporte le **modèle
d'exploitation** (corruption d'un load → contrôle du PC) sur un **STM32F415RG** ; et **chip.fail**
(deck 2019, **ajouté**), qui casse la **RDP2 d'un STM32F2** et publie ses paramètres. ★ S'y ajoute
un **quatrième cas STM32, par EMFI** : **COSIC** sur **STM32F411**, et — en `[ref]` — un
**STM32F401CC** chez Anvil Secure, le seul document à **nommer le rail d'injection sur STM32
(`VCAP_1`)**. Il s'est enrichi de
**12 exposés pratiques Raelize/Riscure** (Timmers, Mune, Pareja, Bogaard, Milburn, Spruyt, Witteman,
Wiersma) — attaques FI réelles + modèles de faute exploitables — qui **comblent la lacune
« instruction skip »** du projet (voir `docs/00` §3.4 et `docs/03` §9), et de **12 papiers repêchés
dans les bibliographies du corpus lui-même** (voir plus bas). Les documents **séparent explicitement trois provenances** :
**`[corpus]`** (sourcé des PDF de `docs_pdf/`, avec pages), **`[ref]`** (sources publiques externes,
avec URL — ex. PicoEMP, ChipShouter) et **`[reco]`** (recommandation d'ingénierie : carte, BOM, PIO,
appuyée sur l'état de l'art et le product brief RP2350). Rien n'est présenté comme sourcé s'il ne l'est pas.

## Points saillants

- **Voltage glitch = vecteur principal sur STM32** : la PLL interne neutralise le clock glitch sauf
  boot sur HSE (*Peak Clock*).
- **Modèle de faute correct** : set/reset (stuck-at), pas bit-flip ; on contrôle le timing et
  l'intensité, jamais la localisation (CASA, Ghalaty).
- **Recommandation n°1** : **sous-alimenter puis glitcher** (1,0 → 0,93 V, *TCHES 2024*) — et
  **chauffer** (*Ege et al., FDTC 2014*). ⚠️ Les deux moitiés sont sourcées **séparément** ; aucun
  papier du corpus ne mesure leur **couplage**. Et le chauffage **déplace** le seuil de faute
  (≈ +2,2 ns à ΔT = 75 °C) plus qu'il n'**élargit** la fenêtre — l'énoncé d'origine est prudent :
  *« SOME types of faults are easier to induce »*. Détail et réserves : `docs/00` §6.
- **Séquences documentées** : bypass RDP STM32F103 (`Read Memory`) et downgrade RDP L2→L1 STM32F373.
- **RP2350** : rôle de contrôleur de timing (PIO déterministe), équivalent du STM32F407 de Bozzato.
- **Modèle de faute d'exploitation** : la faute réelle est une **corruption d'instruction** (le *skip*
  n'en est qu'un sous-cas) → **contrôle du program counter** = exécution arbitraire sans faille
  logicielle (Raelize/Riscure ; formalisation d'origine *Controlling PC on ARM*, deck FDTC 2016,
  **désormais `[corpus]`** — voltage FI sur STM32F415RG, où l'encodage de l'instruction pèse plus que
  la finesse du glitcher : `LDMIA` ne demande qu'**1 bit** corrompu là où `LDR` en demande **2**, et
  réussit d'environ **un ordre de grandeur** plus souvent — ordre de grandeur *lu sur les nuages de
  points* du deck, non imprimé).
- **Un glitch n'a pas besoin d'être « sharp » / sous-cycle** : des largeurs bien supérieures au cycle
  fonctionnent (*False Injections*, Dartmouth 2025) — appui direct du point « résolution de commande ≠
  largeur de glitch ».
- **EMFI touchless, bas coût dès quelques dollars** : retour d'expérience praticien (talk Hackfest
  LeClair 2026, `[ref]`, `docs/06` §1/§5/§6) — traverse potting/encapsulation, faisceau localisé,
  méthodologie de reconnaissance XY (geler CPU, écrire/injecter/comparer) transposable au firmware
  RP2350.

## Répertoire source

`docs_pdf/` contient **68 PDF** (**37 d'origine, non modifiés, + 12 ajoutés par minage des
bibliographies, + 10 ajoutés depuis le gist `dev-zzo`, + 1 thèse de doctorat ajoutée directement —
Werner, VERIMAG 2022, `tel-03719660`**), tous exploités : le
socle académique (voltage / clock / EMFI / détecteurs / modèles de faute), **17 papiers EMFI** (dont
Fraunhofer, EMFI x86 ; O'Flynn — seul cas EMFI in-situ sur ECU automobile réel ; Toldo — banc EMFI DIY
chiffré sur SoC IoT ; **COSIC — seul EMFI sur STM32**), **12 exposés pratiques Raelize/Riscure**
(attaques FI réelles + modèles de faute ; 1 EMFI — Google TV Streamer —, 1 hors périmètre FI — QSEE)
et **5 papiers laser**. `shaminderpaper.pdf` (scan image) a été lu via rendu page-image —
bibliographie annotée complète dans `docs/04`. ⚠️ **Sections comptées = A–G + I** ; la **section H**
(6 talks vidéo) et la **section J** (27 write-ups web) sont `[ref]` et **non comptées**.

### Deuxième vague d'ajouts — le gist `dev-zzo` (10 PDF + 27 write-ups)

Une **liste curatée externe** de ressources sécurité MCU/SoC
([gist `dev-zzo`](https://gist.github.com/dev-zzo/f9eb667729dc9f9a537afb2a77bb6161)) a fourni une
seconde vague. Seuls **les documents dont le fault injection est le vecteur** ont été retenus — le
tri a été fait par comptage d'occurrences (`glitch`, `fault injection`) sur le texte extrait, **avant
téléchargement** ; le détail des rejets est consigné dans [`docs/04`](docs/04_REFERENCES.md) §F.

| Ajout | Ce qu'il débloque |
|---|---|
| **Fill your Boots** (TCHES 2021) | le **FI sur bootloader embarqué** — le régime exact des deux séquences STM32 de Bozzato ; **premier multi-glitch documenté**, ***grey-box glitching***, 9 anti-patterns de conception |
| **chip.fail** (deck 2019) | **3ᵉ voltage FI sur STM32** du corpus (**STM32F2**, Trezor One) ; la bootROM désassemblée ne teste **que `0xAA`** ; glitcher open-source **~92 $** à **MUX MAX4619** |
| **COSIC — *Design Considerations for EM Pulse FI*** | ★ **seul EMFI sur STM32** (STM32F411, non invasif) **et seul papier de conception d'injecteur** : banc **≈ 40 €**, l'**amortissement** fixe la sélectivité temporelle |
| **Gerlinsky — *Breaking CRP on NXP LPC*** (RECON 2017) | l'**asymétrie de l'espace des valeurs** (4 mots protègent, 4,29 milliards ouvrent) ; **origine du MUX MAX4619** |
| **NCC — *Microcontroller Readback Protection*** | l'inventaire des **protections en readback** et de leurs contournements, versant **défensif** compris |
| **GD32 / OFFZONE** (deck 2023) | ★ **attestation `[corpus]` du RP2040 + PIO** comme séquenceur déterministe (là où l'USB introduit du jitter) ; ⚠️ son voltage glitcher, lui, **échoue** |
| **RHUL**, **Hériveaux**, **Skorobogatov (PAINE)** | ouvrent le **vecteur laser**, jusqu'ici absent du corpus — utile comme **repli contre une cible qui détecte les glitchs de tension** |
| **Temeiza & Oswald** (deck BH EU 2019) | *« les bootloaders STM8 et STM32 sont sûrs contre les attaques **logiques** »* — donc sur STM32, **le FI est la voie** |

Le même gist a fourni **27 write-ups de praticiens** (attaques FI réelles sur STM32, ESP32, nRF52,
RH850, LPC1343, EFM32…), **convertis en PDF** et archivés dans **`docs_pdf/writeups/`**. ⚠️ Ils
restent **`[ref]`** et **ne comptent pas** dans les 60 : un billet converti n'est pas un artefact
publié, et **sa pagination est un produit de notre conversion** → on les cite **par URL, jamais par
page**. Liste complète : [`docs/04`](docs/04_REFERENCES.md) §J.
★ Le plus important d'entre eux (**Anvil Secure**, *Glitching STM32 Read Out Protection*, STM32F401CC)
**nomme le rail d'injection sur STM32 — `VCAP_1`** —, ce que ni Bozzato ni le deck FDTC 2016 ne
font : il valide
une inférence que le projet portait en « à vérifier » (voir [`docs/03`](docs/03_METHODOLOGIE_CAMPAGNE.md) §2.2 et §3.4).
★ **Un second rail cœur est désormais nommé, hors STM32** : les deux write-ups **LimitedResults sur
nRF52** (*APPROTECT Bypass*, `[ref]`), relus intégralement, injectent sur **`DEC1`** — *« definitively
the CPU power line »*. Le projet dispose donc de la question généralisée *« le régulateur interne
expose-t-il une broche de découplage ? »*, avec ses trois réponses documentées : `VCAP` (STM32),
`DEC1` (nRF52), **aucune** (BAT32G135 ⇒ VDD à travers le LDO). Voir
[`docs/03`](docs/03_METHODOLOGIE_CAMPAGNE.md) §9.3 et
[`knowledge_base/by-vector/voltage-glitching.md`](knowledge_base/by-vector/voltage-glitching.md) §3.

### Première vague — minage des bibliographies (12 PDF)

**Les 12 ajouts** proviennent d'un **minage des bibliographies du corpus lui-même** : les références
fault injection citées par les 37 PDF d'origine et absentes de `docs_pdf/`, retenues par pertinence
projet plutôt que par nombre de citations, et téléchargées **uniquement depuis des sources libres**
(arXiv, IACR ePrint, HAL, USENIX, NDSS, sites de conférence).

| Ajout | Ce qu'il débloque |
|---|---|
| **O'Flynn — *Fault Injection using Crowbars*** (ePrint 2016/810) | le papier de référence du **crowbar** = Bloc B de la carte, jusqu'ici sans source `[corpus]` |
| **Controlling PC on ARM** (deck FDTC 2016) | la **formalisation d'origine** du *PC control*, en **voltage sur STM32F415RG** |
| **Zussa** (HOST 2014) | mécanisme des glitchs négatifs/positifs **mesuré au voltmètre on-chip** |
| **Carpi** (CARDIS 2013) | **stratégies de recherche de paramètres** chiffrées et comparées |
| **Yuce** (JHSS 2018) | survey côté attaquant : la taille de faute dépend de **l'instruction** |
| **Moro** (FDTC 2013) | modèle de faute **EMFI sur Cortex-M3** — la cible la plus proche d'un STM32 |
| **BADFET** (WOOT'17) | **EMFI *second-order*** ; injecteur **< 350 $** ; écueils de conception attestés |
| **Faults in Our Bus** (NDSS 2024) | fautes sur le **bus système du PCB** ; burst court/long ⇒ bus données/adresses |
| **Trouchkine** (JCEN 2021) | 4 modèles **micro-architecturaux** sur SoC 1,2 GHz sans délidage |
| **Safety != security** (deck FDTC 2017) | **efficacité chiffrée des contre-mesures** (lockstep 90 %, ECC flash 68 %…) |
| **Korak & Höfler** (deck FDTC 2014) | **cartographie par étage de pipeline** : le *skip* vit au **fetch**, la corruption à l'**execute** |
| **Ege *et al.* — *…in the Presence of Heating*** (deck FDTC 2014) | source **directe** du volet « chauffer » de la reco n°1 : le seuil **se déplace de ≈ +2,2 ns** à ΔT = 75 °C |

> Deux corrections factuelles ont découlé de ces lectures, signalées en place dans les documents :
> `docs/06` §7 attribuait à Trouchkine une attaque « sur Intel Core i3 sous Linux » (en réalité
> **BCM2837 / Raspberry Pi 3, bare-metal**), et `docs/01` affirmait qu'« aucun PDF du corpus ne décrit
> un montage crowbar ».
>
> **Korak & Höfler (FDTC 2014)**, un temps classé « non récupérable » faute de copie libre du papier
> IEEE, a finalement été **trouvé sur le site officiel de la conférence**, qui publie les decks de
> session — la même voie que pour FDTC 2016 et 2017. Son deck compagnon sur le **chauffage** a suivi.
> ⚠️ Ces deux-là portent sur le **clock glitching**, pas le voltage : ce qui s'en transpose est
> l'effet sur les **étages de pipeline** et sur les **délais de propagation**, pas le vecteur.

## Avertissement

Recherche en sécurité matérielle / fault injection à des fins d'évaluation et d'éducation. N'attaquez
que du matériel vous appartenant ou pour lequel vous disposez d'une autorisation explicite.
