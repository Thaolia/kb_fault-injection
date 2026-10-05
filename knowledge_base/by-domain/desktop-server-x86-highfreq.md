# Desktop / serveur x86 et SoC ARM haute fréquence

> Vecteur : EMFI. Détail mécanisme : [`../by-vector/emfi.md`](../by-vector/emfi.md).
> ⚠️ Ce fichier contient une **correction d'attribution** entre deux papiers du corpus — à
> lire avant de citer l'un ou l'autre.

## 1. Seule preuve `[corpus]` d'EMFI sur CPU desktop x86

[corpus, Kühnapfel, Buhren, Jacob, Krachenfels, Werling, Seifert, PAINE 2022, *EM-Fault It
Yourself*] :

- **Premier EMFI rapporté contre un CPU desktop AMD** (Ryzen 5 2600, Zen+) : bypass de la
  vérification de signature de l'**AMD root key** (ARK) par l'AMD-SP, succès **jusqu'à
  ~22 %** (l'ARK se vérifie en 53 µs, timing précis requis).
- **Banc entièrement documenté et réplicable** : stage XYZ **2,5 µm**, ChipShouter **500 V**,
  **délidage** (capot indium à 200 °C), **trigger matériel obligatoire** pour éviter le délai
  du trigger logiciel, coût ~**6905 €**.
- ★ **Deux principes transférables** : **l'underpowering aide l'EMFI** (VSoC **0,9 → 0,59
  V**) — même logique que la reco « sous-alimenter puis glitcher » du voltage glitching,
  transposée à l'EMFI ; et **le trigger doit être déterministe** (matériel, pas logiciel).
- Cible aussi ARM/RISC-V selon les auteurs, au-delà du cas x86 démontré.

## 2. ⚠️ Correction d'attribution — ne pas confondre deux papiers du même groupe

Une erreur de citation a longtemps circulé attribuant à *Trouchkine et al., JCEN 2021*
(présent au corpus) une EMFI *« contre un Intel Core i3 sous Linux »*. **C'est faux sur les
deux points**, vérifié à la source :

- **JCEN 2021** [corpus, Trouchkine, Bukasa, Escouteloup, Lashermes, Bouffard] cible le
  **BCM2837** (Raspberry Pi 3 B, quad Cortex-A53 **1,2 GHz**, 28 nm) et le code s'exécute
  **bare-metal, sans aucun OS** — c'est l'argument méthodologique central du papier, qui
  reproche justement aux travaux antérieurs de mesurer sous OS. Le seul Intel du papier
  (E5-1620 v3) est le **poste d'analyse**, pas une cible.
- **Le cas x86/Core i3 réel** est un **autre travail des mêmes auteurs** — *Fault Injection
  Characterization on Modern CPUs — From the ISA to the Micro-Architecture*, WISTP 2019 —
  **hors corpus, `[ref]`**. À citer séparément si l'on veut étayer une affirmation x86.

**Conséquence** : Fraunhofer 2022 (§1) reste la **seule** preuve `[corpus]` d'EMFI sur CPU
desktop. Trouchkine/JCEN2021 étaye l'**ARM haute fréquence**, pas le x86.

## 3. Apports de Trouchkine/JCEN2021 pour le dossier « cible complexe »

- **Quatre modèles de faute micro-architecturaux**, tous prouvés par débogue JTAG : faute
  **persistante en cache L1I** (« *sticky instruction skip* », survit jusqu'à `ic iallu`) ;
  **corruption du mapping MMU** (pages remappées sur `0x0` ou décalées — invalider le TLB
  n'y change rien, c'est la config MMU elle-même) ; **décalage de blocs de 16 B en L2** (=
  la largeur du bus mémoire externe) ; **faute persistante en L1D exploitée par PFA** sur AES
  (une seule injection puis 10 000 chiffrements → clé ramenée de 2¹²⁸ à **2²⁴** hypothèses).
- **Aucun taux de succès n'est publié** (*« we are not able to measure the fault ratio »*) —
  ne pas en dériver de chiffre, ni le comparer aux ~22 % de Fraunhofer.
- **Pas de délidage requis** — sonde commerciale posée sur le boîtier. **1,2 GHz atteignable**
  sans délidage : la fréquence seule n'est pas rédhibitoire.
- ★ **Le vrai obstacle temporel est le jitter de cache-miss, pas la fréquence brute** : la
  durée d'un accès mémoire est imprévisible sur un CPU complexe. Parade : répéter à
  paramètres constants, l'instruction fautée variant dans un petit ensemble.
- ★ **Viser les transferts mémoire, pas le pipeline directement** : sur CPU complexe, le skip
  d'instruction direct **échoue** ; les fautes atterrissent dans les transferts de cache,
  plus lents donc à fenêtre plus large — même conclusion que la stratégie Raelize sur
  transferts de données ([`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
  §5), par un chemin totalement différent.
- ~700 ns de latence trigger → cible : la routine visée doit durer au moins cela.
- ⚠️ Banc = **chaîne RF continue** (amplitude en dBm, ampli 80 MHz–1 GHz) — non commensurable
  avec les paliers de tension en volts (250 V/500 V/1 kV) des injecteurs à décharge
  capacitive.

## 4. Pourquoi un premier NUC/desktop x86 reste dur

| Obstacle | Conséquence |
|---|---|
| **IHS** (capot métallique sur le die) | éloigne la bobine du silicium → plus d'énergie ou délidage |
| **Horloge ~1,4–2,3 GHz** | fenêtre de faute courte → synchro exigeante — ⚠️ nuancé : Trouchkine faute un cœur à 1,2 GHz sans délidage, la fréquence seule n'est pas rédhibitoire |
| **Jitter de cache-miss** | obstacle temporel dominant sur CPU complexe (voir §3) |
| Découplage massif + PDN complexe | absorbe les transitoires → énergie plus élevée |
| Multi-cœur, pas de trigger simple | difficile de synchroniser sur l'instruction visée |
| VRM externe (pré-FIVR) | aide plutôt le voltage FI que l'EMFI |

**Surfaces alternatives souvent plus productives sur un x86/NUC** : la flash SPI du BIOS, la
DRAM (Rowhammer, hors périmètre FI matériel), les rails d'alimentation plateforme, ou le ME —
plutôt que le die du CPU lui-même.

## 5. Cartographier une plateforme x86 par la latence — avant d'y injecter quoi que ce soit `[ref]`

§3 et §4 identifient l'obstacle dominant sur ces cibles : **le jitter des accès mémoire**, pas la
fréquence. Un outil public le mesure — et, en le mesurant, **cartographie le matériel**.

**`mmiotic`** (Christopher Domas — https://github.com/xoreaxeaxeax/mmiotic) : *« Latency x-ray for
undocumented hardware »*. Il chronomètre chaque **adresse physique** et déduit la structure du
matériel des ruptures de latence. Trois usages transférables à une campagne FI :

| Usage | Exemple imprimé au README |
|---|---|
| **Découper l'espace d'adressage sans se fier aux tables** | le premier Mo se découpe sur les frontières classiques par la seule latence ; `C0000`–`FFFFF`, annoncé *« System ROM »* par `/proc/iomem`, montre une **latence de DRAM** ⇒ BIOS *shadowé* |
| **Repérer des registres non documentés** | dans un espace de configuration à plancher ~675 cycles, deux dwords ressortent : `0xe4` (doorbell documenté) et `0xa4` (**non documenté**, valeur `deadbeef`) — même famille de registres, latences quasi identiques |
| ★ **Extraire une topologie d'alimentation sans pilote ni datasheet** | sur un GPU inactif, un bloc contigu de 48 ko où **chaque registre est lent** ; latence attribuée à un **round-trip SMU pour dégager un domaine *clock/power-gated*** ⇒ la carte de latences **révèle le découpage en domaines d'alimentation** |

★ **Pourquoi ce dernier point compte ici** : une campagne EMFI ou voltage sur plateforme complexe a
besoin de savoir **où sont les domaines** et **quand ils commutent**. Obtenir ça **sans délidage, sans
pilote et sans documentation** est exactement ce que §4 décrit comme manquant.

> ⚠️ **Trois bornes.** ① ★ **x86-64 exclusivement** : `arch_timing.h` fait `#error` sur `__i386__`,
> `__arm__` et `__aarch64__` (mesure par `rdtsc`/`rdtscp`) — **rien ne se transpose aux SoC ARM** de
> [`linux-android-arm-socs.md`](linux-android-arm-socs.md). ② ★ **Root sur la cible requis**
> (`/dev/mem`, ECAM via ACPI MCFG) : c'est un outil de **caractérisation d'une plateforme possédée**,
> pas d'obtention d'accès. ③ ⚠️ Certaines adresses **redémarrent la machine à la simple lecture**
> (déni de service matériel, hors périmètre FI). Détail et cadrage :
> [`../../docs/06_EMI_INJECTOR_EMFI.md`](../../docs/06_EMI_INJECTOR_EMFI.md) §7.1.
