# Modèles de faute et mécanismes — connaissance transversale

> S'applique à tout vecteur (voltage, clock, EMFI) sauf mention contraire. Détails par
> vecteur : [`../by-vector/`](../by-vector/).

## 1. Le mécanisme unifiant clock et voltage glitching

Le SoK 2025 (arXiv 2509.18341, §3.1) : *« les fautes produites par le clock glitching et le
voltage glitching sont identiques »* — base commune : **métastabilité par violation de temps
de setup**. C'est pour cela que la littérature les traite souvent comme un seul mécanisme à
deux étages de commande différents (horloge vs alimentation).

## 2. Set/reset (stuck-at), pas bit-flip — le modèle physiquement correct

La formalisation CASA (Richter-Brockmann *et al.*, Bochum, §4.4) donne, par mécanisme :

| Mécanisme | Modèle formel | Nature de la faute |
|---|---|---|
| Clock glitch | `ζ(n, τ_sr, c_i)` | **set/reset** (stuck-at) dans la combinatoire |
| Voltage glitch / underpowering | `ζ(n, τ_sr, c_i)` — identique | idem |
| EM pulse | `ζ(n, τ_sr, m)` | échantillonnage dans les bascules |
| Laser | `ζ(n, τ_nang15, mc_∞)` | le plus général |

★ **Point le plus important pour la modélisation** [corpus, CASA §4.4] : pour un glitch de
clock/voltage, la valeur fautée est **l'ancienne valeur du registre** (échantillonnage trop
tôt), **pas l'inverse** de la bonne valeur. Un exploit ou une simulation basés sur du bit-flip
modélisent mal la réalité. La **sévérité** (combien de bits) **n'est pas contrôlable** ; seule
la **profondeur de chemin ciblée** l'est, via la durée du glitch. Le bit-flip reste un modèle
*worst-case* commode mais imprécis (CASA §6).

**Hiérarchie de couverture** [corpus, CASA §4.5] : un design sûr sous laser l'est sous EM /
clock / voltage glitch ; la réciproque est fausse.

⚠️ **Désaccord de littérature ouvert, à ne pas masquer** : Yuce *et al.* (JHSS 2018, p. 8)
affecte la polarité inverse — *« All of the aforementioned fault injection techniques are able
to induce **bit-flip** effects. In addition, laser and EM pulses are also able to induce
bit-reset, bit-set, and stuck-at faults »* — soit bit-flip pour clock/voltage, set/reset
réservé à laser et EM. **Asymétrie de preuve** : CASA *dérive* son modèle du mécanisme
physique, Yuce donne une ligne de taxonomie de survey. CASA reste la source de grade
« mécanisme » ; le désaccord est à signaler, pas à trancher par supposition.

## 3. Réalisme atteignable — la table de référence (Ghalaty)

Table 2.2 de la thèse Ghalaty (Virginia Tech, 2016, p. 13) :

| Injection | Chosen bit | Single bit | Byte | Random | Contrôle du timing |
|---|:---:|:---:|:---:|:---:|---|
| Glitch (clock/voltage) | – | – | ✔ | ✔ | **précis** |
| Underpowering (starving) | – | – | ✔ | ✔ | lâche |
| Voltage spike | – | – | – | ✔ | précis |
| EM pulse | – | ✔ | ✔ | ✔ | précis |
| Laser | ✔ | ✔ | ✔ | ✔ | précis |

**Conséquence directe** : un glitcher de tension **n'atteint pas** le modèle *chosen-bit*.
Réalistement : **byte fault et random fault**, avec un **bon contrôle temporel** mais
**aucun contrôle spatial**.

⚠️ **Nuance apportée par Zussa *et al.* (HOST 2014)** — à lire comme une table de
**contrôlabilité adverse** (ce que l'attaquant peut *choisir*), pas de **résultats
observables** (ce qui *sort*) : par voltage glitch sur un AES matériel FPGA, *« Most of the
induced faults were **single-bit faults** »* et *« voltage glitches make it possible to
inject **single-bit faults with very good timing accuracy** »* (p. 6-7). Portée à ne pas
outrepasser : chemin de données combinatoire, pas un flux d'instructions de MCU — la
transposition à une faute d'instruction n'est **pas établie**. Retenir : *single-bit* est
**observable** en sortie, il n'est pas **commandable**.

## 4. Les 4 étapes de la faute — squelette de toute campagne

[corpus, Ghalaty §2] :

1. **Fault Injection Access** — accès physique (broches CLK/VDD/VCAP, ou champ proche).
2. **Actual Fault Injection** — application du stress ; on contrôle timing + intensité,
   **jamais** la localisation (sauf EMFI/laser, contrôle *spatial*, toujours pas de contrôle
   *bit-exact*).
3. **Fault Effect** — effet logique **non garanti** : un stress physique peut ne produire
   aucune faute.
4. **Fault Observation** — propager l'effet jusqu'à une sortie observable.

Chaque étape est un **filtre multiplicatif** sur le taux de succès : instrumenter chacune
séparément, sinon on ne sait pas laquelle échoue.

## 5. De l'instruction skip à la corruption d'instruction

Le « skip » est un **modèle de commodité** ; la faute réelle est une **corruption
d'instruction**, dont le skip n'est qu'un sous-cas [corpus, PANDA 2018 sl. 18-20]. Preuve
expérimentale : *False Injections* (Dartmouth 2025) le démontre sur **ESP32 (Xtensa,
voltage)**, sl. 53-73.

**La corruption d'une instruction de transfert** (`ldr`/`ldm`/`ret`/`blr`) peut charger une
donnée attaquant directement dans le **program counter** → exécution arbitraire **sans
faille logicielle** [corpus, *Data Transfers → Arbitrary Execution*, PoC 2019, sl. 24-56].

### La formalisation d'origine — au bit près

*Controlling PC on ARM using Fault Injection* (Timmers, Spruyt, Witteman — deck FDTC 2016) :
on corrompt le **registre de destination** d'un `load`.

- `LDR r3` → `LDR PC` demande de mettre **2 bits** à 1 ; `LDMIA {r3-r10}` → `{r3-r10, PC}`
  n'en demande **qu'un seul** (bit 15 de la liste des registres).
- ★ **Conséquence chiffrée** : sur des campagnes « 10k » à banc identique, `LDR` ne donne
  **qu'~1 succès** là où `LDMIA` en donne **~26** — ⚠️ *comptés sur le nuage de points, non
  imprimés* (à lire comme un ordre de grandeur). La phrase imprimée est *« Success rate is
  different for ldr and ldmia — **the instruction encoding matters** »* (sl. 78-84).
- **Règle générale à en tirer** : **choisir l'instruction cible par sa distance de Hamming
  pèse plus que d'affiner le glitcher.** Corroboré côté EMFI par Moro (FDTC 2013) : les
  registres/instructions dont l'encodage **contient le plus de 1** fautent le plus.
- ⚠️ **Scission ISA** : les encodages imprimés sont en ARM/A32, la carte testée un
  Cortex-M4/Thumb-2 — le concept se transpose (LDR T3/T4, LDM T2 acceptent PC), **les motifs
  binaires imprimés non**.
- Instructions visées **à l'origine** : `LDR`/`LDMIA` dans des boucles de copie (données
  attaquant-contrôlées, exécutées en série, non protégées). Le cadrage plus large
  `ret`/`blr`/register-restore vient d'un deck **postérieur** (PoC 2019).

## 6. Où vit la faute dans le pipeline — cartographie sur MCU réels

[corpus, Korak & Höfler, deck FDTC 2014] — mesuré sur **Atmel ATxmega256** (8 bits, Harvard,
pipeline 2 étages) et **NXP LPC1114/Cortex-M0** (32 bits, von Neumann, pipeline 3 étages),
par **clock glitching** (voir [`../by-vector/clock-glitching.md`](../by-vector/clock-glitching.md)
pour le vecteur) :

| Étage | Effets observés | Modèle correspondant |
|---|---|---|
| **FETCH** | *« Fetch buffer not updated »* · *« Instruction not executed »* · *« Instructions executed twice »* · *« Program flow modification »* | c'est **là que vit le skip** |
| **EXECUTE** | *« Wrong results »* · *« Constant values »* · *« Varying values (TGlitch) »* · *« Data flow modification »* | c'est là que vit la **corruption de données** |
| **DECODE** | *« Decode stage not affected »* — sur les deux plateformes | — |

- ★ *« Varying values (TGlitch) »* : la valeur fautée **dépend de la durée du glitch** —
  confirmation sur MCU réel du principe §2 (on contrôle la **profondeur de chemin**, jamais
  la **sévérité**).
- ★ **Contre-intuition à retenir** : glitcher un **branchement en execute** donne
  *« No effects »* **sur les deux plateformes**. L'effet exploitable sur un branchement est
  **au fetch uniquement**. ⚠️ Ne pas opposer frontalement à *Peak Clock* (« les branchements
  échouent en premier ») ni à *Glitching Demystified* (« skip de branchement > 60 % ») : ces
  deux-là décrivent d'autres régimes (burst PLL soutenu, émulation ISA). Le désaccord porte
  sur le **régime**, pas sur le mécanisme.
- **Appui au modèle « corruption des transferts »** : `ldr`/`str` fautés au fetch donnent
  *« Rd set to zero »* / *« Memory set to zero »* ; à l'execute, *« Address in Rd »* /
  *« Address in Memory »*.
- **Fait de dimensionnement** : fenêtre exploitable au fetch sur load/store — **~12 ns sur
  l'ATxmega (2 étages)** contre **~0,5 ns sur le Cortex-M0 (3 étages)** *(lues sur graphe,
  non imprimées)*. Un cœur Cortex-M étant à 3 étages, **tabler sur le régime étroit**.

## 7. Dépendance aux données traitées

Les délais de chemin **dépendent des données** — un plaintext/état différent déplace le seuil
de glitch [corpus, Ghalaty §3.2.4]. **Fixer les données traitées** pendant toute la phase de
caractérisation.

## 8. Progression par biais de faute

**Commencer par les fautes faiblement biaisées** : 1 bit → 7 valeurs candidates ; 2 bits → 55
[corpus, Ghalaty p. 43]. Séquence recommandée : 1-bit → 2-bit → 3-bit. Au-delà du seuil de
première faute, le comportement **sature** (bit-flip → 0,5, ~4 bits/8) et n'apporte plus
d'information [corpus, Ghalaty p. 128].

## 9. Modèle de faute EMFI — renvoi

L'EMFI a son propre débat de modèle (sampling faults vs faute de timing vs réconciliation à
deux voies) : voir [`../by-vector/emfi.md`](../by-vector/emfi.md) §1.

## Deux mécanismes précisés par les ajouts du gist `dev-zzo`

### EM pulse — ce qui fixe la sélectivité temporelle

[corpus, Beckers *et al.*, imec-COSIC]. Mécanisme retenu : **violation des temps de setup/hold** à
l'échantillonnage des bascules (p. 3) — cohérent avec Ordas (*sampling faults*) et avec le *set/reset*
du voltage glitch.
★ **Apport propre, mesuré sur STM32F411** : à sonde, position, tension et instant **identiques**,
seule la résistance d'amortissement change —
**amortissement critique** ⇒ **une écriture individuelle** fautée (registre par registre d'un `STM`) ;
**sous-amorti** ⇒ les **oscillations harmoniques allongent `t_sensitive`** et **plusieurs instructions
sont fautées simultanément** (p. 13-14).
⇒ **La sélectivité temporelle est une propriété du circuit d'injection, pas de la largeur commandée.**
Exact analogue EM du *sharping / addition* de Zussa côté voltage.

### Laser — effet dominant et surface NVM

[corpus, Kelly & Mayes, RHUL, p. 1] : sur AVR et ARM, l'effet dominant est le **skip — ou la mauvaise
lecture — de l'instruction en cours de fetch**, **hautement reproductible**, obtenu à **puissance
modeste et sans optique de précision**. Même **étage de pipeline** que le *skip* du clock glitch chez
Korak & Höfler : le vecteur change, l'étage atteint non.

★ [corpus, Skorobogatov, PAINE 2020] ajoute une **surface d'attaque absente de tous les autres
modèles du corpus** : les **codes correcteurs (ECC) des blocs NVM** et leur logique de contrôle
rendent l'application vulnérable à une **terminaison précoce de l'opération d'écriture NVM**, ce qui
peut **ramener le niveau de sécurité matériel au mode test/debug d'usine** en contournant la machine
à états. ⚠️ **Ce vecteur-là n'est pas optique** — il relève du **tearing** (coupure d'alimentation
pendant l'écriture) — et il se transpose à toute cible dont les réglages de sécurité vivent en NVM,
**y compris les *option bytes* d'un STM32**. Rien dans le corpus ne l'a testé sur STM32 :
**à caractériser**.

### Un rappel de granularité pipeline, formulé côté défenseur

[corpus, NCC Group, *Microcontroller Readback Protection*, p. 13] : glitcher le **fetch** donne le
*skip*, glitcher l'**exécution** donne un résultat faux — et *« glitching a pipelined processor will
often impact **multiple stages simultaneously** »*. Sur un pipeline à 2 étages, glitcher le fetch de
l'instruction visée **corrompt aussi l'exécution de la précédente**. Cohérent avec Korak & Höfler,
formulé ici en termes de conception défensive.

## Inférer le modèle au lieu de le postuler — l'approche CELTIC

★ [corpus, Werner, thèse VERIMAG 2022, ch. 4]. Plutôt que de *supposer* un modèle (skip,
corruption…), on l'**infère** en croisant une caractérisation **expérimentale** avec une simulation
**ISA** (simulateur **CELTIC**, lignée Dureuil [DPdC+15] — ⚠️ **pas** FiSim), ce qui donne une
probabilité **P(m|c)** par (modèle, configuration d'équipement) et **réduit l'écart
simulation↔expérimentation** (*« 76 % des résultats fautés expliqués en moyenne »*, p. 69).
★ **Fait pour le modèle de faute** : sur ses Cortex-M, les modèles **dominants** sont des **sauts
multi-instructions** (16/32/48 octets) et une **corruption du cache d'instruction**
(`4CacheCorruption`, ~90 % des fautes *power glitch* d'un MCU) — le *skip* d'UNE instruction (§5) est
un sous-cas d'un saut de **bloc**. ⚠️ Modèles **de ses cibles**, inférés — appui, pas loi générale.

★ **Racine et source, ajoutées avec la bibliographie de la thèse** : la méthode d'inférence `P(m|c)`
vient de **Dureuil *et al.* (CARDIS 2015)** `[corpus]` (métrique *vulnerability rate*, simulateur CELTIC
d'origine) ; et le modèle **`4CacheCorruption`** est caractérisé par **Rivière *et al.* (HOST 2015)**
`[corpus]` — EMFI sur le **cache d'instruction d'un ARMv7-M**, modèle précis à **96 %**.
