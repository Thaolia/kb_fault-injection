# Laser fault injection (LFI)

> ★ **Ce fichier a changé de statut.** Il s'ouvrait sur un avertissement de couverture indirecte —
> le corpus n'avait alors **aucune source laser de première main**. Ce n'est plus le cas : il compte
> désormais **68 PDF, dont 5 papiers laser** (section **I** de
> [`../docs/04_REFERENCES.md`](../../docs/04_REFERENCES.md)), entrés depuis la liste curatée
> `dev-zzo`. Le vecteur laser est donc **sourcé en première main**, avec cibles nommées, paramètres
> chiffrés et coûts.
>
> ⚠️ **Ce qui n'a pas changé** : le laser reste **hors du chemin de construction** de la carte
> RP2350/STM32 (voltage FI, puis EMFI). Ce qui suit est un **repère de vecteur alternatif**,
> réutilisable sur de futures cibles — pas une spécification de banc.

## 1. Position dans la hiérarchie des mécanismes

[corpus, Ghalaty, table de réalisme] : le laser est le **seul** mécanisme couvrant les
quatre colonnes de contrôlabilité — *chosen bit*, *single bit*, *byte*, *random* — avec un
**contrôle du timing précis**. C'est la référence haute de toute discussion de réalisme :
voir [`../cross-cutting/fault-models-mechanisms.md`](../cross-cutting/fault-models-mechanisms.md)
§3 pour la table complète.

[corpus, CASA, hiérarchie de couverture §4.5] : un design sûr sous laser l'est sous EM /
clock / voltage glitch — la réciproque est fausse. Le laser est donc le modèle **le plus
général**, formalisé `ζ(n, τ_nang15, mc_∞)`.

★ **Confirmation empirique du modèle de faute** [corpus, Kelly & Mayes, RHUL, p. 1] : sur AVR et ARM,
*« l'effet dominant est le **skip — ou la mauvaise lecture — de l'instruction en cours de fetch** »*,
et il est **hautement reproductible**. Même localisation que le *skip* du clock glitch chez Korak &
Höfler (étage **fetch**, cf. [`clock-glitching.md`](clock-glitching.md)) : le vecteur change, l'étage
de pipeline atteint non.

## 2. Coût et taux de succès

[corpus, SoK 2025, Table 1-2] :

| Coût bas | Coût haut | Taux de succès moyen | Contrôle spatial |
|---|---|---|---|
| 500 $ | 50 000 $+ | ≈ 100 % | **très local** |

À comparer à clock/voltage (50–600 $, ≈1,4 %, aucun contrôle spatial) et EMFI (4 000–10 000 $+,
≈2 %, local) — voir [`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md).

★ **La borne basse « 500 $ » est désormais détaillée** [corpus, Kelly & Mayes, p. 2-3] :
**diode laser 455 nm** récupérée d'un bloc **Nichia NUMB80**, *« available on Ebay for **less than
$40** in 2018 »* · **switch laser** (composant de LiDAR) sur carte d'évaluation, **70 $** ·
**FPGA Spartan-6** sur carte d'évaluation, **35 $** · ★ **et l'optique, qui domine le budget** : un
**microscope trinoculaire Leitz SM-LUX HL de 40 ans, ≈ 250 $ sur eBay** (p. 3), sur le point de
fixation d'appareil photo duquel la diode est montée — objectifs **10×** ou **20×**.
⇒ **≈ 395 $ au total**, contre ~145 $ pour la seule électronique. ⚠️ **Ne pas citer les 145 $ comme
le prix du banc** : le banc reste **sous** les 500 $ du SoK, il n'est pas « à 150 $ ».

## 3. Paramètres et bancs — sourcés

| Paramètre | Valeur | Source |
|---|---|---|
| Largeur d'impulsion | **5 ns (200 MHz)** | [corpus, RHUL, p. 1] |
| Énergie par impulsion | **≈ 2 mJ** (référence de comparaison) | [corpus, RHUL, p. 1] |
| Longueur d'onde (face avant, bas coût) | **455 nm** (bleu) | [corpus, RHUL, p. 2] |
| Longueur d'onde (face arrière) | **1064 nm** — *le silicium y est transparent* | [corpus, RHUL p. 2 ; Skorobogatov p. 3] |
| Puissance (face arrière, NVM) | **> 40 mW** focalisés | [corpus, Skorobogatov, p. 3] |
| Optique | objectif de microscope **50×** + fibre optique | [corpus, Hériveaux, sl. 5] |
| Positionnement | **platine XYZ motorisée** | [corpus, Hériveaux sl. 5 ; Skorobogatov] |
| Contrôleur de banc | **Scaffold** (open-source, Ledger Donjon) | [corpus, Hériveaux, sl. 5] |

★ **Le verrou de cadence a sauté** [corpus, RHUL, p. 1] : les **diodes laser à état solide**
remplacent le laser **YAG**, dont les **20 ms de recharge** entre impulsions interdisaient le
multi-fautes. Conséquence directe : **plusieurs fautes discrètes sur des cycles d'instruction
consécutifs** deviennent possibles — ce que le voltage FI n'obtient qu'au prix des difficultés
décrites dans [`voltage-glitching.md`](voltage-glitching.md) (recharge du découplage, `Δ`).

## 4. Pourquoi le laser est le vecteur de repli le plus sérieux

★ **L'argument le plus fort du lot** [corpus, Hériveaux, sl. 4]. L'**ATECC508A** (mémoire sécurisée,
employée dans le portefeuille matériel **Coldcard Mk2** aux côtés d'un **STM32L4**) implémente :
surface d'attaque logicielle réduite · firmware confidentiel · **capteurs de glitch de tension** ·
**bouclier top-metal** · **générateur d'horloge interne** — **et *« No laser counter-measures »***.

**Autrement dit : une cible durcie contre le voltage FI *et* le clock glitch peut rester nue face au
laser.** C'est la raison structurelle d'entretenir ce fichier, et elle complète l'argument EMFI
(l'EMFI échappe aux **détecteurs globaux**, cf. [`emfi.md`](emfi.md) et DATE 2014).

## 5. Faits de campagne transposables à tout vecteur

★ **Caractériser bat accumuler — mesuré, et l'écart est de cinq ordres de grandeur**
[corpus, Hériveaux, sl. 62 et 68] : une première campagne de **343 617 injections sur plusieurs
jours** donne **1 546 réponses** et **aucun succès**. Après **analyse** des réponses fautées
(elles trahissent un **écrasement de données**), **identification des paramètres optimaux** et
**nouvelle préparation d'échantillon**, le succès tombe en ***« two minutes of testing only »***.
Même leçon que Carpi côté voltage
([`../cross-cutting/parameter-search-methodology.md`](../cross-cutting/parameter-search-methodology.md)).

⚠️ **Coût matériel réel d'une campagne laser**, rarement imprimé [corpus, Hériveaux, sl. 69] :
*« Did we killed chips? **Yes!** »* — mauvaise configuration, **préparation d'échantillon ratée**,
et **corruption de données par écriture EEPROM défectueuse**. À provisionner en exemplaires.

★ **Une surface d'attaque que les autres vecteurs n'ont pas** [corpus, Skorobogatov, PAINE 2020] :
les ***self-induced fault attacks*** exploitent les **codes correcteurs d'erreur (ECC)** des blocs
**NVM** et leur logique de contrôle, qui rendent l'application vulnérable à une **terminaison
précoce de l'écriture NVM** — jusqu'à **ramener le niveau de sécurité matériel au mode test/debug
d'usine**, en contournant la machine à états censée le régir. ⚠️ **Ce vecteur-là n'est pas optique** :
il se déclenche par coupure d'alimentation pendant l'écriture. Il est listé ici parce que le papier
le combine avec de la FI optique, mais il relève du **tearing**, et il se transpose à toute cible
dont les réglages de sécurité vivent en NVM.

## 6. Défenses — le seul volet « codage défensif » du corpus

[corpus, Kelly & Mayes] est le seul papier du corpus à **évaluer les techniques de codage défensif
contre la FI** à l'aide d'un modèle de faute simplifié, et à proposer une **défense hybride** qui
**surpasse les défenses individuelles** sur leur cible. Utile en miroir de la §7 « anti-patterns »
de *Fill your Boots* ([`../cross-cutting/detectors-countermeasures.md`](../cross-cutting/detectors-countermeasures.md)) :
l'une décrit ce qu'il ne faut **pas** faire côté fondeur, l'autre ce qui marche côté développeur.

## 7. Ce que ce répertoire ne fournit toujours pas

Aucune **séquence d'attaque laser sur STM32** (les cibles sourcées sont un IC d'authentification, une
mémoire sécurisée, des AVR/ARM génériques), aucune **cartographie de die** exploitable, et aucun
**taux de succès** comparable à ceux du voltage FI.
⚠️ **Skorobogatov & Anderson, *Optical Fault Induction Attacks*** (**cité 9×** par les PDF du corpus)
reste **hors corpus** — c'est le candidat évident d'un futur ajout laser. **Ni le papier ni sa
référence bibliographique complète (année, conférence) ne figurent dans les sources du projet** : ne
pas lui prêter de venue avant vérification. ⚠️ Le *Sorcerer's Apprentice* de Bar-El, disponible dans
le même gist `dev-zzo`, **reste volontairement écarté** (survey fondateur dont `docs/00` restitue
déjà la substance) — cette exclusion-là n'a **pas** été levée.

## Deux modèles de faute laser ajoutés avec la bibliographie de la thèse Werner

★ `[corpus]` **Colombier *et al.* (HOST 2019)** — laser sur la **flash** d'un **MCU 32 bits** : faute **au
*fetch* de l'instruction** (valeur stockée intacte), **set de bits individuels** ⇒ corruption
d'instruction mono-bit. ★ `[corpus]` **Dutertre *et al.* (NordSec 2019)** — **remet en cause le modèle
« single instruction skip »** : par laser on induit un **nombre arbitraire de sauts**, de quoi
**effacer des sections entières de firmware** (fort impact sur le design des contre-mesures). Détail :
[`../../docs/04_REFERENCES.md`](../../docs/04_REFERENCES.md) §I.
