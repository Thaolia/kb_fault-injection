# EMFI (Electromagnetic Fault Injection)

> Vecteur **sans contact** : une bobine placée en champ proche décharge une impulsion HT
> brève, induisant des courants transitoires localisés → faute. Cibles réelles documentées :
> [`../by-domain/`](../by-domain/) (Android/Linux, automobile, IoT, x86/serveur).

## 1. Modèle de faute — un débat en trois temps, pas une contradiction

| Vs. voltage/clock | EMFI |
|---|---|
| violation de setup → **set/reset** | **« sampling faults »** (perturbation de l'échantillonnage des bascules) |
| effet **global** | effet **local** (positionnement XY) |
| vu par les détecteurs globaux | **échappe** aux détecteurs globaux [corpus, DATE 2014] |

[corpus, Ordas 2015, FDTC] — modèle de référence : les fautes EMFI sont des bitset/bitreset,
mono- ou multi-octets, selon la **polarité/orientation** de la sonde, et **locales**.

★ **Ce modèle reste valide « au niveau du die »**, mais trois ajouts montrent des fautes EM
dont le **siège est ailleurs** — une chronologie de raffinement, pas une contradiction à
trancher :

1. **Moro 2013** [corpus, FDTC 2013] — sur Cortex-M3, l'EM produit une **faute de timing sur
   le transfert de bus depuis la Flash** (`HRDATAI`/`HRDATA`), parce que la Flash répond plus
   lentement que la SRAM et arrive en fin de cycle. **Aucune faute injectée sur un transfert
   SRAM.** Détail cible : [`../by-domain/microcontrollers-mcu.md`](../by-domain/microcontrollers-mcu.md).
2. **Ordas 2015** conteste : ce ne sont pas des fautes de timing mais des *sampling faults*.
3. **Nabhan 2024** [corpus, IOLTS] réconcilie par **deux voies de couplage** : PDN (→
   voltage glitch) et clock tree (→ glitch d'horloge induit).

Deux ajouts supplémentaires montrent que le siège de la faute peut être **hors du die** :
**BADFET** (DRAM voisine, §3) et **Faults in Our Bus** (pistes du bus PCB, §4) — aucun des
deux ne mesure la dépendance à la polarité prédite par Ordas.

## 2. Avantage structurel — pourquoi ajouter ce vecteur

| Critère | Voltage/clock | EMFI |
|---|---|---|
| Contact | oui (rail/horloge) | **non** (champ proche) |
| Spatial | global | **local** |
| Détecteurs | vus | **échappe** aux détecteurs globaux |
| Boîtier fermé | souvent impossible sans modification | **traverse potting/encapsulation** conformes |

[ref, talk Hackfest LeClair 2026] : la bobine peut viser le dessous du PCB à travers un
boîtier plastique fermé ; son faisceau étroit ne perturbe en principe pas le reste de la
carte, contrairement au voltage glitch qui affecte le rail global. Ancrage `[corpus]` du
« touchless » : [corpus, BADFET p. 2] : *« numerous EMFI attacks can be leveraged against
COTS devices non-invasively and in an air-gapped manner »*.

**Justification `[corpus]` de l'EMFI comme vecteur de repli** [corpus, Yuce p. 14] : *«
Voltage glitching is typically the simplest method, this is often prevented by sensors.
Alternative methods like EM and optical glitching are more complex, but also harder to
prevent. »*

## 3. EMFI *second-order* — fauter un composant pour en exploiter un autre

[corpus, Cui & Housley, BADFET, USENIX WOOT'17] : au lieu de modéliser la cible comme *un*
ordinateur, la modéliser comme **une collection de composants synchrones indépendants**
reliés par des interconnexions (i2c, SPI, AXI). Le 1ᵉʳ ordre faute un composant et exploite
la faute *dans ce composant* ; le **2ⁿᵈ ordre faute un composant pour exploiter la
conséquence chez un autre**. Bénéfice revendiqué : **effondrer les exigences de résolution
spatiale ET temporelle** de l'injecteur.

- **Mise en œuvre démontrée** : corruption **non ciblée** de la DRAM (à ~19 mm du CPU, donc
  sans exigence de résolution spatiale) → crée une condition d'erreur normalement
  inatteignable dans un bootloader → accès CLI → exploitation logicielle en aval. Détail
  cible : [`../by-domain/desktop-server-x86-highfreq.md`](../by-domain/desktop-server-x86-highfreq.md).
- **Paramètres** : une impulsion de **10 µs à 300 V**, sonde à **3 mm**, **72 succès/100**.
- **Injecteur < 350 $** (280 A @ 300 V ; 54 A @ 1100 V), contrôlé par microcontrôleur
  embarqué — voir [`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md).
- ★ **Écueils de conception attestés** (transférables à tout injecteur EMFI DIY) : un banc de
  MOSFET bas coût en série avec la sonde **échoue par effet Miller** ; il faut un **gate
  driver opto-isolé** en série avec un driver fort courant, sans quoi l'EMF émis
  **re-déclenche l'impulsion** ; une **diode flyback alignée avec la sonde** est
  indispensable ; **ne jamais laisser le condensateur se décharger entièrement dans les
  MOSFET** (destruction + latching permanent) ; PCB symétrique, boucle de décharge minimale,
  grand plan de masse.
- **Sondes testées** (non attribuées à l'attaque finale) : 13 spires fil émaillé 54 mil ; même
  + noyau ferrite Ø 10×25 mm ; 8 spires fil 25 mil en rectangle 22×17 mm — toutes SMA femelle.

## 4. Fautes de bus système — une classe de modèle inédite

[corpus, Mishra, Chakraborty, Mukhopadhyay, *Faults in Our Bus*, NDSS 2024] : l'impulsion
vise **les pistes du bus système sur le PCB**, entre processeur et mémoire — ni le CPU ni la
mémoire (*« the processor is beyond the field of influence of our probe »*, p. 7). Avantage :
contourne les contre-mesures anti-fautes du processeur, évite les fautes mémoire persistantes
(Rowhammer).

- ★ **La longueur de burst sélectionne le bus fauté** : **~20 impulsions → bus de données**,
  **~100 impulsions → bus d'adresses**. C'est un bouton de contrôle du **type** de faute, pas
  seulement de son intensité.
- **« Register sweeping »** : les fautes de bus de données font passer un registre 32 bits
  entier de non-nul à `0x0`. Taux mesurés (10 000 injections) : **62 %** de données
  corrompues (bus données), **31 %** (bus adresses) — très au-dessus des 1–5 % habituels,
  ne pas généraliser hors de ces cibles. Seuls les 16 bits de poids fort sont fautables ;
  aucune asymétrie 1→0/0→1 mesurée (contraste avec Ordas 2015).
- **Banc = chaîne RF, pas décharge capacitive** — voir
  [`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md) §5.
- **Trigger non invasif par analyse de consommation** : le motif de calcul d'une vérification
  RSA est reconnaissable sur une trace de courant, sans instrumentation du code.
- Cible/exploitation détaillées : [`../by-domain/linux-android-arm-socs.md`](../by-domain/linux-android-arm-socs.md).

## 5. Paliers de tension et sondes

Voir [`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md)
§3 pour les paliers A (~250 V)/B (~500 V)/C (~1 kV), les outils commerciaux (PicoEMP,
FaultyCat, ChipShouter, SiliconToaster) et les budgets DIY chiffrés.

**Construction de sonde** [ref] : noyau ferrite + fil émaillé + connecteur SMA. Taille :
pointes fines (~1 mm) pour la résolution spatiale, larges (~4 mm) pour l'énergie. **La
polarité CW/CCW change le signe du champ** — toujours tester les deux (corrobore le modèle
de faute polarité-dépendant d'Ordas 2015 ; confirmé empiriquement sur ECU réel, voir
[`../by-domain/automotive-ecu.md`](../by-domain/automotive-ecu.md)).

## 6. Méthodologie de balayage spatial

[ref, talk Hackfest LeClair 2026] — procédure de reconnaissance XY avant toute tentative
d'exploitation : geler le CPU cible, écrire des valeurs connues en RAM et dans les registres,
injecter un pulse à une position (X, Y), relire, comparer à la valeur attendue, marquer la
position « sans effet » / « RAM modifiée » / « registre modifié ». Répété sur une grille (pas
typique ~0,5–1 mm, non recoupé indépendamment) → carte des zones actives **avant**
exploitation. Cible de calibration de sonde dédiée à cet usage :
[`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md) §6.

Scoring **par position** en 5 catégories, logique proche du scoring général — voir
[`../cross-cutting/campaign-instrumentation-metrics.md`](../cross-cutting/campaign-instrumentation-metrics.md).

## 7. Faisabilité sur cibles complexes/hautes fréquences

Voir [`../by-domain/desktop-server-x86-highfreq.md`](../by-domain/desktop-server-x86-highfreq.md)
pour le dossier complet (obstacles IHS/jitter de cache-miss/découplage, ce qui reste
attaquable, et l'erreur d'attribution corrigée entre Trouchkine/JCEN2021 et le x86/WISTP2019).

## 8. Sécurité — non négociable au-delà de 250 V

À 250 V comme à 1 kV, l'énergie stockée peut être **létale** et le condensateur **reste
chargé après coupure**.

1. **Résistance de purge (bleed)** en permanence en parallèle du condensateur ; décharge
   active + vérification au multimètre avant toute manipulation.
2. **Côté HT flottant/isolé** ; isolation validée par **hipot** (ex. 1000 V DC, fuite
   < 1 µA/60 s).
3. **Interlock matériel + logiciel** : armement bas par défaut, LED « HV present », capot
   fermé requis pour charger.
4. **Règle une main** ; jamais de sonde/doigt sur le côté HT sous tension.
5. `E = ½·C·V²` : recalculer l'énergie et dimensionner purge/isolation en conséquence à
   chaque palier de tension.
6. Firmware : purge automatique sur perte de liaison ou timeout ; ne jamais laisser le
   condensateur chargé au repos.
7. [ref] La charge résiduelle d'une pointe EMFI peut persister **des minutes** après
   coupure ; toujours couper, débrancher, attendre avant de manipuler une sonde, et isoler
   ses connexions sous plusieurs couches de gaine/ruban isolant.

## 9. Conception de l'injecteur — le seul jeu de paramètres sourcé

[corpus, Beckers *et al.*, *Design Considerations for EM Pulse Fault Injection*, imec-COSIC].
⚠️ **Papier distinct** du survey `290093.pdf` des mêmes auteurs. C'est le **seul document du corpus
qui dimensionne un injecteur EM** au lieu d'en décrire un fini, et ★ **sa cible est un STM32F411
(NUCLEO-F411RE), en non invasif, sans exposer le die** (p. 12-13) — le seul EMFI sur STM32 connu ici.

| Élément | Valeur | Page |
|---|---|---|
| Coût d'assemblage complet | **≈ 40 €** | p. 12 |
| Sonde | barreau **ferrite Ø 750 µm**, **4 spires**, fil émaillé **150 µm** | p. 12, p. 6 |
| Matériau de ferrite | **Fair-Rite « 67 »** — choisi pour la **haute fréquence**, malgré la plus faible amplitude | p. 7 |
| Condensateur de décharge | **`C1` = 1000 pF** (dimensionné sous SPICE pour 10 ns) | p. 12 |
| Amortissement | **`R3` = 10 Ω** (léger sur-amortissement) · **1 Ω** (sous-amorti) | p. 12-13 |
| Largeur obtenue | **12 ns** au premier montage → **10 ns** en abaissant `C1` | p. 12 |
| Commande MOSFET | grille **12 V**, `VGS(th)` **3 V**, **`R2` = 0,22 Ω** ⇒ courant **borné à 40 A** par auto-limitation | p. 12 |
| Cadence max | ≈ `4·R1·(C1 + C_parasite)` | p. 14 |
| Implantation | **boucle RLC haute intensité la plus petite possible** | p. 12 |

★ **Le résultat le plus actionnable : l'amortissement fixe la sélectivité temporelle.** À sonde,
position, tension et instant **identiques**, seul `R3` change :
**amortissement critique (10 Ω)** ⇒ on faute **une écriture individuelle** (registre par registre
d'une instruction `STM`) ; **sous-amorti (1 Ω)** ⇒ les **oscillations harmoniques allongent
`t_sensitive`** et **plusieurs instructions sont fautées simultanément** (p. 13-14).
C'est l'exact analogue EMFI du *sharping / addition* de Zussa côté voltage
([`voltage-glitching.md`](voltage-glitching.md)) : **la finesse vient de la réponse du circuit, pas
du tick du contrôleur**.

**Relations de conception de sonde** (p. 8) : spires ↑ ⇒ inductance en **N²** ⇒ **amplitude ↓,
largeur ↑** (le champ ne croît que linéairement) ; diamètre de noyau ↑ ⇒ amplitude ↓.
⇒ **petite sonde, peu de spires = impulsion la plus courte et la plus intense.**

★ **Caractérisation d'une sonde avant campagne** (p. 6) : la mesurer au-dessus d'une **ligne
microstrip 50 Ω** (FR-4 0,3 mm, cuivre 18 µm, εr 4,7, largeur 0,532 mm), balayée au **pas de 15 µm**.
Elle donne **à la fois** résolution spatiale et forme temporelle — une antenne boucle ne capture
**pas** la résolution spatiale.

**Protocole de test réutilisable** (p. 13) : instruction `STM` écrivant r0–r9 à **`0x55555555`**
(motif alterné, pour capter indifféremment bit-set / bit-reset / bit-flip), trigger GPIO, balayage
**100 ns par pas de 1 ns**, **100 impulsions par pas**, après scan complet de la surface.

⚠️ **Limites** : aucun **taux de succès** publié pour la campagne STM32 ; l'étage de caractérisation
travaille en **basse tension** (tube à décharge gazeuse de claquage **370 V**, condensateur à 400 V,
p. 5-6) — ce papier **ne dimensionne pas** un étage 1 kV, qui reste le SiliconToaster.

## 10. Choisir l'EM parce que le rail n'est pas manipulable `[ref]`

★ **Critère de choix de vecteur, imprimé et directement réutilisable**
[Riscure, *Glitching the KeepKey hardware wallet*, **STM32F205**, `docs_pdf/writeups/`, **`[ref]`**] :
*« Due to the fact that **USB is used for both communication and powering the device**, **EMFI was
used** since it increases the chances of successful glitching »*.

**Quand la cible tire son alimentation du même lien que celui qui sert à communiquer** (USB, PoE,
harnais unique), **le rail n'est pas librement manipulable** : couper ou creuser `VCC` casse la
liaison, donc le trigger et l'observation. **L'EMFI devient alors le vecteur praticable**, et il
contourne au passage la **détection de clock glitching** que cette cible implémente.
⇒ **Critère à appliquer avant de choisir entre crowbar et module EM**, au même titre que « la cible
est-elle sous potting ? » (§1) ou « le découplage est-il retirable ? ».
Méthode employée : **scan spatial complet** de la puce pour localiser les zones sensibles, puis
glitch de `memcpy` juste après le paquet USB. Chaîne d'exploitation en
[`../../docs/03_METHODOLOGIE_CAMPAGNE.md`](../../docs/03_METHODOLOGIE_CAMPAGNE.md) §9.3.

## 11. Le même bug par EM plutôt que par tension `[ref]`

*Raelize — Espressif ESP32: Bypassing Secure Boot using EMFI* (`docs_pdf/writeups/`, **`[ref]`, cité
par URL, jamais par page**). Les auteurs **reproduisent CVE-2019-15894 par EMFI** là où la
publication d'origine utilisait du **voltage** — *« a similar hardware vulnerability »*. Sonde
**Riscure EM-FI Transient Probe** ; ★ **seule modification de la cible : le retrait du capot
métallique** du module ESP32-WROOM-32. Paramètres désignés comme décisifs : **position, puissance,
timing**.

★ **Nuance d'outillage à retenir** : ils jugent le résultat atteignable *« using low cost (e.g.
ChipShouter) or Do-It-Yourself (e.g. BADFET) tooling as well »*, **mais** *« this type of tooling may
be limiting and is often **not able to sufficiently sweep the glitch parameter search space** …
once … the required glitch parameters are known, **low cost tooling may be tuned or built** »*.
⇒ **Un outil bas coût rejoue des paramètres connus ; il ne découvre pas efficacement un espace
inconnu.** C'est le partage des rôles à appliquer entre un banc professionnel et un
PicoEMP/FaultyCat.

---

## ★ EMFI sur bootloader LPC1114 — un jeu de paramètres publié `[fait]`

> **Provenance : `[fait]`**, banc réel du 2026-10-28 ; artefacts dans `tplink_tapo-20260909.tgz`
> (`raiden-pico/SUCCESS_FOUND.md`, `GLITCH_TEST_RESULTS.md`). Détail : `docs/06` §1.8.

**Cible** : bootloader d'un **NXP LPC1114** (Cortex-M0) — plateforme déjà connue du corpus par la
cartographie de pipeline de Korak & Höfler, et famille dont la protection en lecture est le sujet du
deck Gerlinsky. **Résultat** : la commande de sécurité renvoie **`0`** au lieu de l'erreur `19`.

| Paramètre | Valeur |
|---|---|
| Tension de bobine | **290 V** |
| Délai après trigger | **0 cycle** (impulsion immédiate) |
| Largeur | **150 cycles = 1,00 µs** |
| Trigger | octet **UART `0x0D`** |
| Sur 10 tirs | **1 succès (10 %)** · 5 crashs · 4 réponses normales |

⚠⚠ **Deux garde-fous sans lesquels ces chiffres induisent en erreur :**
1. ★ **290 V est une tension de BOBINE, pas une profondeur de creux sur un rail.** Le vecteur est
   l'EMFI (banc ChipSHOUTER) — confondre les deux rendrait le chiffre absurde.
2. ⚠ **n = 10.** À ne pas comparer aux 22 % de Fraunhofer ni aux 72/100 de BADFET, campagnes
   autrement plus larges.

★ **Ce qui vaut le plus ici n'est pas le résultat mais la STRATÉGIE** : l'exploration a attaqué
l'axe d'amplitude **par la descente** (partir d'une tension qui crashe à 100 %, descendre jusqu'à
0 %, puis remonter par pas fins — le succès est au bord de la zone de crash). Méthode générale et
ses réserves dans `cross-cutting/parameter-search-methodology.md`.

## Trois modèles/outils EMFI ajoutés avec la bibliographie de la thèse Werner

★ `[corpus]` **Rivière *et al.* (HOST 2015)** — EMFI sur le **cache d'instruction d'un ARMv7-M**
(Cortex-M, classe STM32), modèle de faute **précis à 96 %**, **source du `4CacheCorruption`** (cf.
`cross-cutting/fault-models-mechanisms.md`). **Proy *et al.* (arXiv 2019)** — EMFI sur **cœur
superscalaire out-of-order** (Cortex-A9) : classification ISA avec effets propres aux cœurs complexes
(substitution d'opérande, corruptions de registres corrélées, détournement de flot). **Madau *et al.*
(CARDIS 2017)** — critère de **susceptibilité EMFI** pour **localiser les hotspots** (balayage XY).
La recherche de paramètres EMFI par GA (**Maldini 2019**) est en
`cross-cutting/parameter-search-methodology.md`. Détail par papier :
[`../../docs/04_REFERENCES.md`](../../docs/04_REFERENCES.md) §E.
