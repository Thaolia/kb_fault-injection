# Méthodologie de recherche des paramètres — connaissance transversale

> Comment trouver les bons réglages (délai, tension/largeur, offset) sans les connaître à
> l'avance. S'applique à tout vecteur ; les valeurs numériques par vecteur sont dans
> [`../by-vector/`](../by-vector/).

## 1. Cadre général — le mode d'échec dominant à anticiper

Sur MCU, une injection passe le plus souvent de **« aucun effet »** directement à
**« crash/reset »** sans traverser la zone d'*instruction skip* exploitable [corpus, SCIS
2019, résultat négatif : 14 injections faibles = rien ; 15 = device mort]. Deux règles :

1. **Balayer largeur ET offset à résolution fine** — la répétition n'est **pas** un substitut
   à l'intensité.
2. **Scorer chaque tentative en 5 catégories** (extension de TCHES'24 + SCIS) :
   *positive* (faute injectée et détectée) / *negative* (rien) / *false positive* (alarme sans
   faute) / *false negative* (faute sans détection, ★ objectif) / *crash-reset* (mode
   dominant, à mesurer explicitement).

## 2. Ordre de recherche recommandé

1. **Balayage monotone du délai d'abord** [corpus, Skorobogatov, sl. 42] : *« Precision
   timing is not necessary — slowly increase the delay until the effect is observed. »*
2. **Récursion en précision** [corpus, DSN'21 p. 405] : partir d'un glitch large (~10
   cycles), affiner d'un facteur `1/(10·profondeur)` jusqu'à 100 % de succès. Convergence
   16–59 min.
3. **Algorithme génétique sur l'espace complet** (forme d'onde incluse) [corpus, Bozzato
   pp. 206–207] : fitness `F = S/T`, **50 tests/candidat** au départ, crossover uniforme
   `p=0,5`, **mutation la plus forte sur la durée**, replace-worst. Convergence 30 min → 10 h.
   Partir d'un petit ensemble de formes prédéfinies.
4. **Interlacer optimisation et attaque** pour ne pas gaspiller de tentatives [corpus,
   Bozzato p. 207].

### ★ La stratégie la mieux classée : dichotomie 2D « adaptive zoom & bound »

[corpus, Carpi *et al.*, CARDIS 2013] — comparaison de 4 stratégies sur 3 cartes à puce :

| Stratégie | Mesures, 1ʳᵉ étape | Taux de succès |
|---|---|---|
| Monte Carlo (aléatoire) | — | **0 %** (0/3072 ; il en faut 76 800 pour 11 succès) |
| FastBoxing | 2048 | 0,295 % |
| Algorithme génétique | 1560 | 0,313 % |
| ★ **Adaptive zoom & bound** | **192** | **1,175 %** |

**Plancher théorique** de la 1ʳᵉ étape, formule réutilisable telle quelle (p. 10) :

```
N = n · ⌈max(log₂(rangeV/resolutionV), log₂(rangeL/resolutionL))⌉
```

→ 112 mesures pour un espace [−5 ; −0,05] V × [2 ; 150] ns à résolutions 0,05 V / 2 ns.

**Le modèle sous-jacent, à reprendre tel quel** (p. 5-6) : recherche en **deux phases** —
d'abord la **forme** (tension, longueur), ensuite seulement l'**instant** d'injection — et
l'on vise la **frontière de décision** entre la région NORMAL et la région RESET/MUTE,
matérialisée par deux verdicts : **INTERESTING** (proche de la frontière) et **CHANGING**
(deux mesures identiques → verdicts différents). ★ C'est en ciblant la zone CHANGING et en
**répétant 3× chaque mesure** (pour absorber le jitter d'horloge interne) que les auteurs
cassent une carte **certifiée Common Criteria EAL4+** annoncée protégée contre le VCC FI
(p. 11-12) — voir [`../by-domain/smartcards-secure-elements.md`](../by-domain/smartcards-secure-elements.md).

★ **Règle de portabilité** (p. 11) : les paramètres de **forme** (tension, longueur) sont
**les mêmes d'un exemplaire à l'autre** du même composant — **les paramètres temporels,
non**. C'est la règle qui décide de ce qu'il faut recalibrer en changeant d'exemplaire.

⚠️ **Citer les pourcentages de Carpi avec leur définition** : les Tables 2/3 donnent des
**médianes par test**, les Tables 5/6 le **meilleur run observé** — deux définitions
différentes pour les mêmes cellules.

## 3. Recherche guidée par la physique du PDN (voltage)

[corpus, Zussa HOST 2014] — la faute ne naît pas sur le plateau de l'impulsion commandée mais
au **tip d'une oscillation négative**, et l'amplitude commandée n'est pas celle vue par le
silicium. **Mesurer la période de ringing du PDN de la carte AVANT de balayer la largeur.**
Trois régimes se déduisent de cette période :

| Effet | Largeur d'impulsion | Bénéfice mesuré |
|---|---|---|
| **Addition** | = demi-période du ringing | même creux au die pour **8 V au lieu de 14 V** commandés → moins de stress, donc moins de resets |
| **Sharping** | ≪ période | tip rétréci (le vrai levier de finesse, fixé par la carte) |
| **Offsetting** | = période complète | annule la 2ᵉ oscillation négative → évite d'injecter une faute parasite |

⚠️ **Réordonnancement à noter** : *« the pulse width value had **no significant effect** on
the induced voltage perturbations. The main parameters… were the **pulse amplitude and DC
component values** »* (p. 7). La largeur ne redevient décisive **que par le recouvrement**
ci-dessus. **Balayer amplitude + composante DC d'abord**, largeur ensuite et relativement à
la période de ringing.

★ **Cartographier le seuil plutôt que balayer en aveugle** [corpus, Zussa p. 7, Fig. 8] : à
chaque pas de temps, faire descendre la composante DC depuis une valeur sûre jusqu'à la
première faute. Carte de seuil de sensibilité par instant, plus informative qu'un balayage
uniforme.

★ **Balayer profondeur et largeur ENSEMBLE, le long de la diagonale** [corpus, *Controlling
PC on ARM*, sl. 61/63/65] : la zone de succès mesurée est une **crête diagonale** (plus la
tension est négative, plus le glitch peut être court), pas un point — balayer un axe puis
l'autre la manque.

## 4. Règles de balayage générales

- **Fixer les données traitées** pendant la caractérisation [corpus, Ghalaty §3.2.4] — voir
  [`fault-models-mechanisms.md`](fault-models-mechanisms.md) §7.
- **Monter l'intensité par pas fins depuis le point de non-effet** ; la zone utile est
  **étroite**, juste après le seuil de première faute.
- **Commencer par les fautes faiblement biaisées** (1-bit → 2-bit → 3-bit) [corpus, Ghalaty
  p. 43].
- **Stratégie différentielle multi-intensité** plutôt qu'à seuil unique — plus robuste au
  jitter de trigger du contrôleur [corpus, Ghalaty Table 5.1].

## 5. Élargir la fenêtre avant de chercher

- **Sous-alimenter** : abaisser VDD sous le nominal. [corpus, TCHES'24 p. 173] : **1,0 → 0,93
  V** fait passer le taux de faux-négatifs de ~50 % à ~100 %. Mécanisme :
  `t_pLH ∝ 1/(V_DD − V_th)²`.
- **Chauffer** — voir [`fault-models-mechanisms.md`](fault-models-mechanisms.md) et
  [`campaign-instrumentation-metrics.md`](campaign-instrumentation-metrics.md) pour le détail
  et les réserves (le seuil se **déplace**, la fenêtre ne s'**élargit** pas
  systématiquement).
- ⚠️ Aucun papier du corpus ne mesure le **couplage** sous-alimentation × chauffage : les
  deux leviers restent sourcés séparément.

## 6. Budgets de tentatives observés (ordre de grandeur à provisionner)

| Cible / attaque | Tentatives | Taux de succès | Durée |
|---|---|---|---|
| STM32F103 — bypass RDP, 128 kB | ~9 000 | ~5 % | < 1 min |
| STM32F373 — downgrade RDP L2→L1 (1 déclenchement) | ~25 | ~4 % | recherche 2 h |
| MSP430F5172 — mot de passe BSL, 32 kB | ~34 000 | 98 % | 16 min |
| Renesas 78K — SequentialDump, 60 kB (AGW) | 3,3 M | — | 2 j 12 h |
| Code durci (GlitchResistor, DSN'21) | — | ~10⁻⁵ | 99,7 % détecté |
| ECU auto — bootloader BAM (O'Flynn EMFI) | recherche position 4-6 h ; puis rapide | ~1,2–1,9 % (outlier 36,3 %) | — |
| Faults in Our Bus — register sweeping | ~40 injections | 62 % (données), 31 % (adresses) sur 10k | — |

> Contre du code durci, viser un **très grand nombre de tentatives** et le **cycle
> glitch→reset→re-trigger le plus court possible**.

**Efficacité comparée des formes** [corpus, Bozzato Tables 4–5] : la forme d'onde arbitraire
(AGW) est **63 % plus rapide** que le crowbar MOSFET et **~5×** plus économe en glitchs, au
prix de **plus de resets** (jusqu'à 31,5 %) et d'un espace de recherche plus grand.

## Trois stratégies de plus — profiler, prédire, mesurer

Les stratégies déjà listées (balayage monotone, récursion en précision, algorithme génétique,
*adaptive zoom & bound*) ont un point commun : elles **explorent** l'espace de paramètres. Les trois
suivantes le **réduisent** avant toute exploration.

### 1. Profiler avant d'attaquer — *bootloader grey-box glitching*

★ [corpus, *Fill your Boots*, TCHES 2021, p. 10]. **Problème** : sur une cible qui ne renvoie **rien**
tant que la protection tient (le bootloader STM8 coupe toute communication), on n'a **aucun retour**
avant le succès complet — *« a full search of the glitch parameters quickly leads to a **state
explosion** »* (p. 14). **Parade** : **flasher les sections critiques du bootloader en tant
qu'application utilisateur**, les instrumenter, profiler **chaque glitch séparément**, puis seulement
combiner.
**Transposition STM32** : la bootROM n'est pas reflashable, mais elle est **désassemblable**
(chip.fail l'a fait sur STM32F2) et la routine équivalente peut être **rejouée en flash utilisateur**.

### 2. Prédire l'offset par exécution symbolique

[corpus, même papier, §5, sur Renesas 78K0] : calculer statiquement les chemins d'exécution jusqu'à la
section visée pour en déduire le nombre de cycles, au lieu de balayer.
⚠️ **Bilan honnête** (Table 4, p. 18) : la méthode **n'améliore pas le taux de succès** —

| Stratégie | checksum | verify |
|---|---|---|
| **AGW + génétique** (Bozzato) | **4,2 %** | **6,8 %** |
| classes d'équivalence (ce papier) | 3,2 % | 4,3 % |
| impulsion + génétique | 2,8 % | 3,7 % |

Son apport est de **supprimer la recherche d'offset**, pas de mieux fauter. Elle **sature** (*state
explosion*) si l'offset est très éloigné du trigger.

### 3. Mesurer le protocole plutôt que balayer — la version simple et directement applicable

★ `[ref]`, Anvil Secure sur **STM32F401CC** (`docs_pdf/writeups/`, cité par URL). Deux horodatages à
l'**analyseur logique** suffisent à borner l'offset : commande `Read Memory` émise à **182,300 µs**,
réponse à **196,800 µs**. À **10 ns** par cycle ⇒ plancher `ext_offset` = **18 230 cycles** ; la
fenêtre utile s'avère être **18 300–18 370** (≈ **700 ns**).
**Deux mesures remplacent des heures de balayage** — applicable à toute cible dont le protocole est
observable (bootloader série, UDS, SWD).

### 4. Analyse de consommation pour localiser la fenêtre

Deux sources indépendantes emploient la même méthode, et elle mérite d'être systématisée :
- [corpus, chip.fail, sl. 137-144] : sur **STM32F2**, les **200 µs** suivant le reset séparent
  visiblement *BootROM → lectures Flash/Option Bytes → application* ; le boot complet dure **1,8 ms**.
- [corpus, GD32/OFFZONE, sl. 53-56] : identifie bootloader (0xC00 o), page flash (0x400 o) et
  *option bytes* (16 o) par leurs signatures de consommation.
- [corpus, *Fill your Boots*, p. 13] : profilage du reset via un **shunt de 30 Ω** ;
  [corpus, Gerlinsky, sl. 22-23] : **10 Ω** en série avec le GND de la cible.

⇒ **Un shunt de quelques dizaines d'ohms sur le retour de masse de la cible est l'instrument le moins
cher du banc, et celui qui économise le plus de tentatives.** Il recoupe le double rôle du `Rs`
d'O'Flynn (mesure **et** trigger).

## Optimisation d'hyperparamètres — SMAC (bayésien) & SHA (bandit)

★ [corpus, Werner, thèse VERIMAG 2022, ch. 6] — **première transposition de l'optimisation
d'hyperparamètres à l'injection de faute** (revendication de l'auteur, p. 99/119). Recherche en
**deux étapes** : (1) **forme** du glitch optimisée sur un **test de caractérisation indépendant de
l'application** (délai ignoré ⇒ une dimension de moins), (2) **délai** balayé sur la cible par
RS/GS. Deux optimiseurs : **SMAC** (optimisation bayésienne : forêt aléatoire + *Expected
Improvement* + intensification) et **SHA** (*Successive Halving*, bandit manchot).

**Mesuré vs son propre algorithme génétique (GA — famille de recherche de Bozzato) et recherche aléatoire (RS)** —
probabilité de faute max, 3 Cortex-M (Table 6.3, p. 115) :

| MCU | SMAC | SHA | GA | RS |
|---|:---:|:---:|:---:|:---:|
| Cortex-M0+ | 0,52 | 0,53 | 0,49 | 0,49 |
| Cortex-M3 | 0,77 | 0,81 | 0,52 | 0,24 |
| Cortex-M4 | **0,95** | 0,79 | 0,81 | 0,71 |

SMAC domine en < 10 000 injections ; SHA converge lentement. ★ Sur le **bypass RDP du STM32F103RB**
(`Read Memory`, la cible de Bozzato) : SMAC **0,79** vs GA **0,37** à 6 000 injections ⇒ RDP
contournée **2× plus vite qu'un GA** (p. 117-119).

⚠️ **Deux garde-fous :**
- **Aucun benchmark contre Carpi** (*adaptive zoom & bound*, §2) : Werner s'en distingue **sur la
  méthode** — forme optimisée sur un *test de caractérisation* vs *« directement sur l'application »*
  (p. 99-100) — sans jamais la mesurer contre. Grandeurs **non commensurables** (probabilité de faute
  à budget fixé ≠ mesures/taux à la frontière de décision). Ne pas en déduire un classement
  SMAC ↔ Carpi.
- « première fois » = revendication de l'auteur, pas un fait vérifié par ce projet.

> Transposable : **régler la forme du glitch par SMAC sur un test de caractérisation** avant de
> balayer le délai est, à ce jour, la méthode la plus rapide documentée du corpus pour accorder un
> glitcher *power-glitch* sur une cible de la classe STM32.

★ **Pendant EMFI** `[corpus, Maldini *et al.* 2019]` : la recherche de paramètres par **algorithme
génétique** appliquée à l'**EMFI** (là où l'état de l'art était *« random search or exhaustive »*) —
même famille GA que Bozzato (§2, n°3), côté électromagnétique.

## Garde-fou : ne jamais multiplier les taux d'un multi-glitch

★ [corpus, *Fill your Boots*, p. 13] : deux glitchs à **0,6 %** et **0,1 %** donnent **0,0001 %** une
fois combinés, là où le produit prédirait **0,0036 %** — **36 fois moins**, à cause du **pipeline
3 étages** (le contenu du pipeline au second glitch diffère de celui du profilage).
**Recaractériser dans la séquence complète.** Détail :
[`../by-vector/voltage-glitching.md`](../by-vector/voltage-glitching.md) §8.

## Caractériser bat accumuler — l'écart mesuré

★ [corpus, Hériveaux, sl. 62 et 68] : **343 617 injections sur plusieurs jours → 0 succès** ; après
analyse des réponses fautées et re-préparation de l'échantillon, **succès en 2 minutes**. C'est la
même leçon que Carpi (*zoom & bound* : 192 mesures contre 2048) et que le profilage préalable
ci-dessus, mesurée sur une cible commerciale.

---

## ★ Descendre depuis la région de CRASH plutôt que monter depuis le silence `[fait]`

> **Provenance : `[fait]`** — campagne EMFI sur bootloader LPC1114, 2026-10-28. Paramètres complets
> dans `docs/06` §1.8. ⚠ **n = 10** : c'est une méthode démontrée, pas un taux de succès établi.

Toutes les stratégies classiques de ce document partent **du bas** — Skorobogatov : *« augmenter
lentement le délai jusqu'à observer l'effet »* ; la récursion en précision de DSN'21 ; le balayage
d'intensité « par pas fins depuis le point de non-effet ». Une campagne réelle a fait **l'inverse
sur l'axe d'amplitude**, et c'est plus économique :

| Étape | Réglage | Observation mesurée |
|---|---|---|
| 1. **Ancrer sur le crash** | intensité **maximale**, offset balayé largement | point à **100 % de crashs** |
| 2. **Descendre** jusqu'à les faire cesser | pas grossier (~5 % de la plage) | **0 % de crash** atteint |
| 3. **Remonter finement** | pas fin (~1 % de la plage) | ★ **premier pas au-dessus : 50 % de crashs ET 10 % de succès** ; les deux pas précédents ne donnaient **rien** |

⇒ ★ **Le succès vit au BORD de la région de crash, et on l'atteint par le haut.**

**Pourquoi c'est plus efficace que de monter depuis le silence.** C'est la même **frontière de
décision** que la zone `CHANGING` de Carpi *et al.* (CARDIS 2013) — mais la **région de crash est
large et bruyante, donc triviale à trouver**, là où la région de succès est étroite. Partir du crash
fournit un **point d'ancrage gratuit** ; partir du silence oblige à balayer à l'aveugle jusqu'à
tomber dessus. C'est le même raisonnement que « viser la frontière plutôt que l'optimum », appliqué à
l'**amplitude** et non au temps.

⚠ **Trois réserves :**
1. On **traverse une zone à 100 % de crashs** — à réserver aux cibles qu'on accepte de redémarrer
   sans cesse, et à éviter si le découplage transforme les crashs en brownouts prolongés.
2. La méthode suppose que **l'intensité maximale crashe** ; si la cible encaisse tout, il n'y a pas
   d'ancrage et il faut revenir aux stratégies montantes.
3. ⚠ **Le scoring doit distinguer « crash » de « sans effet »** — sinon les étapes 1 et 2 sont
   indiscernables. C'est exactement ce que la catégorie *crash/reset* du scoring en 5 catégories
   existe pour capturer, et c'est ici qu'elle **porte la recherche** au lieu d'être un simple
   compteur de déchets.

★ **Complément indispensable** : cette méthode n'a de sens que si l'**oracle est valide**. Un
instrument mal réglé peut produire une **fausse fenêtre de ~1 %** qui ressemble à s'y méprendre à un
résultat — voir `cross-cutting/campaign-instrumentation-metrics.md`, section « Valider l'ORACLE ».
