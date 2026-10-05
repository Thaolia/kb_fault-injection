# 00 — Synthèse du corpus `docs_pdf/`

> **Objet du document.** Compiler les 68 PDF de `docs_pdf/` en une base de connaissances
> exploitable pour concevoir un injecteur de fautes **voltage glitching** à base de **RP2350**
> ciblant des **STM32**. Ce document est **sourcé** : chaque affirmation renvoie à un papier et,
> quand c'est possible, à un numéro de page. Les choix d'ingénierie (carte, BOM, PIO) sont
> volontairement renvoyés aux docs [`01`](01_PRECONISATIONS_ARCHITECTURE.md) et
> [`02`](02_BOM_MATERIEL.md), qui sont des **recommandations** et non des extractions du corpus.

---

## 0. Avertissement méthodologique — lire avant tout

**Le corpus reste déséquilibré par rapport à la demande, mais nettement moins qu'à l'origine.** Sur
**68 papiers** (37 initiaux + **12 ajoutés** en minant les bibliographies du corpus lui-même +
**10 ajoutés** depuis une liste curatée externe, le **gist `dev-zzo`**, + **1 thèse de doctorat
ajoutée directement** — Werner, VERIMAG 2022, [`04`](04_REFERENCES.md) §A — voir
[`04`](04_REFERENCES.md), sections comptées **A–G + I**) :

- **3 traitent le voltage FI sur STM32** (contre 1 à l'origine, 2 après le minage) :
  - **Bozzato, Focardi, Palmarini — *Shaping the Glitch*** (TCHES 2019) : chaîne matérielle complète
    et **attaques réussies contre une protection réelle** (RDP F103/F373). Reste le **document de
    référence** de tout le projet.
  - **Timmers, Spruyt, Witteman — *Controlling PC on ARM using Fault Injection*** (deck FDTC 2016,
    **ajouté**) : **voltage FI sur un STM32F415RG** (sl. 52, lu en rendu page-image ; « The target is
    vulnerable to **voltage FI** », sl. 78-84). Apporte le **modèle d'exploitation** que Bozzato n'a
    pas (corruption d'un load → **contrôle du PC**, §3.4), mais sur une **carte de test**, pas contre
    une protection embarquée.
  - ★ **Roth, Datko, Nedospasov — *chip.fail*** (deck 2019, **ajouté**) : **voltage FI sur STM32F2**,
    contre une **protection réelle** (RDP2 → RDP1 → accès SRAM d'un **Trezor One**). Apport propre :
    la **bootROM STM32F2 désassemblée** montre qu'*« aucun test de RDP2 (`0xCC`) n'existe — toutes les
    vérifications ne portent que sur RDP0 (`0xAA`) »* (sl. 130), ce qui **explique structurellement**
    pourquoi un glitch sur la lecture de l'octet RDP suffit ; plus un glitcher **open-source à ~92 $**
    dont l'organe de commutation est un **MUX analogique MAX4619**, pas un crowbar (sl. 63-66).
- ★ **1 traite l'EMFI sur STM32** — inédit dans le corpus : **Beckers *et al.*, *Design
  Considerations for EM Pulse Fault Injection*** (imec-COSIC, **ajouté**), sur un **STM32F411 /
  NUCLEO-F411RE**, **sans exposer le die** (p. 12-13). C'est aussi le **seul papier du corpus
  consacré à la conception de l'injecteur** (banc à **≈ 40 €**) — exploité dans
  [`06`](06_EMI_INJECTOR_EMFI.md).
- ★ **1 traite le FI sur *bootloader embarqué*** — le régime exact des deux séquences STM32 de
  Bozzato : **Van den Herrewegen, Oswald, Garcia, Temeiza — *Fill your Boots*** (TCHES 2021,
  **ajouté**), qui apporte le **premier multi-glitch pleinement documenté sur cible réelle** (STM8) et
  la technique du ***bootloader grey-box glitching*** (§5, [`03`](03_METHODOLOGIE_CAMPAGNE.md) §5).
- **5 portent sur le laser (LFI)** (dont **Colombier** et **Dutertre**, minés dans la biblio Werner) — vecteur **jusqu'ici absent du corpus** et volontairement écarté ;
  l'exclusion a été levée avec les ajouts du gist (voir [`04`](04_REFERENCES.md) §F et §I). Ils ne
  servent pas à construire la carte, mais fournissent un **vecteur de repli** contre une cible qui
  **détecte** les glitchs de tension (cf. l'ATECC508A d'Hériveaux : capteurs de glitch de tension,
  bouclier top-metal… **et aucune contre-mesure laser**).
- **~10** portent sur le **clock glitching** (+2 ajoutés : les deux decks **FDTC 2014** — Korak &
  Höfler, et Ege *et al.* sur l'effet du **chauffage**), dont plusieurs entièrement **FPGA-internes ou simulés**
  (Endo, Sneaky Glitch, SCIS 2019, Surya, Ning) — leurs fenêtres en ns ne se transposent pas
  telles quelles à un MCU attaqué de l'extérieur.
- **6** portent sur les **modèles de faute / détecteurs** (CASA, Ghalaty, Deshpande, TCHES 2024,
  DATE 2014, + **Yuce 2018** *Fault Attacks on Secure Embedded Software* — **ajouté** ; + **Dureuil 2015** — inférence de modèle de faute, racine de CELTIC, minée dans la biblio Werner) — précieux pour
  le *pourquoi* et pour défaire les contre-mesures.
- ★ **3 ajouts « matériel & méthode » qui comblent des trous propres au projet** :
  **O'Flynn — *Fault Injection using Crowbars on Embedded Systems*** (ePrint 2016/810) : **le** papier
  de référence du **crowbar**, c'est-à-dire du Bloc B de la carte, jusqu'ici sans source `[corpus]`
  dédiée ; **Zussa *et al.*, HOST 2014** : mesure **au voltmètre on-chip** du mécanisme des glitchs
  négatifs **et positifs** (§1) ; **Carpi *et al.*, CARDIS 2013** : **stratégies de recherche de
  paramètres** chiffrées (§5).
- **16 sur l'EMFI** (8 + **8 ajoutés** : **Moro 2013** — modèle de faute EMFI sur MCU 32 bits
  Cortex-M, la cible la plus proche d'un STM32 ; **BADFET** — EMFI *second-order*, injecteur < 350 $ ;
  **Faults in Our Bus** — fautes de **bus système** ; **Trouchkine 2021** — modèles
  micro-architecturaux sur SoC 1,2 GHz ; **+ 4 minés dans la biblio Werner** : **Rivière** (cache d'instruction ARMv7-M), **Proy** (cœur superscalaire), **Maldini** (recherche de paramètres par GA), **Madau** (localisation de hotspots)) : **SiliconToaster** (injecteur EM 1,2 kV, Ledger Donjon),
  **Ordas 2015** (modèle
  de faute EMFI), **Nabhan 2024** (mécanisme + capteur), **Beckers 2023** (survey), **Fraunhofer 2022**
  (*EM-Fault It Yourself* — 1er EMFI sur CPU desktop AMD, banc réplicable x86), **O'Flynn 2020**
  — papier + slides, seul cas EMFI **in-situ sur ECU automobile réel** du corpus (bootloader BAM,
  MPC55xx/56xx PowerPC) — et **Toldo 2023** (slides hardwear.io : banc EMFI DIY chiffré contre un SoC
  IoT à secure boot) — exploités dans [`06_EMI_INJECTOR_EMFI.md`](06_EMI_INJECTOR_EMFI.md).
- **12 exposés pratiques Raelize/Riscure** (Timmers, Mune, Pareja, Bogaard, Milburn, Spruyt,
  Witteman, Wiersma) : **modèles de faute exploitables** (*instruction corruption → PC control*) et
  **attaques FI réelles** (privesc Linux, secure boot, extraction firmware, root d'un SoC ARM via
  **EMFI**). Vecteur surtout **voltage** ; **1 seul EMFI** (Google TV Streamer). Les **2 ajouts** sont
  ***Controlling PC on ARM*** (FDTC 2016 — aussi compté ci-dessus comme voltage FI sur STM32) et
  ***Safety != security*** (FDTC 2017 : taux de succès FI mesurés sur MCU **ASIL-D**, et surtout un
  classement chiffré de **l'efficacité des contre-mesures** — lockstep 90 %, ECC flash 68 %, parité
  RAM 14 % ; cf. [`06`](06_EMI_INJECTOR_EMFI.md) §1.2). Exploités dans
  [`03`](03_METHODOLOGIE_CAMPAGNE.md), [`06`](06_EMI_INJECTOR_EMFI.md) et §3.4. (1 est **hors
  périmètre FI** : QSEE, exploitation logicielle.)
- **1** est un **SoK** de synthèse (2025) utile pour le cadrage coût/taux de succès.

**Conséquence.** La physique, les modèles de faute, les paramètres et les métriques viennent du
corpus. **Le montage crowbar, lui, n'est plus hors corpus** : O'Flynn (ePrint 2016/810, **ajouté**)
le nomme, le caractérise sur 5 plateformes et écrit explicitement qu'il *« ne requiert qu'un
générateur d'impulsions… qui peut même être un simple microcontrôleur »* (p. 8) — ce qui valide
directement le rôle donné au RP2350. En revanche **rien dans le corpus ne décrit le RP2350 ni son
PIO** : ces choix-là, dans les docs [`01`](01_PRECONISATIONS_ARCHITECTURE.md)/[`02`](02_BOM_MATERIEL.md),
restent de la recommandation d'ingénierie appuyée sur l'état de l'art commercial (PicoGlitcher,
ChipWhisperer) et sur le brief officiel RP2350.

**`shaminderpaper.pdf` (Kaur *et al.*, Springer 2021) est un scan image** (0 caractère extractible
par `pdftotext`, « Print To PDF ») ; il a néanmoins été **lu via un rendu page-image** (outil de
lecture PDF en mode image). C'est un papier de **simulation Cadence 180 nm + VHDL** au niveau portes
(pas de MCU) : il est cité en pertinence contextuelle (★) dans [`04_REFERENCES.md`](04_REFERENCES.md).
**Couverture du corpus : 68/68** — les 12 ajouts du minage, **les 10 du gist `dev-zzo`** et la
**thèse Werner** ont tous été lus et annotés dans [`04`](04_REFERENCES.md) **avant d'être comptés**.
⚠️ **Ne pas confondre avec `docs_pdf/writeups/`** : 27 **write-ups web** issus du même gist, convertis
en PDF pour archivage, **`[ref]` et non comptés** (leur pagination est un artefact de conversion —
[`04`](04_REFERENCES.md) §J).

---

## 1. Taxonomie des mécanismes d'injection de faute

Le SoK 2025 (arXiv 2509.18341) fournit le cadre coût / taux de succès (Tables 1 et 2, p. 6) :

| Mécanisme | Coût bas | Coût haut | Taux de succès moyen | Contrôle spatial |
|---|---|---|---|---|
| **Clock / Voltage glitching** | **50 $** (PicoGlitcher v2, réf. [81]) | 600 $ (ChipWhisperer) | **≈ 1,4 %** | aucun (effet global) |
| EMFI | 4 000 $ (ChipShouter) | 10 000 $+ | ≈ 2 % | **local** |
| Laser (LFI) | 500 $ | 50 000 $+ | ≈ 100 % | **très local** |

Le SoK regroupe explicitement clock et voltage glitching : *« les fautes produites par le clock
glitching et le voltage glitching sont identiques »* (§3.1). Base commune : **métastabilité par
violation de temps de setup**.

**Sous-familles du voltage FI** (SoK §3.2, p. 3) :

| Sous-méthode | Forme d'onde | Précision | Effet |
|---|---|---|---|
| **Underpowering** | plate, longue durée | imprécise (affecte tout le die) | rallonge le chemin critique en continu |
| **Negative glitch** | chute nette, courte | **la plus ciblée** | déclenche la faute au round visé |
| **Positive glitch** | sur-tension | indirecte | provoque une oscillation amortie → creux involontaire ; peu utilisé |

> ★ **Ce mécanisme « indirect » est désormais mesuré, pas déduit** — Zussa *et al.*, HOST 2014
> (**ajouté**, `hal_HOST_2014_voltmeter.pdf`), instrumente le die avec un **voltmètre on-chip**
> (4 delay-meters, plage 0,7–2,4 V, résolution ~20 mV, p. 5) :
> - *« a positive power supply glitch induces **negative transient voltage modifications under its DC
>   component** »* (p. 6) ; les fautes surviennent **toujours au niveau du *tip* de l'oscillation
>   négative** — *« an experimental proof that the faults injected with positive power supply glitches
>   are due to **setup time violations created by the negative oscillations** »* (p. 7).
> - Le mécanisme des deux polarités est **le même** : à même position, *« the faults injected in the
>   same AES round were **identical** »* (p. 7). Corollaire défensif imprimé : les contre-mesures
>   anti-glitch négatif *« should also be effective »* contre le positif.
> - ⚠️ **Mais « indirect » ne veut pas dire « moins efficace »** : le positif a fauté **toutes les
>   rondes AES sauf la première**. Le qualificatif « peu utilisé » ci-dessus reste un constat d'usage,
>   pas d'efficacité.
> - ⚠️ **À ne pas confondre avec l'overpowering statique**, qui n'a produit **aucune faute** (p. 4).
> - ★ **Le négatif oscille aussi** : un glitch négatif produit **deux jeux d'oscillations amorties**
>   (fronts descendant *et* montant, p. 6). La colonne « forme d'onde » ci-dessus décrit la
>   **commande**, pas ce que voit le silicium.
> - **Portée** : cible = **FPGA Spartan-3**, AES matériel — pas un MCU. Ce qui se transpose est
>   **mécanistique** (existence du ringing, faute au *tip*), pas numérique : la période de ringing est
>   propre à chaque carte et **doit être mesurée**. Les amplitudes de commande (14 V, 22 V pour ~400 mV
>   au die) sont propres à ce banc. Exploitation pratique en [`03`](03_METHODOLOGIE_CAMPAGNE.md) §5.

> **EMFI** (injection électromagnétique, champ proche, *local*) : vecteur **complémentaire non-contact**,
> traité hors corpus dans [`06_EMI_INJECTOR_EMFI.md`](06_EMI_INJECTOR_EMFI.md) (module RP2350, 5 V → 1 kV).

---

## 2. Pourquoi le voltage glitching sur STM32 (et pas le clock glitch)

Trois résultats du corpus convergent pour faire du voltage glitching **le vecteur principal** sur
STM32, et du clock glitch un complément conditionnel :

1. **La PLL bloque le clock glitch.** TCHES 2024 (p. 176) : *« les variations rapides de l'horloge
   de référence ne traversent pas une PLL »* → contre-mesure quasi totale contre le clock glitching.
   Le cœur d'un STM32 est cadencé par une PLL interne.
2. **Le clock glitch externe exige une horloge externe.** *Peak Clock* (ASHES'19) n'attaque un
   STM32F0 que parce que sa PLL est sourcée par un **signal externe de 4 MHz** (p. 92). Si le
   firmware démarre sur **HSI (RC interne)** et fait tourner la PLL sur HSI, **il n'existe aucun
   nœud d'horloge externe à manipuler**.
3. **Le voltage glitch, lui, reste efficace.** *Peak Clock* le dit en négatif (p. 93) : *« passer à
   une source d'horloge interne… ne protège pas contre les attaques par voltage glitch. »*

> **À retenir.** Le clock glitch n'est exploitable sur STM32 que si l'on peut forcer le boot sur
> **HSE** (cristal, injection sur OSC_IN, bootloader ROM utilisant HSE). Sinon → voltage glitch /
> EMFI. Le doc [`03`](03_METHODOLOGIE_CAMPAGNE.md) traite les deux cas.

---

## 3. Modèles de faute — ce que l'on peut réellement obtenir

### 3.1 Table de réalisme par mécanisme (Ghalaty 2016, Table 2.2, p. 13)

| Injection | Chosen bit | Single bit | Byte | Random | Contrôle du timing |
|---|:---:|:---:|:---:|:---:|---|
| **Glitch (clock/voltage)** | – | – | **✔** | **✔** | **précis** |
| **Underpowering (starving)** | – | – | **✔** | **✔** | lâche |
| Voltage spike | – | – | – | ✔ | précis |
| EM pulse | – | ✔ | ✔ | ✔ | précis |
| Laser | ✔ | ✔ | ✔ | ✔ | précis |

> **Conséquence directe.** Un glitcher de tension **n'atteint pas** le modèle *chosen-bit*.
> Réalistement : **byte fault et random fault**, avec un **bon contrôle temporel** mais **aucun
> contrôle spatial** (la tension est un signal global). Toute analyse qui suppose un bit-flip
> **choisi** est **hors modèle**.

> ⚠️ **Nuance sur la colonne *single bit*, apportée par un ajout au corpus.** La table de Ghalaty se
> lit comme une table de **contrôlabilité adverse** (ce que l'attaquant peut *choisir*), pas de
> **résultats observables** (ce qui *sort*). Zussa *et al.* (HOST 2014, **ajouté**) observe en effet,
> par voltage glitch : *« Most of the induced faults were **single-bit faults** »* (p. 6) et *« voltage
> glitches make it possible to inject **single-bit faults with very good timing accuracy** »* (p. 7).
> **Portée à ne pas outrepasser** : c'est un **AES matériel dans un FPGA Spartan-3** — un chemin de
> données combinatoire, **pas un flux d'instructions de MCU**. La transposition à une faute
> d'instruction sur STM32 **n'est pas établie**. Retenir : *single-bit* est **observable** en sortie,
> il n'est pas **commandable**.

### 3.2 Le modèle physiquement correct : set/reset, pas bit-flip (CASA 2022, §4)

La formalisation de Richter-Brockmann *et al.* (CASA/Bochum) donne l'instanciation par mécanisme
(§4.4, pp. 20–23) :

| Mécanisme | Modèle formel | Nature de la faute |
|---|---|---|
| Clock glitch | `ζ(n, τ_sr, c_i)` | **set/reset** (stuck-at) dans la combinatoire |
| **Voltage glitch / underpowering** | **`ζ(n, τ_sr, c_i)` — identique** | idem |
| EM pulse | `ζ(n, τ_sr, m)` | échantillonnage dans les bascules |
| Laser | `ζ(n, τ_nang15, mc_∞)` | le plus général |

> ★ **Point le plus important pour la modélisation.** Pour un voltage glitch, la valeur fautée est
> **l'ancienne valeur du registre** (échantillonnage trop tôt), **pas l'inverse** de la bonne valeur.
> Un exploit ou une simulation basés sur du bit-flip modélisent mal la réalité. La **sévérité**
> (combien de bits) **n'est pas contrôlable** ; seule la **profondeur de chemin ciblée** l'est, via
> la durée du glitch (paramètre `l = c_i`). Le bit-flip reste un modèle *worst-case* commode mais
> imprécis (CASA §6, p. 27).

**Hiérarchie de couverture** (CASA §4.5, p. 23) : un design sûr sous laser l'est sous EM / clock /
voltage glitch ; la réciproque est fausse.

> **EMFI (`[corpus]` Ordas 2015)** : les fautes EMFI sont des **« sampling faults »** (bitset/bitreset,
> **locales**, dépendant de la **polarité** de la sonde), distinctes du *set/reset* du voltage glitch.
> Détail et exploitation dans [`06_EMI_INJECTOR_EMFI.md`](06_EMI_INJECTOR_EMFI.md).
>
> ★ **Portée à qualifier depuis les ajouts au corpus : « au niveau du die ».** Ordas reste valide pour
> l'EMFI **dans le silicium**, mais trois papiers ajoutés montrent des fautes EM dont **le siège est
> ailleurs** — la **DRAM voisine** (BADFET, `06` §1.4), les **pistes de bus du PCB** (Faults in Our
> Bus, `06` §1.5, qui ne mesure d'ailleurs **aucune asymétrie 1→0 / 0→1**, là où Ordas prédit une
> dépendance à la polarité) et le **transfert de bus depuis la Flash** (Moro 2013, `06` §1.6, qui
> conclut à une **faute de timing**, pas à un *sampling fault*). À lire comme une **chronologie de
> raffinement** — Moro 2013 (timing) → Ordas 2015 (sampling, conteste le timing) → Nabhan 2024
> (réconcilie par les **deux voies de couplage** PDN + clock tree) — et non comme une contradiction à
> trancher.

> ⚠️ **Désaccord de littérature ouvert : bit-flip ou set/reset ?** Yuce *et al.* (JHSS 2018,
> **ajouté**) affecte **la polarité inverse** de CASA : *« **All** of the aforementioned fault
> injection techniques are able to induce **bit-flip** effects. **In addition, laser and EM pulses**
> are also able to induce bit-reset, bit-set, and stuck-at faults »* (p. 8) — soit bit-flip pour le
> voltage glitch, set/reset réservé au laser et à l'EM. **Asymétrie de preuve** : CASA **dérive** son
> modèle du mécanisme physique, Yuce donne une **ligne de taxonomie de survey**. **CASA reste donc la
> source de grade « mécanisme » du projet**, et le fait porteur (« set/reset, pas bit-flip ») est
> maintenu — mais le désaccord est signalé ici plutôt que masqué.

### 3.3 Les 4 étapes de la faute — squelette d'une campagne (Ghalaty §2, pp. 16–17)

1. **Fault Injection Access** — accès physique (broches CLK / VDD / VCAP pour le glitch).
2. **Actual Fault Injection** — application du stress ; on contrôle timing + intensité, **pas** la
   localisation.
3. **Fault Effect** — effet logique **non garanti** : un stress physique peut ne produire aucune
   faute.
4. **Fault Observation** — propager l'effet jusqu'à une sortie observable.

Chaque étape est un **filtre multiplicatif** sur le taux de succès : une campagne doit les
instrumenter séparément, sinon on ne sait pas laquelle échoue.

### 3.4 L'instruction skip → la corruption d'instruction (lacune désormais partiellement comblée)

**Les sources théoriques *classiques* du corpus ne formalisaient pas l'instruction skip.** Les seuls éléments proches :

- TCHES 2024 (p. 174) : les glitchs courts produisent des fautes **grossières**, *« best suited for
  disrupting a microprocessor's instruction execution »*.
- Ghalaty (p. 12) : un **voltage spike** peut *« masquer une instruction lue en mémoire pendant son
  transfert sur le bus »* — la description la plus proche du skip.
- *Glitching Demystified* (DSN'21) montre expérimentalement, cycle par cycle, que l'effet le plus
  probable d'un glitch bon marché est un **flip 1→0** dans l'encodage de l'instruction (masque
  logique AND), ce qui « skippe » les branchements **> 60 %** du temps en émulation.

> **Cette lacune est désormais (partiellement) comblée** par les exposés Raelize/Riscure ajoutés au
> corpus (`[corpus]`, cités par slide) : le « skip » est un **modèle de commodité**, la faute réelle
> étant une **corruption d'instruction** dont le skip n'est qu'un sous-cas (**PANDA 2018** sl. 18-20 ;
> **False Injections**, Dartmouth 2025, sl. 53-73, qui le prouve expérimentalement sur **ESP32
> (Xtensa, voltage)**). La
> corruption d'une instruction de **transfert** (`ret`/`blr`/`ldr`) peut charger une donnée attaquant
> directement dans le **program counter** → exécution arbitraire **sans faille logicielle**
> (**Data Transfers → Arbitrary Execution**, PoC 2019, sl. 24-56 ; démontré sur cibles réelles — voir
> [`03`](03_METHODOLOGIE_CAMPAGNE.md) §9).

> ★ **La formalisation d'origine est désormais AU CORPUS** (elle était signalée ici comme « hors
> corpus » dans les versions précédentes) : *Controlling PC on ARM using Fault Injection*,
> **Timmers, Spruyt, Witteman — deck FDTC 2016**, `docs_pdf/2016_FDTC_Controlling-PC-on-ARM-…_TSW.pdf`,
> cité **`sl. N`**. Ce qui entre est le **deck de présentation** des auteurs, **pas** le papier IEEE
> (paywallé, toujours `[ref]`) — les decks du corpus la citent et l'étendent (PANDA sl. 20/23/27).
> Ce que l'origine apporte, et que les decks postérieurs ne disent pas :
>
> - **Vecteur : voltage, sur un STM32F415RG** (sl. 52, schéma lu en rendu page-image ; « The target is
>   vulnerable to **voltage FI** », sl. 78-84). Banc **Riscure VC Glitcher**, liaisons *trigger /
>   reset / vcc* (sl. 57). Modifications de la cible : **power cut, retrait des condensateurs, reset,
>   trigger** (sl. 52) — le retrait du découplage y est donc attesté une seconde fois.
> - **Le mécanisme est un champ de bits, pas une abstraction** (sl. 25-32) : on corrompt le **registre
>   de destination** d'un load. `LDR r3` → `LDR PC` demande de mettre **2 bits à 1** ;
>   `LDMIA {r3-r10}` → `{r3-r10, PC}` n'en demande **qu'un seul** (bit 15 de la liste).
> - ★ **Conséquence opératoire.** Ce qui est **imprimé** (sl. 78-84) : *« Success rate is different
>   for ldr and ldmia — **the instruction encoding matters** »*. Les nuages de points des campagnes
>   « 10k » (sl. 63 pour `LDR`, sl. 65 pour `LDMIA`) montrent **~1 marqueur de succès** contre
>   **~26** — ⚠️ **valeurs comptées sur le graphe, non imprimées** (recouvrements possibles : à lire
>   comme *un ordre de grandeur*, pas comme un chiffre sourcé). L'enseignement, lui, est bien du
>   papier : **choisir l'instruction visée d'après sa distance de Hamming pèse plus que d'affiner le
>   glitcher.**
> - **Les instructions visées à l'origine sont `LDR` et `LDMIA`** (boucles de copie : données
>   contrôlées par l'attaquant, exécutées en série, non protégées — sl. 16-24). Le cadrage plus large
>   `ret`/`blr`/register-restore vient du deck **PoC 2019**, postérieur.
> - ⚠ **Scission ISA à ne pas gommer** : tous les encodages imprimés sont en **ARM/A32**
>   (`LDR r3,[r1],#4` = `0xE4913004`), alors que la carte expérimentale est un **Cortex-M4 =
>   Thumb-2 uniquement**, incapable d'exécuter de l'A32. Le deck **ne réconcilie jamais les deux** et
>   n'imprime nulle part les encodages Thumb-2 réellement glitchés. Le *concept* se transpose (LDR
>   T3/T4 et LDM T2 acceptent PC) ; **les motifs binaires imprimés, non.**
> - ⚠ **Le deck ne dit pas quel rail a été glitché** (la ligne est étiquetée `vcc`) : **ne pas écrire
>   que VCAP était le point d'injection**, même si la carte expose VCAP1/VCAP2 (br. 31 et 47).
>
> **Moro *et al.* est également passé au corpus** (`1402.6421v1.pdf`, FDTC 2013) : c'est un modèle de
> faute **EMFI** sur **Cortex-M3**, où seuls les **transferts depuis la Flash** sont fautables (jamais
> la SRAM) et où les instructions/registres dont l'encodage **contient le plus de 1** fautent le plus
> — même logique de distance de Hamming que ci-dessus, par l'autre vecteur. Détail en
> [`06`](06_EMI_INJECTOR_EMFI.md) §1.6.

> ★ **Appui empirique récent, par *inférence* de modèle** [corpus, Werner, thèse VERIMAG 2022,
> ch. 4] : en croisant caractérisation expérimentale et simulation ISA (simulateur **CELTIC**, lignée
> Dureuil — ⚠️ **pas** FiSim), Werner infère que les modèles **dominants** sur ses Cortex-M sont des
> **sauts multi-instructions** (16/32/48 octets, soit 4 à 12 instructions) et une **corruption du
> cache d'instruction** (`4CacheCorruption`, ~90 % des fautes *power glitch* sur l'un des MCU, modèle
> déjà observé par Rivière *et al.* en EMFI) — le « skip » est donc un **sous-cas d'un saut de bloc**,
> pas d'une seule instruction. La méthodologie explique *« 76 % des résultats fautés en moyenne »*
> (p. 69). ⚠️ Modèles **de ses cibles**, inférés — cités comme appui, pas comme loi générale. **Les
> deux sources — Dureuil (inférence `P(m|c)`) et Rivière (modèle de cache) — sont traitées en §3.6.**

### 3.5 Où vit la faute dans le pipeline — cartographie sur deux MCU réels

**Korak & Höfler** (deck FDTC 2014, **ajouté**) répondent à une question que le reste du corpus laisse
ouverte : *le skip et la corruption ne sont pas deux modèles concurrents, ce sont deux **étages
différents du pipeline***. Mesuré sur **Atmel ATxmega256** (8 bits, Harvard, pipeline **2 étages**) et
**NXP LPC1114 / Cortex-M0** (32 bits, von Neumann, pipeline **3 étages**), sl. 11-12 :

| Étage | Effets observés | Correspondance avec les modèles du projet |
|---|---|---|
| **FETCH** (sl. 21) | *« Fetch buffer not updated »* · ***« Instruction not executed »*** · ***« Instructions executed twice »*** · *« Program flow modification »* | c'est **là que vit le *skip*** (et le doublon, rarement évoqué) |
| **EXECUTE** (sl. 22) | *« Wrong results »* · *« Constant values »* · ***« Varying values (TGlitch) »*** · *« Data flow modification »* | c'est là que vit la **corruption de données** |
| **DECODE** (sl. 23) | ***« Decode stage not affected »*** — sur les **deux** plateformes | — |

- ★ **« Varying values (TGlitch) »** (sl. 22) : la valeur fautée **dépend de la durée du glitch**.
  C'est la confirmation, sur MCU réel, du principe de §3.2 — on contrôle la **profondeur de chemin
  ciblée** via la durée, jamais la **sévérité**.
- ★ **Contre-intuition à retenir** (sl. 26) : glitcher un **branchement pendant l'execute** donne
  *« **No effects** »* **sur les deux plateformes** (`beq` et `breq`). L'effet exploitable sur un
  branchement est **au fetch uniquement**. ⚠️ À ne pas opposer frontalement à *Peak Clock* (« les
  branchements échouent en premier ») ni à *Glitching Demystified* (« skip de branchement > 60 % ») :
  ces deux-là décrivent d'autres régimes (burst PLL soutenu, émulation ISA). Le désaccord porte sur le
  **régime**, pas sur le mécanisme.
- **Appui au modèle « corruption des transferts »** (sl. 25, Cortex-M0) : `ldr`/`str` fautés au
  **fetch** donnent *« Rd set to zero »* / *« Memory set to zero »* ; à l'**execute**, *« Address in
  Rd »* / *« Address in Memory »*. C'est exactement la corruption de transfert que Raelize exploite
  ([`03`](03_METHODOLOGIE_CAMPAGNE.md) §9.1), observée ici au niveau instruction.
- **Fait de dimensionnement** : la fenêtre `TGlitch` exploitable au fetch sur load/store fait
  **~12 ns sur l'ATxmega (2 étages)** contre **~0,5 ns sur le Cortex-M0 (3 étages)**
  *(mesures **lues sur le graphe** sl. 27, **non imprimées**)*. Un STM32 étant un Cortex-M à 3 étages,
  **tabler sur le régime étroit**.

> ⚠️ **Portée de ce papier — deux réserves qui comptent.** (1) **Le vecteur est le clock glitch**, pas
> le voltage : malgré son titre, l'underpowering n'y est qu'un **sensibilisateur combiné**, jamais un
> vecteur autonome. (2) La Fault Board fournit à la cible **l'horloge *et* l'alimentation** (sl. 13),
> soit la précondition « horloge externe » que §2 identifie comme **absente d'un STM32 bootant en
> HSI**. Ce papier ne remet donc pas en cause le choix du voltage glitch pour ce projet — il en
> confirme plutôt la règle : *quand on possède la ligne d'horloge, le clock glitch est excellent*.
> Les effets par étage, eux, se transposent : ils décrivent un pipeline, pas un vecteur.

### 3.6 Inférer le modèle au lieu de le postuler — et le modèle de cache d'instruction

Les §3.1–§3.5 énumèrent des modèles **postulés** (set/reset, skip, corruption). Deux papiers minés
dans la bibliographie de Werner traitent la question **en amont** : *comment savoir quel modèle
s'applique*, et *quel est le modèle concret d'un Cortex-M attaqué par EMFI*.

★ **Inférer le modèle — Dureuil *et al.* (CARDIS 2015)** `[corpus]`, la **racine** de la méthode de
Werner (§3.4). Plutôt que de supposer un modèle, on l'**infère** pour un couple (matériel attaqué,
équipement de l'attaquant) en lui attachant une **probabilité d'occurrence `P(m|c)`** (p. 1). Deux
phases (§2–§4) : (1) **inférence** du modèle depuis une caractérisation ; (2) **simulation**
d'injection par l'outil **CELTIC** (§4), qui calcule une métrique prédictive — le ***vulnerability
rate*** — pour **classer les attaques et mesurer la robustesse avant toute campagne réelle**
(*« simulators provide exhaustiveness and reproducibility »*, p. 2). ⇒ Le modèle de faute cesse d'être
une hypothèse de l'attaquant : il devient une **sortie mesurée + simulée**, propre à chaque cible et
chaque banc. C'est ce pipeline que Werner reprend et **automatise** (§3.4 ; exploitation en
[`03`](03_METHODOLOGIE_CAMPAGNE.md) §5).

★ **Le modèle concret sur Cortex-M — Rivière *et al.* (HOST 2015)** `[corpus]`. EMFI sur le **cache
d'instruction** d'un **Cortex-M4 (ARMv7-M, pipeline 3 étages)** : la faute ne porte pas sur **une**
instruction mais sur une **ligne de cache de 128 bits**. Une impulsion **remplace ou saute ≈ 4
instructions 32 bits (6 à 8 Thumb-2 de 16 bits)** d'un coup ; une double injection **remplace la ligne
de cache entière** (§3.1). Le modèle — *« instruction replacement »* **et** *« instruction skip »* —
est **reproductible dans jusqu'à 96 % des cas** (p. 1) et *« not yet considered in the literature »*.
⇒ **Conséquence directe pour §3.4** : le « skip » exploitable sur un Cortex-M est le saut d'un **bloc
de ≈ 4 instructions** (granularité de ligne de cache), **pas d'une seule** — c'est la base empirique
du `4CacheCorruption` qu'infère Werner. ⚠️ Vecteur = **EMFI** (contrôle spatial) ; ce qui se transpose
au voltage glitch est la **granularité de bloc**, pas le mécanisme de couplage.

---

## 4. Paramètres de glitch observés dans la littérature

Table transversale — **une ligne par résultat exploitable**, valeurs telles qu'imprimées.
⚠️ = régime non transposable tel quel à un MCU externe (FPGA-interne / simulation).

| Source | Cible / régime | Paramètre-clé | Valeur | Page |
|---|---|---|---|---|
| **Bozzato** | STM32F103, bypass RDP | résolution du délai trigger→glitch | **10 ns** (timer HW STM32F407) | p. 204 |
| **Bozzato** | STM32F373, downgrade RDP | délai d'injection après boot | **11 µs** | p. 209 |
| **Bozzato** | MSP430FR5725 | VDD nominal → VDD glitch | **1400 mV → 880 mV** (transitions douces) | p. 211 |
| **Bozzato** | AGW, toutes cibles | sortie / résolution DAC / BP | **±10 V**, **12 bits**, **6 MHz** | p. 204 |
| **Bozzato** | forme d'onde | dérive fatale sur 1 point | **−170 mV → attaque KO** | p. 218 |
| Skorobogatov | ARM sécurisé, ProASIC3 | pas de balayage du délai | **25 ns** | sl. 33/41/55 |
| Skorobogatov | — | cadence d'attaque | **10 ms → 100 ms / cycle** | sl. 33/54 |
| *Peak Clock* | STM32F0308R (HSE) | durée du burst d'over-clock PLL | **~100–140 µs**, fenêtre de succès **~19 µs** | p. 89 |
| *Peak Clock* | XMC4500 (PLL rapide) | durée du burst | **500 ns** | p. 90 |
| ⚠️ Endo | FPGA Virtex-II | résolution temporelle du glitch d'horloge | **0,17 ns** (min. phase-shift DCM) | p. 266 |
| ⚠️ Sneaky Glitch | FPGA 7-Series | pas de phase / largeur visible | **14,8 ps** cmd / **531 ps** visible / **921 ps** = 20 % VDD | — |
| ⚠️ Marotta (SPICE) | 28 nm FDSOI | seuil tension domine seuil largeur | **0,03 ns possible à 0,84 V ; rien sous 0,46 V** | p. 14 |
| ⚠️ Ning (simul.) | AES FPGA | pas de réduction de période | **0,02 ns** (balayage 4,4 → 3,72 ns) | p. 16 |
| ⚠️ Surya | S-box ASCON FPGA | fenêtre productive | **[4,1 ; 5,4] ns** (LUT filtre < 4,1 ns) | — |
| ⚠️ Martín | TRNG FPGA, underpowering | seuil de faute vs tension | **1,20 V → fautes à 40 MHz ; 0,70 V → dès 32 MHz** | p. 271 |
| **Controlling PC on ARM** *(ajout)* | **STM32F415RG**, voltage | zone de succès (profondeur × largeur) | **crête diagonale** : −1,40 → −1,00 (**unité non imprimée**) × **650–1000 ns** | sl. 61, 63, 65 |
| **Controlling PC on ARM** *(ajout)* | idem, campagnes « 10k » | succès `LDR` vs `LDMIA` | **~1** vs **~26** (1 bit à corrompre au lieu de 2) — ⚠️ **comptés sur le nuage de points, non imprimés** ; seul *« the instruction encoding matters »* l'est | sl. 63, 65 (sl. 78-84 pour la phrase) |
| **O'Flynn — crowbar** *(ajout)* | ATMega328P / RPi / BeagleBone / Android | **durée d'activation du crowbar** pour une faute | **135 / 635 / 485 / 615 ns** | p. 5, Table 1 |
| **O'Flynn — crowbar** *(ajout)* | AVR, salve verrouillée en phase | largeur d'impulsion élémentaire réalisée | **16,9 ns** (50 % de la période de glitch-clock) | p. 6 |
| **O'Flynn — crowbar** *(ajout)* | Spartan-6, readback bitstream | largeur → corruption | **≥ 600 ns** = toujours ≥ 1 bit ; **750 ns** = 50 % de flips sans casse ; **> 900 ns** = reset | p. 5-7, Table 2 |
| **Zussa HOST'14** *(ajout)* | FPGA Spartan-3, AES | **amplitude commandée → amplitude au die** | **−14 V** commandé → **~400 mV** de creux au die (tip ~20 ns) | p. 6 |
| **Zussa HOST'14** *(ajout)* | idem, effet d'*addition* | largeur = **demi-période** du ringing | **8 V** suffisent pour les mêmes 400 mV (au lieu de 14 V) | p. 7 |
| **Zussa HOST'14** *(ajout)* | idem, effet de *sharping* | largeur ≪ ringing | tip **rétréci à ~10 ns**, au prix de **22 V** | p. 7 |
| **Moro** *(ajout, EMFI)* | Cortex-M3 56 MHz | seuil / saturation en tension d'impulsion | **rien à 172 V** · 1ʳᵉ faute **174 V** (73 %) · **saturation `0xFFFFFFFF` dès 186 V** | p. 6, Table III |
| **BADFET** *(ajout, EMFI)* | Cisco 8861, ARM **1 GHz+** | impulsion unique / répétabilité | **10 µs à 300 V** à 4,62 s du power-cycle, sonde à 3 mm → **72/100 succès** | p. 4, p. 6 |
| **Faults in Our Bus** *(ajout, EMFI)* | RPi3/RPi4, bus système | **longueur de burst → bus fauté** | **~20 impulsions = bus de données** · **~100 = bus d'adresses** | p. 8 |
| **Fill your Boots** *(ajout gist)* | **STM8L152C6**, double glitch sur CRP | `T0 / W0 / T1 / W1` → succès | **29,5 µs / 50 ns / 7,32 µs / 50 ns → 0,0001 %** | Table 2, p. 14 |
| **Fill your Boots** *(ajout gist)* | **STM8AF6266**, double glitch sur CRP | `T0 / W0 / T1 / W1` → succès | **80,75 µs / 120 ns / 3,91 µs / 120 ns → 0,001 %** | Table 2, p. 14 |
| **Fill your Boots** *(ajout gist)* | STM8L, glitchs **individuels** (profilage) | tension et largeur figées, offset balayé | **V_F = 1,84 V**, **W = 50 ns**, succès **0,1–0,6 %** ; tolérance d'offset **± 20 ns** | Table 1, p. 13 |
| **Fill your Boots** *(ajout gist)* | banc GIAnT + Raspberry Pi 3 | **résolution de l'instrument** (largeur et offset) | **10 ns** — *limite du générateur, pas de la physique* | p. 5 |
| **Fill your Boots** *(ajout gist)* | STM8AF6266, cadence | débit de tentatives | **100 000 glitchs ≈ 2,5 min** (reset compris) | p. 13 |
| **chip.fail** *(ajout gist)* | **STM32F2** (Trezor One), RDP2→RDP1 | paramètres publiés du glitcher | `Delay ≈ 17900` · `Pulse = 50` — ⚠️ **unités non imprimées** (compteurs FPGA), ne pas convertir en ns | sl. 149 |
| **chip.fail** *(ajout gist)* | STM32F2, chronologie de boot | durée du boot / fenêtre observable | boot **1,8 ms** ; les **200 µs** après reset séparent *BootROM → lectures Flash/Option Bytes → application* | sl. 137-144 |
| **COSIC — EM Pulse** *(ajout gist, EMFI)* | **STM32F411**, Cortex-M4 100 MHz | largeur d'impulsion visée / réalisée | **10 ns** visés ; **12 ns** au premier montage, ramenés à 10 ns en abaissant `C1` | p. 12 |
| **COSIC — EM Pulse** *(ajout gist, EMFI)* | idem, balayage | pas temporel et répétitions | **100 ns balayés par pas de 1 ns**, **100 impulsions par pas** | p. 13 |
| **RHUL — laser bas coût** *(ajout gist, LFI)* | AVR / ARM | largeur d'impulsion laser | **5 ns (200 MHz)**, ≈ **2 mJ/impulsion** ; **plus de temps de recharge** (contre **20 ms** en YAG) | p. 1 |
| **Hériveaux — laser** *(ajout gist, LFI)* | ATECC508A (Coldcard Mk2) | volume de campagne | **343 617 injections → 0 succès** ; après re-caractérisation, succès en **2 minutes** | sl. 62, 68 |

**Deux enseignements de synthèse :**

- **Impulsion vs burst.** Sur logique combinatoire / FPGA, la fenêtre utile est de l'ordre de la ns
  (Surya 1,3 ns ; Endo ~7 ns ; Ning 0,7 ns). Sur cible à **PLL** (STM32), il faut un **burst
  soutenu** dont la durée est dictée par la **pente de la PLL** (µs à centaines de µs).
- **La résolution de commande ≠ la largeur d'impulsion réalisable.** Sneaky Glitch le chiffre
  crûment : commander à 14,8 ps ne produit un glitch visible qu'à partir de **531 ps**. Sur une carte
  physique avec câbles et capacité d'entrée de la cible, **le plancher de largeur est fixé par
  l'étage de sortie, pas par le contrôleur** — point capital pour dimensionner le RP2350 (voir
  [`01`](01_PRECONISATIONS_ARCHITECTURE.md)).
- ★ **Troisième enseignement, apporté par les ajouts : ce n'est pas l'impulsion commandée qui faute,
  c'est la réponse du PDN.** Zussa mesure **−14 V commandés → ~400 mV au die** (p. 6) et montre que la
  faute naît au ***tip* d'une oscillation**, pas sur le plateau de l'impulsion (p. 7). O'Flynn
  l'observe côté carte : à la relâche du crowbar, **overshoot de plusieurs fois le nominal puis
  ringing** dont *« le niveau et la fréquence dépendent grandement du PDN »* (p. 4). **Conséquence :
  la « finesse » réellement atteignable est fixée par la période de ringing de la carte** — que l'on
  peut exploiter (*sharping* : tip ramené à ~10 ns) mais pas par le tick du contrôleur. **Mesurer
  cette période sur la carte cible avant toute campagne.**
- ★ **Quatrième : le choix de l'instruction visée pèse plus que la finesse du glitcher.** À banc
  identique, `LDMIA` réussit **~26 fois** quand `LDR` réussit **~1 fois** sur des campagnes de 10 000
  essais — parce qu'il faut corrompre **1 bit au lieu de 2** (*Controlling PC on ARM*, sl. 63/65 ;
  ⚠️ **comptages sur graphe, non imprimés** — le papier n'imprime que *« the instruction encoding
  matters »*, sl. 78-84). Côté EMFI, Moro observe la
  même logique : les registres dont l'encodage **contient le plus de 1** (r7 = `111`, pc) fautent le
  plus (p. 7). **Choisir la cible d'instruction par sa distance de Hamming avant d'investir dans la
  résolution matérielle.**
- ★ **Cinquième, et c'est le plus contre-intuitif du lot : un multi-glitch réussit MOINS souvent que
  le produit de ses glitchs individuels.** Sur STM8L, deux glitchs à 0,6 % et 0,1 % devraient donner
  ≈ 0,0036 % combinés ; le taux mesuré est **0,0001 %**, soit **36 fois moins**
  (*Fill your Boots*, p. 13). Cause imprimée : le **pipeline 3 étages** — après le premier glitch, le
  flot d'exécution change, donc **le contenu du pipeline au moment du second glitch n'est plus celui
  du profilage**. **Conséquence de dimensionnement : ne jamais budgéter un multi-glitch en
  multipliant les taux individuels** ; les recaractériser dans la séquence complète.
- ★ **Sixième : caractériser bat accumuler, et l'écart se compte en ordres de grandeur.** Hériveaux
  injecte **343 617 fautes sur plusieurs jours sans un seul succès**, puis — après analyse des
  réponses fautées et re-préparation de l'échantillon — réussit en **deux minutes** (sl. 62, 68).
  Même leçon que Carpi (§5) et que le profilage préalable de *Fill your Boots*, mais mesurée ici sur
  une cible commerciale.

---

## 5. Stratégies de recherche des paramètres

Ordre recommandé, synthétisé des quatre papiers pratiques :

1. **Balayage monotone du délai d'abord** — Skorobogatov (sl. 42) : *« Precision timing is not
   necessary — slowly increase the delay until the effect is observed. »*
2. **Récursion en précision** — DSN'21 (p. 405) : partir d'un glitch large (~10 cycles), puis
   affiner d'un facteur `1/(10·profondeur)` jusqu'à 100 % de succès. Convergence **16–59 min**.
3. **Algorithme génétique sur l'espace complet** (dont la forme d'onde) — Bozzato (pp. 206–207) :
   fitness `F = S/T`, départ à **50 tests/candidat**, crossover uniforme `p=0,5`, **mutation la plus
   forte sur la durée**, replace-worst. Convergence **30 min → 10 h**.
4. **Interlacer optimisation et attaque** pour ne pas gaspiller de glitchs (Bozzato p. 207).
5. ★ **Recherche dichotomique 2D « adaptive zoom & bound »** — Carpi *et al.*, CARDIS 2013
   (**ajouté**) : c'est la **stratégie la mieux classée** des quatre comparées, *« it completes the
   first stage of the search with the **least number of measurements**, and it has the **best ratio of
   SUCCESSFUL measurements** »* (p. 14). Chiffres : **192 mesures** en 1ʳᵉ étape contre **2048** pour
   FastBoxing et **1560** pour l'algorithme génétique, pour un **meilleur** taux de succès
   (**1,17 %** contre 0,30 % et 0,31 %, Table 5 p. 14). Le **Monte Carlo** (tirage aléatoire) est la
   baseline : **0 succès en 3072 mesures**, et il en faut **76 800 pour 11 succès** (p. 8).
   **Plancher théorique** de la 1ʳᵉ étape, formule directement réutilisable (p. 10) :
   `N = n · ⌈max(log₂(rangeV/resolutionV), log₂(rangeL/resolutionL))⌉` → **112 mesures** pour un
   espace [−5 ; −0,05] V × [2 ; 150] ns à résolutions 0,05 V / 2 ns.
   > **Le modèle sous-jacent, à reprendre tel quel** : la recherche se fait en **deux phases** —
   > d'abord la **forme** du glitch (tension, longueur), ensuite seulement l'**instant** d'injection
   > (p. 5) — et l'on vise la **frontière de décision** entre la région NORMAL et la région
   > RESET/MUTE, matérialisée par deux verdicts dédiés : **INTERESTING** (proche de la frontière) et
   > **CHANGING** (deux mesures identiques donnant des verdicts différents). ★ **C'est en ciblant la
   > zone CHANGING et en répétant 3× chaque mesure** que les auteurs cassent leur **Target C**,
   > pourtant **certifié Common Criteria EAL4+** et annoncé protégé contre le VCC FI : *« As far as
   > the authors know, this target was not known to be vulnerable to VCC FI attack before »* (p. 11-12).
   > ★ **Résultat de portabilité** (p. 11) : les **paramètres de forme** (tension, longueur) sont
   > **les mêmes d'un exemplaire à l'autre** du même composant et donc réutilisables ; **les
   > paramètres temporels, non**. C'est la règle qui décide de ce qu'on recalibre en changeant de puce.
   > ⚠️ **Citer les pourcentages de Carpi avec leur définition** : les Tables 2/3 donnent des
   > **médianes par test**, les Tables 5/6 le **meilleur run observé** — deux définitions différentes
   > pour les mêmes cellules (voir [`04`](04_REFERENCES.md)).

6. ★ **Profiler avant d'attaquer : le *bootloader grey-box glitching*** — *Fill your Boots*
   (TCHES 2021, **ajouté**), p. 10. Quand la cible ne renvoie **aucun retour** avant le succès complet
   (le bootloader STM8 coupe toute communication tant que la protection est active), **flasher les
   sections critiques du bootloader en tant qu'application utilisateur** et profiler **chaque glitch
   séparément**, puis seulement combiner. Sans cela, *« a full search of the glitch parameters quickly
   leads to a state explosion »* (p. 14). **Transposable au STM32** : le bootloader système est en ROM
   et n'est pas reflashable, mais son **code peut être désassemblé** (chip.fail l'a fait sur STM32F2,
   sl. 129-130) et **une routine équivalente exécutée en flash utilisateur** pour la même fin.
7. **Prédire l'offset au lieu de le chercher — exécution symbolique** (même papier, §5, sur 78K0) :
   calculer statiquement les chemins d'exécution jusqu'à la section visée pour en déduire le nombre de
   cycles. ⚠️ **Honnêteté du bilan** (Table 4, p. 18) : cette méthode **n'améliore pas le taux de
   succès** — l'AGW + génétique de Bozzato reste devant (**4,2 % / 6,8 %** contre **3,2 % / 4,3 %**) ;
   elle **supprime la recherche d'offset**. Elle sature (*state explosion*) si l'offset est très
   éloigné du trigger.

8. ★ **Optimisation d'hyperparamètres : bandit (SHA) + optimisation bayésienne (SMAC)** — la
   **première transposition de ces méthodes à l'injection de faute** [corpus, Werner, thèse VERIMAG
   2022, p. 99 et p. 119] (c'est la **revendication de l'auteur**, pas un fait vérifié par ce projet).
   La recherche est **décomposée en deux étapes** (§6.3) : (1) optimiser la **forme du glitch sur un
   *test de caractérisation* indépendant de l'application** — le délai est **ignoré**, ce qui retire
   une dimension —, puis (2) balayer le **délai** sur la cible par simple recherche aléatoire (RS) ou
   grille (GS). Deux optimiseurs :
   - **SMAC** (*Sequential Model-based Algorithm Configuration*) — **optimisation bayésienne** :
     substitut = forêt aléatoire, acquisition = *Expected Improvement*, plus une **intensification**
     gérant un budget par configuration (supporte le non-déterministe).
   - **SHA** (*Successive Halving Algorithm*) — **bandit manchot** : budget réparti sur ⌈log₂(n)⌉
     tours, les pires moitiés éliminées à chaque tour.

   **Résultat mesuré sur 3 Cortex-M, en tête-à-tête vs son propre algorithme génétique (GA — famille
   de recherche employée par Bozzato en V-FI, stratégie 3) et la recherche aléatoire (RS)** —
   probabilité de faute maximale atteinte, Table 6.3 p. 115 :

   | MCU | SMAC | SHA | GA | RS |
   |---|:---:|:---:|:---:|:---:|
   | Cortex-M0+ | 0,52 | 0,53 | 0,49 | 0,49 |
   | Cortex-M3 | 0,77 | 0,81 | 0,52 | 0,24 |
   | Cortex-M4 | **0,95** | 0,79 | 0,81 | 0,71 |

   En **moins de 10 000 injections, SMAC identifie systématiquement des configurations de probabilité
   de faute supérieure à GA/SHA/RS** (p. 115) ; SHA converge **lentement** (« il ne tient pas compte
   des résultats précédents », p. 116). ★ **Sur l'attaque phare du projet** — bypass RDP du
   **STM32F103RB** par `Read Memory`, la cible de Bozzato — SMAC atteint **0,79** de probabilité de
   faute contre **0,37** pour GA à **6 000 injections**, et contourne la RDP *« deux fois plus vite
   qu'avec un GA »* (GA n'y parvient qu'à 12 000 injections) [Table 6.4, p. 117-119] — voir
   [`03`](03_METHODOLOGIE_CAMPAGNE.md) §3.1.

   ⚠️ **Deux garde-fous de lecture, à ne jamais relâcher :**
   - **Aucun benchmark contre Carpi (stratégie 5).** Werner se situe par rapport à Carpi **sur la
     méthode** — même découpage en deux étapes, mais il optimise la forme sur un **test de
     caractérisation** quand *« Carpi et al. optimisent directement sur l'application ciblée »*
     (p. 99-100) — il ne la **mesure jamais** contre l'*adaptive zoom & bound*. Les grandeurs sont par
     ailleurs **non commensurables** (probabilité de faute à budget d'injections fixé ≠ nombre de
     mesures / taux de succès pour atteindre une frontière de décision). **Ne pas chaîner « SMAC > GA »
     et « Carpi > GA » en un classement SMAC ↔ Carpi.**
   - L'optimisation porte sur la **forme** du glitch ; le **délai** reste à rebalayer par cible
     (étape 2) — même partage forme/temps que la règle de portabilité de Carpi (stratégie 5).

9. ★ **Simuler et inférer AVANT de chercher — le *vulnerability rate*** [corpus, Dureuil *et al.*,
   CARDIS 2015] : la **racine conceptuelle** des stratégies 6–8. Au lieu d'explorer l'espace de
   paramètres à l'aveugle, on **infère le modèle de faute `P(m|c)`** du couple (cible, équipement),
   puis on **simule** (outil **CELTIC**) l'effet de ce modèle sur l'application pour calculer un
   ***vulnerability rate*** qui **classe les attaques candidates** ; la campagne réelle ne traite
   ensuite que les mieux classées. *« Simulators provide exhaustiveness and reproducibility »* (p. 2) :
   la simulation **épuise gratuitement l'espace logiciel**, le banc ne paie que le **physique**. C'est
   précisément le découpage que Werner (stratégie 8) **automatise** et étend à l'optimisation de
   l'équipement. (Le mécanisme d'inférence `P(m|c)` lui-même est détaillé en **§3.6**.)

> ★ **La reproductibilité du modèle change l'économie de la recherche** [corpus, Rivière *et al.*,
> HOST 2015]. Sur le cache d'instruction d'un Cortex-M, une fois le point et les paramètres EMFI
> trouvés, le modèle de faute est **reproductible dans jusqu'à 96 % des cas** (p. 1). L'effort se
> déplace alors de *« répéter pour vaincre le jitter »* (§7) vers *« trouver le point reproductible »* :
> une méthodologie **« haut contrôle / haute reproductibilité »** (p. 1) vaut mieux qu'un grand nombre
> de tentatives bruitées. ⚠️ Mesuré en **EMFI** (contrôle spatial) ; en voltage glitch, sans contrôle
> spatial, la reproductibilité tient surtout à la **stabilité du PDN et du trigger**. (Le modèle de
> cache d'instruction sous-jacent : **§3.6**.)

**Efficacité comparée des formes (Bozzato, Tables 4–5)** : la forme d'onde arbitraire (**AGW**) est
**63 % plus rapide que le crowbar MOSFET** et **~5×** plus économe en glitchs, au prix de **plus de
resets** (jusqu'à 31,5 %) et d'un espace de recherche plus grand.

**Budgets de tentatives observés** (ordre de grandeur à provisionner) :

| Cible / attaque | Glitchs | Taux de succès | Durée |
|---|---|---|---|
| STM32F103 — bypass RDP, 128 kB | ~9 000 | ~5 % | < 1 min |
| STM32F373 — downgrade RDP L2→L1 (1 déclenchement) | ~25 | ~4 % | recherche 2 h |
| MSP430F5172 — mot de passe BSL, 32 kB | ~34 000 | 98 % | 16 min |
| Renesas 78K — SequentialDump, 60 kB (AGW) | **3,3 M** | — | **2 j 12 h** |
| Code durci (GlitchResistor, DSN'21) | — | **~10⁻⁵** | 99,7 % détecté |

> Contre du code durci, viser un **très grand nombre de tentatives** et le **cycle
> glitch→reset→re-trigger le plus court possible**.

---

## 6. Détecteurs de glitch et leurs angles morts

Table de référence (agrégée de TCHES 2024, DATE 2014, Deshpande 2018, Martín 2015). Ces détecteurs
sont des **blocs de design** qu'un fondeur *peut* instancier ; ce ne sont pas des blocs documentés
d'un STM32 de stock — mais leurs **angles morts sont des propriétés de mécanisme** qui se
transposent.

| Contre-mesure | Angle mort exploitable | Source |
|---|---|---|
| Détecteur à délai de garde (Zussa) | 100 % contre clock/voltage glitch (effet global) ; **~32 % seulement contre l'EMFI** ; délai figé en pré-silicium → **dérive PVT** | DATE'14 §II.D ; Deshpande p. 11 |
| PDL-1 / *Tunable Replica Circuit* Intel | `T_G < T_inv` (le launch-flop n'inverse pas) ; fenêtre `T_inv+T_setup < T_G < T_xor` | TCHES'24 pp. 163–166 |
| PDL-2 / PDL-3 | double-glitch avant propagation du XOR | TCHES'24 p. 167 |
| **Alarme resynchronisée sur front d'horloge** | un pic d'alarme **entre deux fronts est perdu** | TCHES'24 p. 165 |
| Détecteur RO / compteur | fenêtre aveugle `[t_attack, t_safe]` (Leniency Factor) ; **dérive process ±20 %**, vieillissement −3,5 %/10 ans | Deshpande pp. 25, 31 |
| Razor FF / canary | glitch calibré pour que **FF ET shadow latch** capturent le faux → indétectable | Deshpande p. 15 |
| CED / duplication | injecter **la même faute** dans l'opération réelle **et** la redondante | Deshpande p. 14 |
| Code de redondance | fautes indétectables = **les mots du code** (ex. LED64 : 14 mots de poids 4) | CASA Table 3 |
| Capteur analogique VDD | **latence de détection** ; ne voit que les glitchs **positifs** | Deshpande p. 16 |
| Tests statistiques en ligne (TRNG) | **rester sous le seuil** (ex. Longest-run à 20) | Martín p. 272 |
| PLL interne | très efficace contre le clock glitch ; contournable si `LOCKED` n'interrompt pas le calcul | TCHES'24 p. 176 |

> ★ **Recommandation n°1, transférable au STM32 : sous-alimenter puis glitcher.** TCHES 2024
> (p. 173) mesure qu'abaisser le cœur de **1,0 V à 0,93 V (−7 %)** fait passer le taux de
> **faux-négatifs de ~50 % à ~100 %**. Mécanisme (CASA éq. 2 ; SoK annexe C) :
> `t_pLH ∝ 1/(V_DD − V_th)²` — baisser VDD **rallonge les délais**, ce qui **relâche la contrainte
> de bande passante de l'injecteur et élargit la fenêtre temporelle utile**. Combinable avec le
> **chauffage** (même effet sur les délais : Ghalaty §3.2.4). C'est de la physique de délai de
> propagation, pas une propriété de topologie de détecteur — donc valable quel que soit le STM32.

> ★ **Le volet « chauffage » est désormais sourcé en direct — et il faut en corriger la formulation.**
> Il reposait ici sur une citation de seconde main (« Korak *et al.* **via CASA p. 4** »). Le deck
> **Ege, Korak, Hutter, Batina — *Clock Glitch Attacks in the Presence of Heating*** (FDTC 2014,
> **ajouté**) est cette source. Sur un **ATmega162** posé sur une **plaque chauffante**, à **deux
> températures seulement — 25 °C et 100 °C** :
>
> - ✅ **Ce qui est solide : le seuil de faute se DÉPLACE.** Le décalage du paramètre de glitch vaut
>   **+1,4 à +2,9 ns** (moyenne **≈ +2,2 ns**) et va **dans le même sens dans 35 mesures sur 36**.
>   ★ **Il est identique en nanosecondes absolues à 10 MHz et à 20 MHz** — un effet lié à la période
>   aurait été divisé par deux. C'est donc bien un **allongement du délai de propagation**, exactement
>   le mécanisme invoqué par la reco n°1, et **c'est ce qui rend le résultat transposable au voltage
>   glitching** (mêmes chemins critiques). *(Valeurs **lues sur graphe**, non imprimées.)*
> - ✅ **La chaleur fait apparaître des types de faute absents à froid** (et en fait disparaître
>   d'autres) : l'espace des fautes atteignables change, pas seulement leur timing.
> - ⚠️ **Ce qu'il ne faut PAS dire : « chauffer élargit la fenêtre ».** L'énoncé imprimé du deck
>   (sl. 31) est prudent — *« **SOME** types of faults are easier to induce due to increased time
>   frame with heat »* — et les mesures le confirment : la largeur de fenêtre **augmente pour
>   certaines catégories de faute, diminue pour d'autres, reste stable pour d'autres encore**. Ce qui
>   est robuste, c'est le **déplacement** du seuil, pas son **élargissement**.
> - ⚠️ **Aucun taux de succès n'est publié** : ce deck ne peut pas chiffrer un gain de succès par
>   chauffage. Et avec **deux points de température**, **aucun coefficient en %/°C n'est mesurable**.
>   Si un ordre de grandeur est indispensable : **≈ 0,03 ns/°C** (≈ +2,2 ns / 75 °C), à étiqueter
>   **estimation deux points dérivée de graphe** — et à **ne pas confondre** avec les **0,1 %/°C** de
>   Bozzato, qui compensent une autre grandeur.
> - ⚠️ **Le deck ne teste pas la tension** : il n'y a **aucune mesure du couplage
>   température × sous-alimentation**. Les deux moitiés de la reco n°1 restent donc sourcées
>   séparément — TCHES 2024 pour l'underpowering, ce deck pour la température.
> - ⚠️ **Vecteur = clock glitch.** Deux des catégories de faute observées (*« Repeat Same »*,
>   *« Repeat & Modified »* : une instruction **ré-exécutée**) s'expliquent par un **front d'horloge
>   supplémentaire** — **un glitch de tension n'ajoute aucun front**, donc pas d'équivalent attendu en
>   voltage FI. Ne pas reporter ces deux catégories dans la méthodologie voltage.
>
> **Conséquence opératoire** (voir [`03`](03_METHODOLOGIE_CAMPAGNE.md) §5 et §7) : un changement de
> température impose de **re-caractériser l'offset**, pas seulement de le compenser au premier ordre.

Le coût des détecteurs est dérisoire (DATE'14 Table I : +1 détecteur = **+0,3 %** de slices ;
détecteur RO Deshpande = **+0,23 %** surface, **+1,4 %** puissance) — un fondeur n'a aucune raison
de s'en priver, mais aucun de ces papiers ne prouve leur présence dans un STM32 donné.

---

## 7. Facteurs environnementaux et métriques de campagne

### 7.1 Environnement — sources de dérive à instrumenter

| Facteur | Effet chiffré | Source |
|---|---|---|
| **Température** | Bozzato : ±3 °C décale le timing optimal ; **compensation ~0,1 %/°C** sur le délai. *Peak Clock* : tout mesuré à **30,0 °C**, *« a few degrees already significantly shift the sensitivity thresholds »* | Bozzato p. 215 ; Peak Clock p. 88 |
| **Jitter de trigger** | ±2 µs sur le cas Renesas (RC interne + transmission de commande) | Bozzato p. 214 |
| **Données traitées** | les délais de chemin **dépendent des données** → un plaintext/état différent déplace le seuil de glitch | Ghalaty §3.2.4, pp. 32–33 |
| **Variabilité de l'exemplaire** | seuils détecteur ±20 % (process), −3,5 %/10 ans (vieillissement) → **caractériser l'exemplaire, pas la datasheet** | Deshpande pp. 31–32 |
| **Recharge du condensateur (Δ)** | si le condensateur ne se recharge pas assez vite, le **multi-glitch voltage devient physiquement impossible** | DSN'21 p. 405 |

### 7.2 Métriques scalaires (à porter dans le doc de méthodologie)

| Métrique | Définition | Source |
|---|---|---|
| **Fault Intensity (FI)** | `1/T_glitch` (clock) ; **profondeur × durée du creux** (tension) | Ghalaty éq. 3.1, p. 27 |
| **Fault Bias (FB)** | chemins violés / chemins totaux, à FI donnée ∈ [0,1] | Ghalaty éq. 3.2, p. 29 |
| **r_fault** | `N_effective / N_max` (fautes observées / possibles) | CASA éq. 4, p. 19 |
| **Leniency Factor** | `1 − t_attack/t_safe` — **largeur de la fenêtre aveugle du détecteur** | Deshpande éq. 4.3, p. 25 |
| **Δ (f_max = 1/Δ)** | temps min entre 2 injections — **borne physique du setup** | Martín Déf. 2, p. 275 |

> ★ **Métriques de *qualité d'un programme de test* de caractérisation** [corpus, Werner, thèse
> VERIMAG 2022, ch. 5, p. 80-93] — distinctes des métriques de campagne ci-dessus : **PR** (taux de
> propagation = résultats fautés / fautes injectées), **DR** (taux de discrimination = fraction de
> résultats fautés non ambigus entre modèles) et **CR** (taux de couverture des modèles), à
> **maximiser ensemble via le produit PR·DR·CR**. Un jeu minimal de 3 tests (IC/RC/MC, ARMv7-M)
> propage/discrimine/couvre *« ~8 % de mieux »* que les meilleurs tests antérieurs (p. 93). À relier
> au firmware de test / *nop-slide* de [`03`](03_METHODOLOGIE_CAMPAGNE.md) §7.

### 7.3 Le mode d'échec dominant : « rien » ou « crash », rarement entre les deux

SCIS 2019 (résultat **négatif** sur Xoroshiro128+) est instructif : entre « glitch sans effet »
(≤14 injections) et « crash complet » (≥15) il n'y a **quasiment aucune fenêtre exploitable**. Deux
règles en découlent :

1. **Balayer largeur ET offset à résolution fine** — la répétition n'est **pas** un substitut à
   l'intensité (14 glitchs faibles = rien ; 15 = device mort).
2. **Scorer explicitement en 5 catégories** : *positive / negative / false-positive / false-negative
   / **crash-reset*** (extension de la taxonomie TCHES'24 p. 162 avec la catégorie *crash* de SCIS).

---

## 8. Table de correspondance papier → apport → pertinence projet

| Papier | Apport principal | Pertinence |
|---|---|:---:|
| **Bozzato — Shaping the Glitch** (TCHES'19) | chaîne V-FI complète, BOM nommée, séquences RDP STM32F103/F373, AGW | **★★★** |
| **SoK 2025** (arXiv 2509.18341) | taxonomie, coûts, PicoGlitcher v2, physique (annexes B/C) | ★★★ |
| **Peak Clock** (ASHES'19) | over-clock PLL sur STM32F0 (HSE), contrôle d'alim DUT, thermique | ★★★ |
| **TCHES 2024 — Who Watches the Watchers** | comment défaire les détecteurs ; « underpower puis glitch » | ★★★ |
| **Glitching Demystified** (DSN'21) | ChipWhisperer + STM32F071, modèle de faute cycle-par-cycle, GlitchResistor | ★★ |
| **Skorobogatov — glitch to flash** | méthodo de balayage, économie du nb de tentatives (bumping) | ★★ |
| **CASA — Revisiting Fault Adversary Models** | modèle set/reset correct pour le voltage glitch | ★★ |
| **Ghalaty — thèse** (2016) | modèles de faute, Fault Intensity/Bias, métriques de campagne | ★★ |
| **Deshpande — thèse** (2018) | inventaire des détecteurs et de leurs angles morts | ★★ |
| **DATE 2014 — glitch detector** | 100 % de détection du voltage glitch (effet global) ; l'EMFI échappe | ★ |
| **Marotta — main.pdf + slides** (COSADE'24) | modèle énergie-seuil (pont conceptuel clock↔voltage), FPGA-interne | ★ |
| **Endo** (2011) | générateur d'horloge glitchy (compteur+2 DLL+MUX), 0,17 ns, FPGA | ★ |
| **Ning** (2018) | modèle de setup-violation, chemin critique (simulation) | ★ |
| **Surya** (iSES'20) | clock glitch **local** émulant l'EMFI, ASCON, FPGA | ★ |
| **Sneaky Glitch** (2024) | générateur d'horloge furtif, calibration TDC, résolution vs largeur réelle | ★ |
| **Martín** (TIFS'15) | underpowering/thermique élargissent la fenêtre, contournement de tests statistiques | ★ |
| **SCIS 2019** | résultat négatif : « rien ou crash », méthodo skip→SPA→glitch | ★ |
| **Kaur, Singh — Injecting Power Attacks** (Springer 2021) | génération power + clock glitch (Cadence 180 nm + VHDL), niveau portes/simulation | ★ |
| **SiliconToaster** (Abdellatif & Hériveaux, Ledger Donjon) | **injecteur EM DIY 5 V → 1,2 kV programmable** (transfo ×200 + Cockcroft-Walton ×4 + IGBT) → réf. du palier 1 kV de [`06`](06_EMI_INJECTOR_EMFI.md) | ★★★ (EMFI) |
| **Ordas 2015** (FDTC) | **modèle de faute EMFI** : *sampling faults* (bitset/bitreset, local, polarité) | ★★ (EMFI) |
| **Beckers 2023** (IEEE TC) | survey EMFI (100–1000 V, sondes direct/coupled, 4 paramètres, BBI) | ★★ (EMFI) |
| **Fraunhofer 2022 — EM-Fault It Yourself** (PAINE'22) | **1er EMFI sur CPU desktop AMD** (Ryzen 5 2600/Zen+) : banc réplicable (stage XYZ, délidage, ChipShouter 500 V), bypass vérif. ARK (succès ~22 %), underpowering VSoC 0,9→0,59 V aide l'EMFI → réf. x86 de [`06`](06_EMI_INJECTOR_EMFI.md) §7 | ★★ (EMFI) |
| **Nabhan 2024** (IOLTS) | mécanisme EMFI (PDN + clock tree) + capteur de détection | ★ (EMFI) |
| **O'Flynn — papier + slides** (ESCAR EU'20) | **seul cas EMFI in-situ sur ECU automobile réel** : bootloader BAM (MPC55xx/56xx PowerPC), ChipSHOUTER 444V, jeu de paramètres complet, confirme la dépendance à la polarité (Ordas 2015) sur cible réelle | ★★★ (EMFI) |
| **Toldo — slides** (hwio USA'23) | **banc EMFI DIY chiffré de bout en bout** (~2300 $) sur SoC IoT à secure boot ; apport = **méthodologie** (scoring 5 catégories par position, cartographie XY grossière→fine) et **3 obstacles de caractérisation** transférables (brown-out FreeRTOS, boucle éliminée par l'optimiseur, UART corrompu par l'injection) | ★★ (EMFI) |
| **False Injections** (Dartmouth'25, Mune/Timmers) | voltage ESP32 : **démolit le mythe « glitch sharp/sub-cycle »** (largeurs 200–5000 ns = 16–400× le cycle), interprétation énergétique, corruption→PC control | ★★★ |
| **No Hat 2022 — Glitching for code exec** (Raelize) | **desserrer les contraintes de timing** : corruption > skip, ciblage des transferts de données, *pointer sled*, attaques quasi-triggerless | ★★★ |
| **Google TV Streamer EMFI** (hwio NL'25, Timmers) | **EMFI réel → root** (MediaTek MT8696, ~1,8 GHz) : sonde EMFI Keysight/Riscure + platine XYZ, glitch de `setresuid`, attaque runtime sans trigger | ★★★ (EMFI) |
| **There Will Be Glitches** (escar'18, Milburn/Timmers/Pareja) | voltage : **extraction firmware 512 kB** d'un ECU auto (bypass UDS ReadMemory / interface debug), ~300 k glitchs / ~3 j | ★★★ |
| **Data Transfers → Arbitrary Execution** (PoC'19, Timmers/Mune) | modèle **corruption d'instruction → PC control** (`ret`/`blr`/`ldr`), simulateur + sled ; cite l'origine FDTC 2016 | ★★ |
| **PANDA 2018 — Advancing FI attacks** (Mune) | taxonomie : **le skip est un modèle de commodité, la faute réelle est la corruption** ; PC/SP control | ★★ |
| **Escalating Privileges in Linux** (FDTC'17, Timmers/Mune) | voltage : **privesc → root** en glitchant le check de `setresuid` ; scoring de campagne chiffré | ★★ |
| **KERNELFAULT** (BlueHat v17'17, Timmers/Mune) | voltage : rooting ARM/Linux ; grille **contre-mesures SW inefficaces** vs exploit-mitigations | ★★ |
| **Secure Boot Under Attack** (BHEU'18, Bogaard/Timmers) | voltage (VCC 1,2→0,9 V) : **bypass secure boot** + simulateur **FiSim** (Unicorn+Capstone) | ★★ |
| **QSEE Wifi Pro** (OffensiveCon'26, Raelize) | ⚠ **exploitation logicielle** (CVEs QSEE/TrustZone → EL3), **pas de FI** ; renvoie à un EMFI-EL3 antérieur (hors corpus) | ★ |
| **O'Flynn — *Fault Injection using Crowbars*** (ePrint 2016/810, **ajouté**) | **le** papier de référence du **crowbar** = Bloc B de la carte : topologie, MOSFET nommés (IRF7807 / IRLML2502), 5 plateformes, durées d'activation 135–635 ns, et *« un simple microcontrôleur suffit à piloter le MOSFET »* (p. 8) | **★★★** |
| **Controlling PC on ARM** (deck FDTC'16, Timmers/Spruyt/Witteman, **ajouté**) | **formalisation d'origine** du *corruption → PC control*, en **voltage sur STM32F415RG** ; `LDMIA` (1 bit à corrompre) réussit ~1 ordre de grandeur plus souvent que `LDR` (2 bits) — *« the instruction encoding matters »*, l'écart étant **lu sur graphe, non imprimé** | **★★★** |
| **Zussa *et al.*** (HOST 2014, **ajouté**) | **mécanisme mesuré au voltmètre on-chip** : glitch positif ⇒ faute par **oscillation négative** ; −14 V commandés → ~400 mV au die ; effets *offsetting / addition / sharping* | **★★** |
| **Carpi *et al.*** (CARDIS 2013, **ajouté**) | **stratégies de recherche de paramètres** chiffrées : *adaptive zoom & bound* = 192 mesures vs 2048, plancher théorique 112 ; verdicts INTERESTING/CHANGING ; forme portable entre exemplaires, timing non | **★★** |
| **Yuce, Schaumont, Witteman** (JHSS 2018, **ajouté**) | survey **côté attaquant** : 4 paramètres de faute, la taille dépend de l'**instruction** (ALU ⇒ 1 bit, `load` ⇒ n bits), scoring d'évaluation 3 catégories, **< 500 $** d'équipement | **★★** |
| **Moro *et al.*** (FDTC 2013, **ajouté**) | **modèle de faute EMFI sur Cortex-M3** : faute de **timing sur le transfert de bus Flash** (jamais la SRAM) ; seuil 174 V, saturation 186 V ; set-at-1 **propre au fabricant** | **★★** (EMFI) |
| **BADFET** (Cui & Housley, WOOT'17, **ajouté**) | **EMFI *second-order*** : fauter la **DRAM voisine** plutôt que le CPU ⇒ effondre les exigences de résolution ; injecteur **< 350 $** (300 V / 1100 V) ; 72/100 succès ; écueils de conception attestés | **★★** (EMFI) |
| **Faults in Our Bus** (NDSS 2024, **ajouté**) | fautes sur le **bus système du PCB** (ni CPU ni mémoire) ; **longueur de burst ⇒ type de faute** (20 = données, 100 = adresses) ; *register sweeping* → bypass TrustZone ; **chaîne RF sans HT** | **★★** (EMFI) |
| **Trouchkine *et al.*** (JCEN 2021, **ajouté**) | **4 modèles micro-architecturaux** (L1I *sticky skip*, MMU, L2, L1D+PFA) sur SoC **1,2 GHz sans délidage** ; le jitter de cache miss est le vrai obstacle ; ⚠ **pas** un Intel Core i3 | **★★** (EMFI) |
| **Safety != security** (deck FDTC'17, Pareja & Wiersma, **ajouté**) | FI sur MCU **ASIL-D** : taux par cible et par vecteur, et surtout **efficacité chiffrée des contre-mesures** (lockstep 90 %, ECC flash 68 %, parité RAM 14 %) ; « ISO 26262 ≠ Security » | **★★** |
| **Korak & Höfler** (deck FDTC'14, **ajouté**) | ⚠ **clock glitch, pas voltage** (underpowering = sensibilisateur) : **cartographie par étage de pipeline** sur ATxmega256 et Cortex-M0 — le *skip* vit au **fetch**, la corruption de données à l'**execute**, le **decode est intact** ; branchement en execute = *« no effects »* | **★★** |
| **Fill your Boots** (TCHES'21, **ajout gist**) | **FI sur bootloader embarqué** : premier **multi-glitch** documenté (STM8), ***grey-box glitching***, exécution symbolique pour prédire l'offset, **9 anti-patterns** de conception ; ⚠️ son cas **LPC1343 est un exploit logiciel, sans glitch** | **★★★** |
| **chip.fail** (deck 2019, **ajout gist**) | **voltage FI sur STM32F2** contre une protection réelle (RDP2→RDP1, Trezor One) ; **bootROM désassemblée : aucun test de RDP2, seulement de RDP0** ; glitcher open-source **~92 $** à **MUX MAX4619** (pas un crowbar) ; paramètres Trezor publiés | **★★★** |
| **COSIC — *Design Considerations for EM Pulse FI*** (**ajout gist**) | **seul EMFI sur STM32 du corpus** (STM32F411, non invasif) **et** seul papier de **conception d'injecteur** : banc **≈ 40 €**, sonde ferrite Ø 750 µm/4 spires, ★ **le facteur d'amortissement fixe la sélectivité temporelle** | **★★★** (EMFI) |
| **Gerlinsky — *Breaking CRP on NXP LPC*** (deck RECON'17, **ajout gist**) | ★ **asymétrie de l'espace des valeurs** : 4 mots activent la CRP contre 4,29 milliards qui la désactivent ; **origine du MUX MAX4619** ; shunt **10 Ω** en série avec le GND ; fautes = **adresses dans les registres** | **★★** |
| **NCC — *Microcontroller Readback Protection*** (whitepaper 2020, **ajout gist**) | **inventaire des protections en readback** et de leurs contournements (**§7 = fault injection**), plus le **versant défensif** (§10, bootloaders sûrs) — le seul document du corpus à traiter la protection elle-même | **★★** |
| **GD32/OFFZONE** (deck 2023, **ajout gist**) | ⚠️ **pas du FI** (courses SWD/NRST/DMA ; son voltage glitcher **échoue**, sl. 57) — mais ★ **attestation `[corpus]` du RP2040 + PIO** comme contrôleur de timing déterministe, **IRLML2502** nommé, et sémantique de protection **identique à la RDP** sur un **clone de STM32** | **★★** |
| **RHUL — *High Precision Laser FI using Low-cost Components*** (**ajout gist**) | **chiffre le palier laser** : diode **< 40 $**, switch 70 $, FPGA 35 $ ; impulsions **5 ns**, **multi-fautes sur cycles consécutifs** ; évalue les **codages défensifs** et propose une défense hybride | **★★** (laser) |
| **Hériveaux — *Black-box Laser FI on a Secure Memory*** (deck BH USA'20, **ajout gist**) | cible durcie **contre le voltage** (capteurs de glitch, bouclier, horloge interne) **mais sans contre-mesure laser** → argument « vecteur de repli » ; ★ **343 617 injections sans succès, puis succès en 2 min après re-caractérisation** | **★★** (laser) |
| **Skorobogatov — *Compromising device security via NVM controller vulnerability*** (PAINE'20, **ajout gist**) | l'**ECC de la NVM** devient la surface d'attaque : **terminaison précoce d'écriture** ⇒ retour au mode test/debug d'usine ; + FI **optique** 1064 nm > 40 mW par la face arrière | **★★** (laser) |
| **Breaking Bootloaders on the Cheap** (deck BH EU'19, **ajout gist**) | compagnon de *Fill your Boots* ; retenu pour ★ *« les bootloaders STM8 et STM32 sont sûrs contre les attaques **logiques** »* — donc **sur STM32, le FI est la voie** | **★** |
| **Ege, Korak, Hutter, Batina — *Clock Glitch Attacks in the Presence of Heating*** (deck FDTC'14, **ajouté**) | **source directe du volet « chauffage » de la reco n°1** (jusqu'ici citée via CASA) : à ΔT = 75 °C le seuil de faute **se déplace de ≈ +2,2 ns**, **identiquement à 10 et 20 MHz** ⇒ effet de **délai de propagation**, donc transposable au voltage. ⚠ Corrige la formulation du projet : le seuil **se déplace**, la fenêtre ne **s'élargit pas** systématiquement | **★★** |
| **Werner — thèse VERIMAG** (2022, **ajoutée**) | ★ **1ʳᵉ optimisation d'hyperparamètres en FI** : **SMAC** (bayésien) bat un algorithme génétique (GA — famille de recherche de Bozzato, §5 strat. 3) sur le bypass RDP STM32F103 (**2× plus vite**, 0,79 vs 0,37) ; recherche en **2 étapes** (forme sur test de caractérisation, puis délai). + **inférence de modèle de faute** (CELTIC, « 76 % expliqués ») et **métriques de test PR/DR/CR**. Vecteurs : power glitch + laser | **★★★** |
| **Lu — *Injecting SW Vulnerabilities with Voltage Glitching*** (arXiv'19, **ajouté biblio Werner**) | **voltage crowbar** sur PS Vita (F00D/ARM) → code exec + **dump boot ROM** ; confirme le ringing d'O'Flynn | **★★** |
| **Dureuil — *Filling the Gap using Fault Model Inference*** (CARDIS'15, **ajouté biblio Werner**) | ★ **racine de CELTIC/Werner** : inférence de modèle de faute `P(m\|c)` + métrique *vulnerability rate* | **★★** |
| **Rivière — *High Precision FI on Instruction Cache of ARMv7-M*** (HOST'15, **ajouté biblio Werner**) | EMFI **cache d'instruction** Cortex-M, modèle précis **96 %** — **source du `4CacheCorruption`** | **★★** |
| **Proy — *EM Pulse Effects on Superscalar µarch at ISA Level*** (arXiv'19, **ajouté biblio Werner**) | EMFI sur **cœur superscalaire** (Cortex-A9) : classification ISA + effets propres aux cœurs complexes | **★★** |
| **Maldini — *Optimizing EMFI with Genetic Algorithms*** (2019, **ajouté biblio Werner**) | **recherche de paramètres par GA** pour l'EMFI (vs random/exhaustif) — pendant EMFI de Carpi/Werner | **★★** |
| **Colombier — *Laser-induced Single-bit Faults in Flash*** (HOST'19, **ajouté biblio Werner**) | **laser**, bit-set à l'**instruction-fetch en flash**, MCU 32-bit → corruption d'instruction | **★★** |
| **Dutertre — *Laser-Induced Instruction Skip Fault Model*** (NordSec'19, **ajouté biblio Werner**) | **laser** : **nombre arbitraire de skips** (≠ single-skip) → efface des sections de firmware | **★★** |
| **Madau — *EMFI Susceptibility Criterion / Hotspots*** (CARDIS'17, **ajouté biblio Werner**) | critère de susceptibilité EMFI pour **localiser les hotspots** (balayage XY) ; ⚠️ **fourni par l'utilisateur** | **★★** |

---

*Suite : [`01_PRECONISATIONS_ARCHITECTURE.md`](01_PRECONISATIONS_ARCHITECTURE.md) (choix carte),
[`02_BOM_MATERIEL.md`](02_BOM_MATERIEL.md) (nomenclature),
[`03_METHODOLOGIE_CAMPAGNE.md`](03_METHODOLOGIE_CAMPAGNE.md) (attaque),
[`04_REFERENCES.md`](04_REFERENCES.md) (bibliographie annotée).*
