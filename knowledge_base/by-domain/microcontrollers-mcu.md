# Microcontrôleurs bare-metal (STM32, AVR, MSP430, Cortex-M/M3, Renesas)

> Vecteurs employés : surtout voltage glitching, un cas EMFI (Moro/Cortex-M3). Détail
> mécanisme : [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) et
> [`../by-vector/emfi.md`](../by-vector/emfi.md).

## 1. STM32 — sémantique RDP et cibles réussies

### Readout Protection (RDP)

[corpus, Bozzato Table 1, série F3, représentative] :

| Niveau | Valeur RDP | Effet |
|---|---|---|
| Level-0 | `0xAA` (`~RDP = 0x55`) | aucune protection |
| Level-1 | toute autre valeur | debug autorisé mais flash inaccessible en bootloader/debug |
| Level-2 | `0xCC` (`~RDP = 0x33`) | bootloader **et** debug désactivés ; **irréversible** |

**Conséquence pour le modèle de faute** : passer de L2 → L1 ne demande de corrompre **qu'un
seul bit** (L1 = « toute valeur ≠ 0xCC33 et ≠ 0xAA55 ») — cohérent avec le modèle set/reset
mono-bit. **Descendre en L0 exigerait d'écrire exactement `0xAA55`** → jugé non faisable par
glitch.

### Où injecter selon la famille (mapping documenté vs inféré)

| Famille | Rail | Point d'injection | Trigger |
|---|---|---|---|
| F1 (F103) | **VDD** | vérification RDP après `Read Memory`, avant ACK/NACK | activité I/O UART |
| F3 (F373) | broche condensateur régulateur | chargement du RDP au power-up (~11 µs après boot) | front sur NRST |
| F2/F4/F7 | **VCAP1/VCAP2** (cœur 1,2–1,8 V) | selon scénario | I/O ou NRST |
| L4/G0/G4/U5 | à vérifier datasheet | **non documenté** | à caractériser |

⚠️ Le mapping « broche condensateur → VCAP » est une **inférence** à valider sur datasheet ;
Bozzato ne prononce jamais « VCAP ». Un cas réel de voltage FI sur STM32F4 existe (ci-dessous,
STM32F415RG) mais **ne confirme pas non plus** cette inférence — le deck source ne nomme
jamais le rail glitché.

### Séquence 1 — F103, bypass RDP sur `Read Memory`

1. Entrer en bootloader série (BOOT0=1).
2. Envoyer `Read Memory` sur un bloc (max 256 octets).
3. Trigger sur l'activité UART ; balayer le délai (≤ 10 ns) pour couvrir la vérification RDP
   entre commande et réponse.
4. Injecter. Si ACK au lieu de NACK → bloc renvoyé en clair. Itérer bloc par bloc.

**Résultats** : 128 kB en < 1 min, ~9 000 glitchs, ~5 % de succès, recherche 20 min,
répétabilité haute. Tension/profondeur/largeur : non données → à caractériser.

> ★ **Réglage par optimisation bayésienne** [corpus, Werner, thèse VERIMAG 2022, p. 117-119] :
> cette attaque exacte (RDP F103 par `Read Memory`) a été rejouée en réglant la **forme du glitch
> avec SMAC** (optimisation bayésienne) au lieu d'un algorithme génétique — **0,79 vs 0,37** de
> probabilité de faute à 6 000 injections, RDP contournée **2× plus vite qu'un GA** (cible mesurée :
> STM32F103RB). Méthode et garde-fous :
> [`../cross-cutting/parameter-search-methodology.md`](../cross-cutting/parameter-search-methodology.md).

### Séquence 2 — F373, downgrade RDP L2 → L1 au power-up

1. Couper puis rétablir VCC.
2. Surveiller NRST pour la sortie de POR (1,5–4,5 ms ; pull-up interne ~40 kΩ, comparateur
   conseillé pour un front net).
3. Injecter à ~11 µs après le début effectif du boot.
4. Vérifier l'accès JTAG/SWD et le bootloader.

**Résultats** : ~25 glitchs, ~4 %, recherche 2 h, répétabilité modérée. **Un dump flash
complet n'est PAS obtenu par FI seule** : la ligne correspond à un déclenchement du
downgrade. Post-downgrade, le debugger lit RAM+registres (pas le flash) → attacher pendant
une routine sensible, ou exploiter un auto-test CRC-32 au boot pour dumper pendant le calcul
(un downgrade réussi requis **par octet extrait**).

### Cas STM32F415RG — voltage FI + modèle d'exploitation

[corpus, *Controlling PC on ARM using Fault Injection*, deck FDTC 2016] : banc Riscure VC
Glitcher. *« The target is vulnerable to voltage FI »*. Modifications de cible : power cut,
retrait des condensateurs, reset, trigger. Mécanisme et chiffres (LDR vs LDMIA) détaillés
dans [`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
§5. Zone de succès = crête diagonale (profondeur × largeur, ~650–1000 ns). ⚠️ Le rail glitché
n'est pas nommé (étiqueté `vcc`) ; ne pas conclure VCAP malgré la présence de VCAP1/VCAP2 sur
la carte (broches 31/47). Cortex-M4/Thumb-2 — les encodages imprimés sont en ARM/A32, à ne
pas recopier tels quels.

## 2. AVR (ATMega, ATxmega)

- **ATMega328P** [corpus, O'Flynn ePrint 2016/810] : crowbar avec IRLML2502, durée
  d'activation pour une faute réussie **135 ns**. Détail topologie :
  [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §3.
- **ATxmega256** (8 bits, Harvard, pipeline **2 étages**) [corpus, Korak & Höfler, deck FDTC
  2014] : cartographie par étage de pipeline (clock glitching), fenêtre exploitable au fetch
  sur load/store **~12 ns** *(lu sur graphe, non imprimé)* — voir
  [`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
  §6.
- **ATmega162** [corpus, Ege *et al.*, deck FDTC 2014] : cible de l'étude « chauffage » — voir
  [`../cross-cutting/campaign-instrumentation-metrics.md`](../cross-cutting/campaign-instrumentation-metrics.md)
  §3. ⚠️ Le point 20 MHz testé est **hors spec** de cette puce (16 MHz max annoncés).

## 3. Cortex-M0 (NXP LPC1114)

[corpus, Korak & Höfler] : 32 bits, von Neumann, pipeline **3 étages**, fmax 50 MHz. Fenêtre
exploitable au fetch sur load/store **~0,5 ns** *(lu sur graphe, non imprimé)* — bien plus
étroite que sur l'ATxmega 2 étages. Un STM32 étant un cœur Cortex-M à 3 étages, **tabler sur ce régime étroit** par
analogie.

## 4. Cortex-M3 générique (EMFI)

[corpus, Moro *et al.*, FDTC 2013] : MCU 32 bits, CMOS 130 nm, Cortex-M3 56 MHz, sans cache,
Thumb-2, bus AHB-Lite. ⚠️ **La référence exacte du MCU n'est jamais donnée** — ne pas
inférer un STM32F1 malgré la coïncidence des caractéristiques. Modèle de faute EMFI complet :
[`../by-vector/emfi.md`](../by-vector/emfi.md) §1.

## 5. MSP430

[corpus, Bozzato] : **MSP430FR5725** — VDD nominal → VDD glitch **1400 mV → 880 mV**
(transitions douces). **MSP430F5172** — bypass mot de passe BSL, 32 kB, ~34 000 glitchs,
**98 %** de succès, 16 min.

## 6. Renesas 78K

[corpus, Bozzato] : extraction **SequentialDump**, 60 kB, via AGW — **3,3 M glitchs**,
2 j 12 h.

## 7. Ce qui reste hors corpus

Les familles STM32 modernes (L4/G0/G4/U5) avec protections RDP/TZEN renforcées **ne sont pas
couvertes** — les traiter en terrain inconnu. Aucun autre MCU 32 bits grand public (RISC-V,
ESP32 bare-metal hors le cas voltage ESP32/Xtensa cité en corruption d'instruction — voir
[`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
§5) n'a de séquence RDP-équivalente documentée dans ce corpus.

## 8. STM32 — deux cibles supplémentaires, dont une avec le rail nommé

★ **STM32F2 — RDP2 → RDP1 par voltage FI** [corpus, chip.fail, deck 2019]. Troisième cas STM32 du
corpus. Son apport propre n'est pas le taux mais **l'explication** : la **bootROM du STM32F2 est
lisible en RDP0** ; désassemblée, *« **no check found, all checks only for RDP0 (0xAA)** »* (sl. 130).
**Il n'existe aucun test de la valeur RDP2 `0xCC`** — la protection se réduit à une égalité à `0xAA`,
donc **faire retourner `0xAA` à une seule lecture suffit**. Le glitch vise la **lecture du RDP depuis
la NVM interne** pendant la bootROM après POR (sl. 135-136). Chronologie utile : boot **1,8 ms**, et
les **200 µs** suivant le reset séparent nettement *BootROM → lectures Flash/Option Bytes →
application* (sl. 137-144, par **analyse de consommation**). Paramètres publiés (sl. 149) :
`Delay ≈ 17900`, `Pulse = 50` — ⚠️ **unités non imprimées** (compteurs FPGA), ne pas convertir.
Exploitation : **RDP1 donne accès à la SRAM**, où les secrets ont été copiés.

★ **STM32F401CC — bypass RDP1 sur `Read Memory`** `[ref]` (Anvil Secure, `docs_pdf/writeups/`, **cité
par URL**). Le seul document du projet à **nommer le rail d'injection sur STM32** : câble soudé
sur **`VCAP_1`**,
**condensateurs de bypass dessoudés**, au motif que *VCAP_1/VCAP_2 sont directement connectés au
cœur*. Banc **ChipWhisperer-Lite CW1173**, trigger sur `USART_TX`. ★ **Offset déterminé par mesure du
protocole à l'analyseur logique**, pas par balayage : commande à **182,300 µs**, réponse à
**196,800 µs**, cycle **10 ns** ⇒ `ext_offset` ≥ **18 230** cycles ; **fenêtre utile 18 300–18 370**
(≈ **700 ns**). Firmware dumpé, script publié.

★ **STM32F411 — par EMFI** [corpus, Beckers *et al.*] : voir
[`../by-vector/emfi.md`](../by-vector/emfi.md) §9 — **sans exposer le die**, banc ≈ 40 €.

## 9. GD32 — clone de STM32, sémantique de protection identique

[corpus, Kovrizhnykh, deck OFFZONE 2023]. ⚠️ **Les trois vulnérabilités de ce deck ne sont pas du
FI** : ce sont des **conditions de course** (SWD/`NRST`, `CDBGPWRUPREQ`, DMA) ; son voltage glitcher
**échoue** (sl. 57). Ce qui en fait une entrée utile ici :

- **`OB_SPC`** : `0x5A` = aucune protection · **toute autre valeur** = niveau bas · `0xCC` = niveau
  haut, irréversible (sl. 24) — **structure identique à la RDP STM32**, sur un clone.
- **Fenêtres de course chiffrées** (sl. 51, 64) : *« more than **1600 µs** on GD32F130 vs **~20 µs**
  on GD32E230 »*, l'écart venant de la **mise en cache du flash au power-on reset** (~18 ms de délai
  sur F1x0, où les *option bytes* sont eux aussi cachés).
- **Cartographie du boot par analyse de consommation** (sl. 53-56) : identifie bootloader
  (0xC00 octets), page flash (0x400) et *option bytes* (16 octets) — même méthode que chip.fail.
- ★ **Le contrôleur employé est un RP2040 avec SWD en PIO** (sl. 35-38), parce qu'un J-Link sur USB
  a *« large floating delays »* et ne permet pas de piloter `NRST` **en synchronisme**. Voir
  [`../../docs/01_PRECONISATIONS_ARCHITECTURE.md`](../../docs/01_PRECONISATIONS_ARCHITECTURE.md).

## 10. NXP LPC — l'asymétrie de l'espace des valeurs

★ [corpus, Gerlinsky, deck RECON BRX 2017, sl. 6]. Sur **LPC1343**, **4 mots de 32 bits activent** la
Code Read Protection contre **4 294 967 292 qui la désactivent** : *n'importe quelle* corruption de ce
mot ouvre la puce. C'est l'**anti-pattern « default to unprotected »** (A6 de *Fill your Boots*) sous
sa forme chiffrée, et **la configuration la plus favorable à l'attaquant**.
⚠️ **La RDP STM32 est bâtie à l'envers** (L1 = « toute valeur sauf `0xAA` ») — mais **le downgrade
L2→L1 rejoue la même asymétrie**, et le STM32F2 de chip.fail (§8) montre le cas extrême.
Fautes observées imprimées (sl. 41, 43) : registres corrompus en `50030008` et `100003fc`, c'est-à-dire
**des adresses** — appui direct au modèle *« Address in Rd »* de Korak & Höfler. Banc : **Xmega-A1
Xplained**, code publié ; mesure par **résistance 10 Ω en série avec le GND** de la cible.
⚠️ Le cas **LPC1343 de *Fill your Boots*** est en revanche un **exploit logiciel (ROP), sans glitch** —
*« can be carried out using a standard UART-USB cable… for less than $ 5 »* (p. 8). Ne pas le compter
comme un résultat FI.

## 10bis. Cmsemicon BAT32 / CMS32 — l'asymétrie de §10, mais sur un Cortex-M0+ moderne

★ **Deuxième instance chiffrée de l'anti-pattern « default to unprotected », et la plus favorable du
lot.** Source **officielle** : *BAT32G135 用户手册* **V0.11 §28.3, fig. 28-4, p. 735** (Cmsemicon,
archivé dans `datasheet/cible_BAT32G135/`) — donc **plus solide** que le deck de §10.

| `OCDM` (`0x0050_0004`) | `OCDEN` (`0x0000_00C3`) | Niveau |
|---|---|---|
| `0x3C` | `0xC3` | **L2** — aucune opération debugger |
| ≠ `0x3C` | `0xC3` | **L1** — chip erase seul |
| — | **≠ `0xC3`** | **L0** — lecture / écriture / effacement |

⇒ `OCDEN` doit valoir **exactement `0xC3`** ; **255 valeurs stockées sur 256 donnent le Level 0** —
là où le STM32 impose un downgrade en deux temps et interdit L1 → L0.
⚠️ **Coupure de provenance à conserver** : le tableau porte sur des **valeurs stockées**. Qu'une
**lecture fautée** de `OCDEN` atterrisse en Level 0 plutôt que sur un **défaut fail-safe fermé** est
une **inférence `[reco]`**, pas le manuel — le chargement des option bytes est matériel et peut se
verrouiller par défaut sur une lecture malformée. Hypothèse de travail, à confirmer par la première
campagne.
★ **Corollaire de ciblage** : glitcher **`OCDEN`**, jamais `OCDM` (fauter `OCDM` ne donne que L1, qui
bloque toujours la lecture).

**Généralisation utile hors de ce composant** : la question à poser sur toute nouvelle cible n'est pas
« quel est le niveau de protection ? » mais **« combien de valeurs de l'octet de protection ferment la
puce, et combien l'ouvrent ? »**. LPC1343 : 4 contre 4,29 milliards. BAT32G135 : **1 contre 255**.
STM32 : 255 contre 1 — c'est le seul des trois bâti dans le bon sens.

**Autres faits domaine-génériques de cette famille** (détail complet : `docs/07`) :
- **Trois verrous indépendants** : `OCDEN`, `OCDM`, et **`DBGSTOPCR.SWDIS`** (`0x4001_B004` bit 24),
  que le *firmware* pose à l'exécution ⇒ ce troisième-là est une **course**, pas un glitch. `DBGSTR`
  expose `CDBGPWRUPREQ`/`CDBGPWRUPACK` — les signaux mis en course par le deck GD32/OFFZONE (§9).
- **Option bytes de facture Renesas RL78** (`000C0`=WDT, `000C1`=LVD, `000C2`=HOCO, `000C3`=OCD) avec
  **miroir `010C0–010C3` pour le boot swap** : si le boot swap est actif, **l'octet réellement
  consulté est `0x0000_01C3`**, et une recopie oubliée entre clusters peut laisser la puce ouverte.
- ⚠️ **`OCDM` et `BTEN` vivent dans la data flash utilisateur** (`0x0050_0004`/`0x0050_0005`) — le
  manuel avertit lui-même qu'un firmware y stockant des données peut **poser ou lever sa propre
  protection par accident**.
- **POR : dip minimal de 300 µs** sous `VPDR` (1,37–1,45 V) pour être reconnu ⇒ large marge de
  profondeur pour un crowbar, **sauf si le LVD est armé** (12 seuils, 1,88–4,06 V, option byte
  `000C1`). Mesurer le plancher d'alimentation avant de budgéter la profondeur.
- **Pas de broche `VCAP`/`REGC`, pas de `BOOT0`** : injection sur **VDD** à travers le LDO interne ⇒
  impulsions **larges** (centaines de ns à µs), pas sub-cycle.

## 11. STM8 — bootloader, multi-glitch et anti-patterns

[corpus, *Fill your Boots*] : **STM8L152C6** et **STM8AF6266** (ce dernier employé dans des
**antidémarrages automobiles**). L'*option byte* est chargé depuis **0x004800** puis comparé à
**`0xAA`** [corpus, Temeiza & Oswald, sl. 8]. Paramètres, taux et piège du multi-glitch :
[`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §8.
★ **Technique transposable** : le ***bootloader grey-box glitching*** — flasher les sections critiques
du bootloader **comme application utilisateur** pour profiler chaque glitch séparément, la cible ne
renvoyant **rien** avant le succès complet (p. 10).
★ **Verdict de portée** [corpus, Temeiza & Oswald, sl. 4] : *« To the best of our knowledge, the
**STM8 and STM32 bootloaders are secure against logical attacks** »* — **sur STM32, le FI est la
voie**, il n'y a pas d'échappatoire logicielle connue (contrairement au LPC1343).

## 11bis. Nordic nRF52 — la protection qui n'est pas lue par du code, et son correctif

> **Playbook complet et autonome** sur cette cible :
> [`../../docs/08_NRF52820_APPROTECT.md`](../../docs/08_NRF52820_APPROTECT.md) — brochage par
> boîtier, banc, oracles, campagne, budget.
> ★ **Les nRF52 se trouvent dans des produits du commerce à bas prix**, ce qui rend la **stratégie
> multi-échantillons** abordable là où une cible rare impose de réussir du premier coup : `[LR]`
> attaque une souris **Logitech G Pro** (nRF52840), et une **Logitech Signature M650** (~40 $) embarque
> un **nRF52820** (`[ref]` iFixit). ⚠️ Sur un produit lancé **après juillet 2021**, s'attendre au
> **régime durci** — acheter plusieurs unités et lire le *build code* sur chacune.
> ★★ **Et le marquage se lit sans ouvrir ni alimenter** : les **photos internes des dossiers FCC** sont
> une source publique de *build codes*. Sur le dongle **Logitech CU0021** (FCC ID `JNZCU0021`), le
> marquage `N52820 / QDAACA / 2011AA` donne `<H>` = **`C`** (régime non durci) et `<PP>` = **`QD`**
> (QFN40) — **une cible attestée, choisie sur pièce**. ⇒ ★ **Réflexe transposable à toute cible :
> chercher les *internal photos* du dossier FCC avant d'acheter.**

★ **Le seul cas de ce fichier où l'octet de protection n'est jamais lu par une instruction.**
`[ref]` LimitedResults, *nRF52 Debug Resurrection (APPROTECT Bypass)* parties 1 et 2
(`docs_pdf/writeups/`, **cités par URL, jamais par page**) :
https://www.limitedresults.com/results/nrf52-debug-resurrection-approtect-bypass et
https://www.limitedresults.com/results/nrf52-debug-resurrection-approtect-bypass-part-2

**Sémantique de protection** : `UICR.APPROTECT` à `0x10001208`, valeur `0xFFFFFF00` = protégé, POR
requis pour appliquer. Deux ports de debug : **CTRL-AP** (maître, **indépendant d'APPROTECT**, porte
`ERASEALL`) et **AHB-AP** (le seul réellement bloqué). Le retrait de protection officiel est un
`ERASEALL` via CTRL-AP — il efface Flash, UICR et RAM.

★★ **Ce qui rend le cas structurellement différent du STM32 et du BAT32** : le nRF52 **n'a pas de
bootROM**. L'initialisation des ports de debug est *« achieved by **pure Hardware**… before the CPU
start to load from Flash and execute Code »*, le contrôleur mémoire (NVMC) transférant la valeur
d'`UICR.APPROTECT` vers l'AHB-AP. **Conséquences de méthode**, toutes deux transposables :
- la fenêtre n'est **pas une routine de code** → **aucun désassemblage n'est possible**, contrairement
  au STM32F2 de §8 dont la bootROM est lisible en RDP0 ;
- elle se localise donc **uniquement par analyse de consommation** — activité Flash au trigger, **CPU
  démarrant à 19 µs**, motif NVMC isolé en comparant deux rails d'alimentation.

★ **Point d'injection : `DEC1`** — broche de découplage du régulateur interne, *« definitively the CPU
power line »*, **0,8–0,9 V** sur nRF52840 ; `DEC4` (1,2–1,3 V, alim système) sert de **trigger**.
C'est le **deuxième rail cœur nommé** du projet après le `VCAP_1` d'Anvil Secure (§8), et sur une
autre famille — voir la généralisation en
[`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §3.
★ **Nuance de découplage** : les condensateurs sont retirés (C5, C15, C16, C11) **puis un 100 nF est
RE-SOUDÉ** sur le rail cœur *« to have more stability of the CPU power during boot-up »*.
**Résultats** : glitcher maison **< 5 $** ; testé sur **nRF52840** (dev-kit et souris Logitech G Pro),
reproduit sur **nRF52832** et **nRF52833** — *« only the thin wire connected to DEC1 is sufficient »*.
**Persistance** : dump Flash + UICR → `ERASEALL` → reflash avec APPROTECT patché ⇒ ★ **une seule faute
réussie suffit à vie**, même économie que le BAT32G135 (§10bis).
⚠️ **Aucun paramètre de glitch n'est publié** (largeur, profondeur, offset) → **à caractériser**.
⚠️ **Aucun CVE n'existe.** **CVSS 7,6 (High)**, `CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H` ;
Nordic a confirmé par notice clients du **12 juin 2020**.

### Le correctif — et pourquoi il change le verdict selon l'exemplaire

Source **officielle** : *nRF52820 Product Specification* **v1.3 §4.8.2, p. 41** (Nordic, archivée dans
`../../datasheet/cible_nRF52820/`). Le write-up conclut *« the vulnerability resides in Silicon. There
is no way to patch without HW revision »* — ★ **Nordic a fait la révision**, et la PS la documente :

| Régime | Par défaut | Pour que le debug reste ouvert |
|---|---|---|
| *build codes* **`Cxx` et antérieurs** — « controlled by hardware » | **désactivée** | ne rien écrire dans `UICR.APPROTECT` |
| *build codes* **`Dxx` et ultérieurs** — « controlled by hardware **and software** » | ★ **activée** | `UICR.APPROTECT = HwDisabled` **ET** le firmware écrit `APPROTECT.DISABLE = SwDisable` (`0x5A`) |

Registres, base `0x40000000` : `FORCEPROTECT` (offset `0x550`) et `DISABLE` (offset `0x558`).
`DISABLE` est **remis à zéro à chaque pin / power / brownout / watchdog reset** et au réveil de
System OFF. Durcissement recommandé par Nordic : `UICR.APPROTECT = Enabled` **plus** un firmware
écrivant `FORCEPROTECT = Force`.

★★ **Le régime se détermine avant toute campagne, à la loupe.** Le marquage boîtier (Figure 166,
§10.1) porte `<PP><VV><H><P>`, et la PS précise que *« only the **first two characters** of the
function variant code are used »* ⇒ **la lettre `<H>` (build code) est lisible sur la puce, le suffixe
`-D` ne l'est pas**. Sur un composant déjà soudé, `<H>` est **le seul** discriminant : `C` ou
antérieur ⇒ une seule faute suffit ; `D` ou ultérieur ⇒ verrou matériel **et** logiciel.
★ Second indice, indépendant : **`DEC5` est non connecté sur les *build codes* `Dxx` et
ultérieurs** (fait sourcé) ⇒ l'absence de condensateur sur cette broche est un signe lisible sur la
carte — mais c'est une **inférence `[reco]`**, un intégrateur pouvant avoir omis ce découplage pour
une autre raison.
⚠️ **Deux identifiants distincts que la PS ne relie jamais** : §4.8.2 indexe le régime sur le **build
code `<H>`**, la **Table 144** (§10.4) sur le **code de variante fonctionnelle `<VV>`** (`AA` =
*controlled by hardware*, `AA-D` = *hardware and software* ; références réelles `nRF52820-QDAA-D-R7`,
`nRF52820-CFAA-D-R7`). La corrélation `AA-D ↔ Dxx` est **plausible mais non imprimée** → `[reco]`.

**Brochage utile** (même source) : **QFN 5×5 mm, 40 broches, pas 0,4 mm** → **broche 1 = `DEC1`,
« 1.1 V Digital supply decoupling »** · **WLCSP 2,531 × 2,531 mm, 44 billes, pas 0,35 mm** → **bille
A7 = `DEC1`** · `DEC4` = 1,3 V (broche 38 / bille A5, à relier à `DEC6`) · 256 kB Flash / 32 kB RAM.
⚠️ **Ne pas fusionner deux tensions** : `DEC1` vaut **0,8–0,9 V mesurés** par LimitedResults sur
**nRF52840** et **1,1 V spécifiés** par la PS sur **nRF52820** — puces différentes, mesuré vs spécifié.

### ★ Ce que ce cas apporte à la question *fail-safe* du §10bis — les deux branches

Le §10bis laisse en `[reco]` l'hypothèse qu'une **lecture fautée** d'un octet de protection chargé
**en pur matériel** atterrisse en niveau ouvert plutôt que sur un **défaut fail-safe fermé**. Le nRF52
fournit **un précédent dans chaque sens**, et il faut citer les deux :

- **`Cxx` — précédent favorable** : une initialisation de port de debug **purement matérielle**,
  glitchée, **échoue ouvert**. C'est la première attestation empirique du projet que ce type de bloc
  peut se comporter ainsi.
- **`Dxx+` — contre-précédent** : le même fondeur a **délibérément redessiné** le bloc en
  **fail-safe closed** par défaut. Un tel bloc *peut* donc parfaitement se verrouiller.

⇒ **L'hypothèse du §10bis reste `[reco]`** : elle gagne un précédent nommé **et** un contre-précédent
nommé, pas une source.
★ **Inversion de course à noter** : sur BAT32, `DBGSTOPCR.SWDIS` part **ouvert** et le firmware ferme
⇒ course en faveur de l'attaquant. Sur nRF52820 `Dxx+`, la protection part **fermée** et le firmware
ouvre ⇒ **pas de course équivalente**, et **deux fautes** sont nécessaires — la pénalité multi-glitch
de *Fill your Boots* (36× sous le produit des taux) s'applique alors, voir
[`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §8.

⚠️ **Portée à ne pas outrepasser** : les seules puces **réellement fautées** sont **nRF52840,
nRF52832 et nRF52833**. La liste des six versions vulnérables (52810, 52811, **52820**, 52832, 52833,
52840) accompagne la phrase *« NordicSemiconductor confirmed all their nRF52 versions are
vulnerable »* — la **revendication est de Nordic**, la **liste est du write-up**, et le **nRF52820 est
couvert par architecture commune, pas par mesure**.

> ★ **Un second banc public existe, et il publie un point de fonctionnement.** Le fork
> `iceman1001/raiden-pico` (`[ref]`, @ `90b547e`, **non compté dans les 68**) monte exactement cette
> attaque sur **nRF52840** et apporte cinq faits que LimitedResults tait : garde-fou **`NVMC ERASEALL`**
> (largeur clampée ≤ 450 cyc), ***cold-boot-only*** (le LDO tient `DEC1` en régime établi ⇒ seule la
> rampe froide est glitchable), **bouton d'amplitude par la résistance de source** du MOSFET, oracle par
> **lecture `FICR.INFO.PART`** (APPROTECTSTATUS jugé peu fiable), et **bypass transitoire**. ⚠️ Chiffres
> **du nRF52840, banc tiers** ⇒ **pas un `[fait]`**, et ils **ne comblent pas** le vide « aucun paramètre
> publié » du nRF52820. Développé dans
> [`../../docs/08_NRF52820_APPROTECT.md`](../../docs/08_NRF52820_APPROTECT.md) §3bis. EFM32LG et PIC18 du
> même fork : §13.

## 12. Familles supplémentaires attestées `[ref]` (write-ups)

Protection en lecture contournée **par voltage FI** sur : **EFM32 Gecko** (Silicon Labs) ·
**Nuvoton M2351** (**ARMv8-M TrustZone**) · **SAM4C32** et
**SAM E70/S70/V70/V71** (Microchip) · **RH850/P1M-E** et **RH850/F1L** (Renesas automobile) ·
**RX65** · **RL78** (syscon PS4) · **CC2510** (TI) · **LPC1343** (toothless, 3 parties).
⚠️ Tous **`[ref]`** — `docs_pdf/writeups/`, cités par URL, jamais par page.
**Leur valeur est statistique** : le cas STM32 n'a rien d'une exception.
★ **Le nRF52 ne figure plus dans cette liste** — ses deux write-ups ont été lus intégralement et sont
développés en §11bis.

## 13. EFM32LG & PIC18 — deux cibles outillées par le fork raiden `iceman1001` `[ref]`

> **Nature : `[ref]`** — docs d'outil du fork `iceman1001/raiden-pico` (`feat/unique-dump-paths`
> @ `90b547e`), cité par URL SHA-figée, **non compté dans les 68**. Même moteur crowbar RP2350 que ce
> projet. ⚠️ **3ᵉ raiden**, distinct de l'upstream AdamLaurie et du fork local v0.14. Le volet
> **nRF52840** du même fork est traité en §11bis et dans
> [`../../docs/08_NRF52820_APPROTECT.md`](../../docs/08_NRF52820_APPROTECT.md) §3bis.

### EFM32LG Leopard Gecko (Silicon Labs, Cortex-M3 @ 48 MHz)

L'**analogue EFM32 de l'APPROTECT nRF et de la RDP STM32**, dit tel quel par la source. Le debug est
verrouillé par un **Debug Lock Word (DLW)** en page de lock-bits (`0x0FE0_4000`), **latché par le MSC
pendant `tRESET ≈ 163 µs`** au boot. Un crowbar sur **`DECOUPLE`** (sortie du LDO cœur ~1,8 V) pendant
cette fenêtre faute l'évaluation du DLW ⇒ l'**AHB-AP** remonte *enabled* et la flash se lit en SWD
**sans** déclencher l'effacement de masse. Points réutilisables :

- **`DECOUPLE` est un 4ᵉ rail cœur nommé**, après `VCAP` (STM32), `DEC1` (nRF52) et « aucune » (BAT32) —
  voir la généralisation [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §3.
- **Recovery officielle = AAP `DEVICEERASE`** : elle efface tout et **ne lit jamais** (même rôle que
  l'`ERASEALL` CTRL-AP du nRF52 en §11bis, ou le chip-erase du BAT32 en §10bis) — voie destructive, pas
  l'attaque.
- **`VDD` abaissé à ~2,0 V** pour un dip plus net ; ⚠️ garder l'impulsion **sub-µs** pour qu'un reset
  BOD propre (seuil 1,74–1,96 V) n'avorte pas la tentative.
- ⚠️ **`DPIDR 0x2BA01477` ne confirme aucune puce** : iceman le classe lui-même en *caveat à vérifier
  au banc*, et c'est la valeur **SW-DP générique Cortex-M3/M4** (partagée STM32F1 / LPC17xx) — **la même
  que celle que ce fork lit sur sa cible nRF52**. L'identification positive est la lecture du mot
  *Device-Info PART*. **Même piège d'oracle** que la leçon « valider l'instrument » de
  [`../../docs/03_METHODOLOGIE_CAMPAGNE.md`](../../docs/03_METHODOLOGIE_CAMPAGNE.md) §1.1.
- ⚠️ **Distinct du write-up LimitedResults EFM32** de §12 : deux sources, une même famille.

### PIC18 (Microchip) — cible neuve, modèle de faute distinct

Le PIC18 n'a **ni SWD ni UART** : la mémoire programme passe par **ICSP** (horloge PGC + donnée PGD +
MCLR/VPP). ★ **Le modèle de faute n'est pas un creux de rail cœur** : quand les bits de code-protect
(`CONFIG5L`) sont posés, une lecture de table d'un bloc protégé rend **`0x00`** — la donnée **est bien
chargée dans le table-latch**, la protection ne faisant que **gater sa sortie sur PGD**. L'attaque
**faute ce gate pendant le clock-out de lecture** ⇒ le vrai octet apparaît. Faits réutilisables :

- **Crowbar sur `VDD`** — le PIC18 **n'expose aucune broche de rail cœur**, comme le BAT32G135
  (§10bis) : c'est la **branche « aucune »** de
  [`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §3. ★ Mais noter que le
  **but du glitch diffère** : gater une sortie d'E/S, pas sous-alimenter un cœur.
- **Entrée LVP sans haute tension** : clé 32 bits `"MCHP"` sur PGD **ou** broche RB5/PGM maintenue
  haute (deux variantes selon le silicium), **pas de VPP 9–13 V** — accès par simples GPIO.
- **Économie « une cellule, un dump »** : rendement single-shot **~0,24 %**, mais la gate est
  **ré-évaluée par octet** ⇒ une bonne cellule (delay, width) se **rejoue adresse par adresse** pour la
  mémoire entière — même logique que « une faute réussie suffit » ailleurs dans ce fichier.
- ⚠️ **L'analogue optique** (bunnie, *Hacking the PIC 18F1320*) est **écarté du corpus** en
  [`../../docs/04_REFERENCES.md`](../../docs/04_REFERENCES.md) §F comme **non-FI** (UV) ; ce cas-ci est
  **voltage/ICSP**, vecteur différent — pas de contradiction.

---

## ★ Ce qu'une protection en lecture ferme VRAIMENT — quatre faits mesurés `[fait]`

> **Provenance : `[fait]`** — campagne BAT32G135 (Cortex-M0+), 2026-08-31 → 09-07, détail dans
> `docs/07` §2bis / §2ter / §5.2bis. Cible mesurée : un capteur **TP-Link Tapo T310**.
> ⚠ Ce sont des faits **de cette puce** ; ce qui se généralise est la **question à poser**, pas la
> réponse.

### 1. La protection peut ne couvrir QUE la flash — et la SRAM devient une brèche

Au niveau intermédiaire (« chip erase autorisé, lecture interdite »), mesuré **dans le même run, au
même instant** :

| Cible | Résultat |
|---|---|
| Flash `0x0000_0000` | ❌ **FAULT** |
| **SRAM `0x2000_0008`** | ✅ **lue**, valeur réelle |
| 64 octets en `0x2000_0000` | ✅ contenu complet, **identique au niveau 0** |

★ **Pourquoi ça compte** : le code de démarrage C **recopie la section `.data` depuis la flash vers
la SRAM à chaque boot**. Lire la SRAM restitue donc du **contenu d'origine flash sans jamais lire
la flash**. ⇒ **question à poser sur toute cible** : *la protection couvre-t-elle la RAM, ou
seulement la mémoire non volatile ?*

⚠⚠ **Mais le contre-exemple est sur la MÊME puce, et il annule la brèche.** Test : SRAM badigeonnée
d'un motif connu, reset, relecture → **255 mots sur 256 intacts**, et le cœur **en blocage dès le
reset**. **Au niveau intermédiaire, sonde attachée, ce cœur ne démarre pas** ⇒ **aucun `.data`
recopié, donc aucune fuite**. ⚠ Une rédaction antérieure annonçait « 104 puis 187 octets lisibles » :
**c'était un résidu de l'époque non protégée** — la SRAM conserve son contenu bien en dessous de ce
qu'un reset provoque. ⇒ **toujours badigeonner la RAM avant de conclure à une fuite.**

### 2. La protection peut viser le CŒUR, pas seulement le debugger

L'idée d'injecter un **payload en RAM** exécuté par le cœur — qui, lui, « a le droit » de lire la
flash puisqu'il s'exécute dessus — **a échoué**. Sonde différentielle (§C de
`cross-cutting/campaign-instrumentation-metrics.md`) : la lecture de flash **par le cœur** produit
une **erreur de bus**, exactement comme une adresse non mappée. ⇒ **ne pas supposer que le cœur est
privilégié** ; le vérifier, et s'attendre à ce qu'il ne le soit pas.

★ **Question ouverte qui en découle, et qui vaut pour toute puce vendue protégée** : *si le cœur ne
peut pas lire sa flash, comment le produit du commerce démarre-t-il ?* Hypothèse la plus économique
(**non testée**) : le verrou est conditionné à la **présence du debugger** (`C_DEBUGEN`, ou la mise
sous tension du domaine de debug). Test gratuit : **reset sans jamais connecter la sonde**, puis
observer la consommation.

### 3. Le port de debug survit au reset, pas le bus derrière lui

En pré-armant l'accès mémoire **avant** le reset et en ne tirant qu'une lecture après :

| Délai après relâche du reset | Résultat |
|---|---|
| 0 → **440 µs** | lecture **OK**, mais renvoie `0x00000000` — **y compris sur la RAM** |
| **450 µs** et au-delà | valeur réelle (niveau 0) · **FAULT** (niveau protégé) |

Transition **franche**, 9 tirs de chaque côté, **aucune dispersion**. ⇒ ★ **il n'y a pas
d'interstice** : la protection se verrouille **exactement** à l'instant où la mémoire devient
accessible. ⚠ **Et la fenêtre de zéros n'est pas un « réveil de la flash »** — la RAM aussi rend
zéro : c'est **le système entier maintenu en reset**, le port de debug survivant mais pas le bus.
⇒ **arriver plus tôt ne sert à rien**, et c'est un résultat NÉGATIF à connaître avant d'investir
dans une course.

### 4. Un effacement « total » peut épargner une zone — vérifier avant de s'y fier

Après un **chip erase** réussi, la flash de code était uniformément vierge mais la **flash de
données** contenait toujours son enregistrement d'appairage, **identique octet pour octet** au dump
d'avant. ⇒ deux conséquences opposées : **on ne perd pas l'appairage** en déverrouillant par
effacement, mais **on ne l'efface pas non plus** en croyant tout nettoyer. L'effacement de la zone
de données demandait une **commande distincte** (effacement par secteur).

★ **Et la granularité d'écriture se lit chez le fondeur, pas dans la doc de reverse** : le driver
officiel programme **octet par octet**, là où le manuel laissait croire à des mots de 32 bits. C'est
ce qui permet de réécrire **un seul octet d'option** sans toucher aux octets voisins qui partagent
son mot.

### 5. Un bootloader peut vivre en flash sans aucune ROM

Sondage de l'espace d'adressage (47 adresses, cœur halté) : **aucune ROM de boot**, table ROM
CoreSight standard à **3 entrées** sans composant propriétaire. Mais un **bootloader A/B** occupe la
flash — slot A en `0x0000`, slot B en `0x8000` — avec la séquence canonique de passation
(désassemblée) : masquage des interruptions → installation du SP de l'application → **écriture de
`VTOR`** → saut. ⇒ **« pas de ROM » ne veut pas dire « pas de bootloader »**, et le `VTOR` du slot A
prouve au passage que le cœur **implémente** la relocalisation de vecteurs — information réutilisable
pour y poser un gestionnaire d'exception en RAM.

⚠ **Piège de sondage** : les lectures **hors cartographie ne fautent pas toujours** — elles rendent
la **dernière donnée vue sur le bus**. Test qui tranche : lire **deux amorces de contenu différent**
juste avant la même sonde ; si la sonde suit l'amorce, **il n'y a pas de mémoire là**.
