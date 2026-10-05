# Base de connaissances — Fault Injection (réutilisable)

> **Objet.** Ce répertoire distille les 68 PDF de `../docs_pdf/` (corpus du projet
> `voltage_glitch`) en une base de connaissances **indexée par sujet**, pensée pour être
> réutilisée sur de **futures cibles et de futurs vecteurs**, indépendamment du RP2350/STM32
> qui a motivé la constitution du corpus. `../docs/` reste le document de projet (BOM,
> schémas, méthodologie appliqués à *cette* carte) et **n'est pas modifié** par la présence de
> ce répertoire. Ceci en est une **vue transversale** : mêmes faits, mêmes citations, organisés
> par **vecteur** et par **domaine cible** plutôt que par document de projet.


> ★ **Cinq étiquettes de provenance dans ce répertoire.** `[corpus]` = un PDF de `../docs_pdf/`
> (cité par page) · `[ref]` = source publique externe (citée par URL) · `[reco]` = recommandation
> d'ingénierie · **`[fait]`** = **mesuré sur un banc réel** (date + journal cités) · **`[fw]`** =
> **lu dans le code source** d'un firmware (fichier + ligne). Chaque section qui emploie `[fait]` ou
> `[fw]` rappelle sa provenance dans son propre encadré d'ouverture.
> ★ **`[fait]` prime sur `[corpus]`** pour la pièce mesurée, **mais ne se généralise pas** : ce qui
> se transpose est la *question à poser*, pas la réponse. ⚠ **Un modèle n'est jamais un `[fait]`.**

## Convention de provenance (identique à `../docs/`)

- **`[corpus]`** — sourcé d'un PDF de `docs_pdf/`, cité par fichier + page (`p. N`) ou slide
  (`sl. N` pour les decks de présentation). Jamais paraphrasé au point de perdre la nuance.
- **`[ref]`** — source publique externe (talk vidéo, dépôt GitHub, page produit), citée avec
  URL. Les 4 talks vidéo du corpus ne sont qu'en **sous-titres auto-générés** : tout chiffre
  qui en vient et n'est pas recoupé indépendamment est marqué comme tel.
- **`[reco]`** — jugement d'ingénierie, minoritaire dans cette base (elle vise l'évidentiel).
- Une valeur **lue sur un graphe plutôt qu'imprimée** est explicitement marquée `(lu sur
  graphe, non imprimé)` — jamais présentée comme un chiffre aussi solide qu'un chiffre imprimé.
- Rien n'est inventé : un paramètre non sourcé reste **« à caractériser »**.

## Comment naviguer

Deux axes principaux, plus un socle transversal :

- **[`by-vector/`](by-vector/)** — organisé par **mécanisme physique d'injection**
  (qu'est-ce qui produit la faute, quels paramètres, quel équipement). Utile quand la
  question de départ est *« je veux faire du voltage glitching / de l'EMFI / du clock
  glitching, que sait-on ? »*
- **[`by-domain/`](by-domain/)** — organisé par **classe de cible** (quel OS, quel type de
  matériel, quelles protections rencontrées, quelles séquences documentées). Utile quand la
  question de départ est *« je vise un Android / un ECU automobile / une carte à puce, que
  sait-on ? »*
- **[`cross-cutting/`](cross-cutting/)** — connaissance **indépendante du vecteur et de la
  cible** : modèles de faute, méthodologie de recherche de paramètres, détecteurs et
  contre-mesures, classes d'équipement/coût, instrumentation et métriques de campagne.

Un même papier apparaît souvent dans plusieurs fichiers (ex. *Faults in Our Bus* est à la fois
un mécanisme EMFI et un cas ARM TrustZone) : chaque fichier ne répète que les faits qui lui
sont propres et renvoie aux autres pour le reste, afin d'éviter la dérive par duplication.

## Index

| Fichier | Contenu en un mot |
|---|---|
| [`by-vector/voltage-glitching.md`](by-vector/voltage-glitching.md) | mécanisme, crowbar, AGW, **où trouver le rail cœur**, paramètres, cibles MCU réussies |
| [`by-vector/clock-glitching.md`](by-vector/clock-glitching.md) | burst PLL, glitch de période, précondition horloge externe |
| [`by-vector/emfi.md`](by-vector/emfi.md) | sampling faults, second-order, bus-fault, paliers de tension, sondes |
| [`by-vector/laser-fi.md`](by-vector/laser-fi.md) | ★ **3 sources de première main** (paramètres, coûts, bancs) ; le laser comme **vecteur de repli** contre une cible qui détecte les glitchs de tension |
| [`by-domain/microcontrollers-mcu.md`](by-domain/microcontrollers-mcu.md) | STM32 RDP, **nRF52 APPROTECT**, BAT32 `OCDEN`, AVR, MSP430, Renesas, Cortex-M0/M3 |
| [`by-domain/linux-android-arm-socs.md`](by-domain/linux-android-arm-socs.md) | privesc Linux, root Android, TrustZone/OP-TEE |
| [`by-domain/automotive-ecu.md`](by-domain/automotive-ecu.md) | UDS, bootloader BAM PowerPC, ASIL-D |
| [`by-domain/smartcards-secure-elements.md`](by-domain/smartcards-secure-elements.md) | JavaCard, cibles certifiées EAL4+ |
| [`by-domain/iot-embedded-secure-boot.md`](by-domain/iot-embedded-secure-boot.md) | secure boot bare/RTOS, obstacles de caractérisation |
| [`by-domain/desktop-server-x86-highfreq.md`](by-domain/desktop-server-x86-highfreq.md) | AMD Ryzen, SoC ARM haute fréquence, faisabilité x86 |
| [`cross-cutting/fault-models-mechanisms.md`](cross-cutting/fault-models-mechanisms.md) | set/reset vs bit-flip, étages de pipeline, corruption d'instruction |
| [`cross-cutting/parameter-search-methodology.md`](cross-cutting/parameter-search-methodology.md) | stratégies de balayage, adaptive zoom & bound |
| [`cross-cutting/detectors-countermeasures.md`](cross-cutting/detectors-countermeasures.md) | détecteurs, angles morts, efficacité des contre-mesures |
| [`cross-cutting/equipment-cost-tiers.md`](cross-cutting/equipment-cost-tiers.md) | coûts, outils commerciaux et DIY par vecteur |
| [`cross-cutting/campaign-instrumentation-metrics.md`](cross-cutting/campaign-instrumentation-metrics.md) | scoring, métriques, facteurs de dérive |

## État du corpus source (68 PDF — thèse Werner + 8 papiers minés dans sa bibliographie, 2026-10-05)

**68 PDF**, tous lus et annotés dans `../docs/04_REFERENCES.md`. ⚠️ **Sections comptées = A–G + I** :
**12** voltage FI pratique & synthèse (dont le SoK 2025, la **thèse Werner** et **Lu**), 10 clock glitch/PLL,
6 modèles de faute/métriques, 6 détecteurs & protections, 17 EMFI, 12 exposés pratiques
Raelize/Riscure, **5 laser** — soit **68**. Les sections **H** (6 talks vidéo) et **J** (27 write-ups web) sont **`[ref]` et non
comptées**. Historique complet des ajouts et méthode de sourcing : `../docs/04_REFERENCES.md` §F et
`../README.md`.

★ **Ce que la dernière vague a changé dans ce répertoire** (10 PDF du gist `dev-zzo`) :

- **`by-vector/laser-fi.md`** cesse d'être un fichier de cadrage : le vecteur laser a **3 sources de
  première main** (paramètres, coûts, bancs, modèle de faute, défenses).
- **`by-vector/emfi.md`** gagne le **seul jeu de paramètres de conception d'injecteur** du corpus —
  et sur **STM32**.
- **`by-vector/voltage-glitching.md`** gagne le **piège du multi-glitch** et une **topologie de
  sortie** (MUX analogique) que le crowbar ne couvre pas.
- **`cross-cutting/detectors-countermeasures.md`** gagne l'**inventaire des protections en readback**
  et les **9 anti-patterns** de conception.
- **`cross-cutting/parameter-search-methodology.md`** gagne trois stratégies qui **réduisent**
  l'espace de recherche au lieu de l'explorer.

⚠️ **Statut des write-ups.** `../docs_pdf/writeups/` contient **27 write-ups de praticiens** convertis
en PDF. Les faits qui en proviennent sont **`[ref]`, jamais `[corpus]`**, et se citent **par URL,
jamais par page** (leur pagination est un artefact de notre conversion). Ils sont signalés comme tels
partout dans ce répertoire.

### Mise à jour du 2026-09-15 — lecture de deux write-ups déjà archivés

⚠️ **Cette mise à jour n'a bougé aucun compteur** (les write-ups restent **27**) : elle ne vient pas
d'un ajout de source, mais de la **lecture intégrale de deux write-ups déjà
présents** dans `../docs_pdf/writeups/` — LimitedResults, *nRF52 Debug Resurrection (APPROTECT
Bypass)* parties 1 et 2 — jusque-là comptés parmi les write-ups « non lus en détail ». S'y ajoute une
**datasheet constructeur officielle** archivée dans `../datasheet/cible_nRF52820/`, qui n'entre pas
davantage dans le compte du corpus.

Ce que cela change ici :

- **`by-domain/microcontrollers-mcu.md`** gagne une **§11bis** : le seul cas du répertoire où l'octet
  de protection **n'est jamais lu par du code** (le nRF52 n'a pas de bootROM) ⇒ fenêtre localisable
  **uniquement par analyse de consommation**, et **deux régimes de protection selon la version de la
  puce**.
- **`by-vector/voltage-glitching.md`** gagne la question *« où est le rail cœur ? »* traitée en propre
  (`VCAP` / `DEC1` / aucune broche) et une **troisième position dans le débat du découplage**.
- **`cross-cutting/detectors-countermeasures.md`** gagne le **correctif de l'anti-pattern A6 observé
  en production** : inverser le défaut, et scinder le verrou en parties matérielle et logicielle pour
  défaire l'attaque à une seule faute.
- **`cross-cutting/campaign-instrumentation-metrics.md`** et
  **`by-domain/desktop-server-x86-highfreq.md`** gagnent **`mmiotic`** `[ref]` — un outil qui **mesure
  le jitter de latence** sur plateforme x86-64 et en tire une **carte du matériel**. ⚠️ Instrument de
  **caractérisation d'une plateforme possédée** (root requis, x86-64 uniquement), **pas** un
  remplacement du trigger matériel.

## ★★★ Apport du 2026-09-16 — la première MESURE de banc du projet (`[fait]`)

> **Une nouvelle étiquette de provenance entre ici : `[fait]` = mesuré sur matériel réel.** Jusqu'à
> présent ce répertoire ne contenait que du `[corpus]`, du `[ref]` et du `[reco]` — de la lecture.
> ★ **Une mesure de première main prime sur un papier** quand les deux se contredisent, **mais elle
> ne vaut que pour la pièce mesurée** : ce qui se généralise est la *question à poser*, pas la
> réponse obtenue. ⚠ Et **un modèle n'est jamais un `[fait]`**, même recoupé par deux solveurs.
>
> Source : campagne **BAT32G135 / TP-Link Tapo T310** (août-septembre 2026), plus une campagne EMFI
> **LPC1114**. Les artefacts (dumps, journaux, firmware, outillage) vivent dans l'archive
> `tplink_tapo-20260909.tgz`, **hors de ce dépôt** ; les documents porteurs sont `../docs/07` et
> `../docs/09`.

- ★★★ **`cross-cutting/campaign-instrumentation-metrics.md`** gagne la section la plus transférable
  de toute la campagne : **valider l'ORACLE avant d'interpréter**. Un lien de debug **trop rapide**
  imite parfaitement une puce verrouillée — et fabrique une **fausse fenêtre de ~1 %** qui ressemble
  à un résultat. Deux signatures le trahissent (`ACK` impossible, identifiant **décalé d'un bit**).
  S'y ajoutent l'**état d'erreur collant** et la **sonde différentielle** (rejouer sur une adresse
  non mappée) qui a servi à **falsifier** une hypothèse séduisante.
- ★★ **`by-domain/microcontrollers-mcu.md`** gagne quatre faits mesurés sur ce qu'une protection en
  lecture ferme **vraiment** : la **RAM peut rester ouverte** quand la flash est fermée (et son
  **contre-exemple**, sur la même puce, qui annule la fuite) ; la protection peut viser **le cœur**
  et pas seulement le debugger ; le **port de debug survit au reset mais pas le bus** (transition
  franche, **aucun interstice**) ; et un **chip erase peut épargner une zone**.
- ★★ **`by-vector/voltage-glitching.md`** gagne la **méthode de dimensionnement de la maille
  crowbar** : `R_série` **se mesure** (`C_résid = τ / R`), le **réservoir** n'est pas optionnel, et
  surtout l'**amortissement de drain** — un composant que les schémas de principe omettent, sans
  lequel le nœud **oscille jusqu'à −2,37 V**. Plus deux protections obligatoires côté contrôleur
  (pull-down de grille, résistance série d'ADC) et la démonstration `[fw]` que **la largeur
  commandée n'est pas la largeur livrée**.
- ★ **`cross-cutting/parameter-search-methodology.md`** gagne une stratégie que le corpus ne
  documentait pas : **descendre depuis la région de crash** au lieu de monter depuis le silence —
  le succès vit **au bord** de la zone de crash, laquelle est large et donc facile à trouver.
- ★ **`by-vector/emfi.md`** gagne un **jeu de paramètres EMFI publié sur bootloader LPC1114**.
  ⚠ 290 V y est une **tension de bobine**, pas une profondeur de creux — et **n = 10**.
- ★ **`cross-cutting/equipment-cost-tiers.md`** gagne la **composition réelle d'un banc** : trois
  fonctions (temps / puissance / **oracle**), et le coût caché qu'un glitcher bas coût **ne sait
  souvent pas lire la cible**.

## Maintenance

Ce répertoire est une **photographie** du corpus au 2026-09-15 (**apport `[fait]` du 2026-09-16**). Quand `docs_pdf/` grandit
(nouveaux PDF ajoutés au projet), mettre à jour le(s) fichier(s) `by-vector`/`by-domain`/
`cross-cutting` concerné(s) dans la même session — ce n'est pas automatique. `../docs/`
reste la source de vérité pour l'historique des ajouts et leur justification.
