# Détecteurs et contre-mesures — angles morts exploitables

> Ces détecteurs sont des **blocs de design** qu'un fondeur/intégrateur *peut* instancier ;
> leur présence dans une cible donnée n'est jamais garantie par le corpus — mais leurs
> **angles morts sont des propriétés de mécanisme**, donc transposables.

## 1. Table de référence des détecteurs matériels

Agrégée de TCHES 2024, DATE 2014, Deshpande 2018, Martín 2015 :

| Contre-mesure | Angle mort exploitable | Source |
|---|---|---|
| Détecteur à délai de garde (Zussa) | 100 % contre clock/voltage glitch (effet global) ; **~32 % seulement contre l'EMFI** ; délai figé en pré-silicium → dérive PVT | DATE'14 §II.D ; Deshpande p. 11 |
| PDL-1 / *Tunable Replica Circuit* Intel | `T_G < T_inv` (le launch-flop n'inverse pas) ; fenêtre `T_inv+T_setup < T_G < T_xor` | TCHES'24 pp. 163–166 |
| PDL-2 / PDL-3 | double-glitch avant propagation du XOR | TCHES'24 p. 167 |
| Alarme resynchronisée sur front d'horloge | un pic d'alarme **entre deux fronts est perdu** | TCHES'24 p. 165 |
| Détecteur RO / compteur | fenêtre aveugle `[t_attack, t_safe]` (Leniency Factor) ; dérive process ±20 %, vieillissement −3,5 %/10 ans | Deshpande pp. 25, 31 |
| Razor FF / canary | glitch calibré pour que **FF ET shadow latch** capturent le faux → indétectable | Deshpande p. 15 |
| CED / duplication | injecter **la même faute** dans l'opération réelle **et** la redondante | Deshpande p. 14 |
| Code de redondance | fautes indétectables = les mots du code (ex. LED64 : 14 mots de poids 4) | CASA Table 3 |
| Capteur analogique VDD | latence de détection ; ne voit que les glitchs **positifs** | Deshpande p. 16 |
| Tests statistiques en ligne (TRNG) | rester sous le seuil (ex. Longest-run à 20) | Martín p. 272 |
| PLL interne | très efficace contre le clock glitch ; contournable si `LOCKED` n'interrompt pas le calcul | TCHES'24 p. 176 |

**Coût des détecteurs** — dérisoire pour un fondeur : +1 détecteur = +0,3 % de slices
[corpus, DATE'14 Table I] ; détecteur RO Deshpande = +0,23 % surface, +1,4 % puissance. Un
fondeur n'a donc aucune raison de s'en priver — mais aucun papier ne prouve leur présence
dans une puce donnée sans reverse-engineering.

## 2. La recommandation transversale n°1 : sous-alimenter puis glitcher

[corpus, TCHES 2024, p. 173] : abaisser le cœur de **1,0 V à 0,93 V (−7 %)** fait passer le
taux de **faux-négatifs de ~50 % à ~100 %**. Mécanisme (CASA éq. 2 ; SoK annexe C) :
`t_pLH ∝ 1/(V_DD − V_th)²` — baisser VDD **rallonge les délais**, ce qui **relâche la
contrainte de bande passante de l'injecteur et élargit la fenêtre temporelle utile**. C'est
de la physique de délai de propagation, pas une propriété de topologie de détecteur — donc
généralisable à toute cible dont le rail cœur est accessible.

Combinable avec le **chauffage** — voir
[`campaign-instrumentation-metrics.md`](campaign-instrumentation-metrics.md) pour le détail
sourcé et ses réserves (le seuil se **déplace**, il ne s'élargit pas nécessairement).

## 3. EMFI échappe aux détecteurs globaux

[corpus, DATE 2014] : un détecteur à délai atteint 100 % contre clock/voltage glitch (effet
global) mais **l'EMFI locale lui échappe** (> 10 % de bypass avec 5 détecteurs). Rappel : le
voltage glitch est le **plus détectable** des vecteurs bon marché — voir
[`../by-vector/emfi.md`](../by-vector/emfi.md) §2 pour l'exploitation de cet avantage.

## 4. Efficacité chiffrée des contre-mesures — classement transférable

[corpus, *Safety != security*, deck FDTC 2017, sl. 47, cible D1 ASIL-D] — le classement le
plus réutilisable du corpus, **au-delà de l'automobile** :

| Contre-mesure | Efficacité (résiste à la FI) |
|---|---|
| **CPU lockstep** | **90 %** |
| **ECC flash** | **68 %** |
| Alarme | 25 % |
| OTP ECC | 20 % |
| **Parité RAM** | **14 %** |

Conclusion de la source : « **ISO 26262 ≠ Security** » — un mécanisme de sûreté fonctionnelle
(safety) n'est pas conçu pour résister à un attaquant actif, et son taux de couverture de
pannes aléatoires ne prédit pas son efficacité contre la FI.

## 5. Les contre-mesures logicielles sont structurellement faibles face à la corruption

[corpus, *Controlling PC on ARM*, deck FDTC 2016, sl. 66-77] : *deflect* (délais aléatoires) /
*detect* (double check) / *react* (reset) atténuent mais ne suppriment pas le risque. Verdict
imprimé : *« You can lower the probability but you cannot rule it out! »* S'y ajoutent des
mitigations d'**exploitation** (n'exécuter depuis la mémoire que quand nécessaire, randomiser
l'adresse de destination des copies).
[corpus, No Hat 2022] : même conclusion par un autre chemin — les contre-mesures SW sont
contournées parce que le flot de contrôle est détourné **avant** qu'elles ne s'exécutent.
[corpus, KERNELFAULT] : grille contre-mesures **SW inefficaces** vs exploit-mitigations
(DEP/NX/ASLR/CFI) — les mitigations d'exploitation post-corruption (empêcher l'exécution
depuis une zone mémoire, randomiser les adresses de destination de copie) sont plus robustes
que la détection de la faute elle-même.
[corpus, *Faults in Our Bus*] : l'**intégrité de flot de contrôle** bloque le skip
d'instruction mais **la faute de bus la contourne** — une contre-mesure conçue pour un modèle
de faute donné n'arrête pas un modèle différent visant la même cible.

## 6. Exploiter la latence et le mauvais positionnement des capteurs

- **Capteurs analogiques VDD** : latence de réponse — un glitch plus court que le temps de
  réponse du comparateur passe ; ces capteurs ne voient souvent que les glitchs **positifs**
  [corpus, Deshpande p. 16].
- **Sous-alimenter** relâche simultanément la contrainte de bande passante de l'injecteur
  **et** dilue les seuils de détecteur (les zones « s'étirent dans le temps », [corpus,
  TCHES'24 p. 173]).
- **Caractériser l'exemplaire, pas la datasheet** : ±20 % de dispersion process sur les
  seuils, die vieilli = cible plus facile [corpus, Deshpande p. 31].
- **Cartographier le seuil d'alarme AVANT de chercher la faute** : dans TCHES'24 la région
  intermédiaire est purement *faux-positive* (bruit détecté sans gain). Viser la fenêtre
  aveugle `[t_attack, t_safe]` (Leniency Factor).

## Protection en lecture (readback) — l'inventaire côté fondeur

[corpus, Qasim Khan, NCC Group, *Microcontroller Readback Protection: Bypasses and Defenses*, 2020].
**Seul document du corpus à traiter la protection en readback comme un objet en soi** — celle que
visent toutes les attaques STM32 de ce projet — et le seul à fournir le **versant défensif**.

**Mécanismes réellement employés** (p. 3) : désactivation complète du debugger · interdiction de lire
les adresses flash mappées **en laissant le debug actif** · interdiction de lecture flash par tout
maître de bus **autre que le fetch d'instruction du CPU** · désactivation des lectures flash **dans le
bootloader** · **chiffrement du flash** ; souvent couplés à une protection en écriture.

**Familles de contournement**, chapitre par chapitre : broches de debug reconfigurées (§3) ·
interfaces de debug **partiellement** restreintes (§4) · **blocs mémoire effaçables indépendamment**
(§5) · interfaces de bootloader (§6) · **fault injection (§7)** · attaques invasives (§8) ·
protection d'un **flash externe** (§9) · **implémentation d'un bootloader sûr (§10)**.

## Anti-patterns de conception — la grille la plus actionnable du corpus

★ [corpus, *Fill your Boots*, TCHES 2021, p. 19]. Neuf motifs à chercher sur une cible **avant** de
lancer une campagne — chacun est une **économie de tentatives** :

| | Anti-pattern | Ce qu'il ouvre |
|---|---|---|
| **A1** | écriture RAM partielle en état protégé | compromission de la pile → ROP (cas LPC1343) |
| **A2** | fuite partielle de mémoire ou de registres | *cold-boot stepping*, reconstruction du flot |
| **A3** | réécriture partielle du flash | écrire un *dumper* dans un secteur |
| **A4** | effacement de puce incomplet ou non atomique | clés survivant à l'effacement |
| **A5** | code non *constant-time* | mot de passe récupéré octet par octet |
| ★ **A6** | **« default to unprotected »** | *n'importe quelle* corruption ouvre la puce — voir l'asymétrie 4 vs 4,29 milliards de Gerlinsky |
| ★ **A7** | **vérification non redondante** | *« le taux de succès décroît **exponentiellement** avec chaque vérification redondante »* |
| **A8** | trop de niveaux de protection | confusion du développeur sur le niveau réellement actif |
| **A9** | OCD et protection en lecture **séparés** | une voie d'accès oubliée annule toutes les autres |

★ **A6 appliqué au STM32** : la RDP est bâtie à l'envers (L1 = « toute valeur **sauf** `0xAA` »), donc
**protégée par défaut** — sauf que **le downgrade L2→L1 rejoue la même asymétrie**, et que sur
**STM32F2** la bootROM désassemblée *« ne teste que `0xAA` »* [corpus, chip.fail, sl. 130].
★ **A7 est la raison structurelle** du garde-fou multi-glitch
([`parameter-search-methodology.md`](parameter-search-methodology.md)).

**Mitigations matérielles citées** (p. 19) : **détection de brown-out sensible**, **horloge interne
randomisée** — au prix des performances et du coût, d'où la préférence des fondeurs pour le logiciel.
⚠️ **Mise en garde à retenir** [corpus, chip.fail, sl. 153] : *« **Brown out detector != glitch
protection** »*. Autres recommandations du même : composant à **moniteurs de glitch**, **tamper
actif**, tester sa conception **sur kit de développement**, écrire du code **résistant au glitch**.

## Le correctif d'A6 observé en production — protection en deux parties, activée par défaut

★ **Le corpus décrit l'anti-pattern A6 ; voici un fondeur qui l'a corrigé, et comment.** Source
**officielle** : *nRF52820 Product Specification* **v1.3 §4.8.2, p. 41** (Nordic, archivée dans
`../../datasheet/cible_nRF52820/`). Cas d'attaque correspondant, `[ref]` :
[`../by-domain/microcontrollers-mcu.md`](../by-domain/microcontrollers-mcu.md) §11bis.

Le nRF52 des premières séries est un **A6 manuel** : protection **désactivée par défaut**, activée
seulement si le développeur écrit `UICR.APPROTECT`, et chargée par une **initialisation purement
matérielle** qu'un unique glitch met en défaut. La révision suivante applique **deux correctifs
distincts**, tous deux transposables hors de ce composant :

| Correctif | Effet sur l'attaquant |
|---|---|
| ★ **Inverser le défaut** — la protection est **activée par défaut**, il faut agir pour l'ouvrir | supprime A6 à la racine : une corruption de l'octet ne peut plus « tomber » du côté ouvert |
| ★ **Scinder le verrou en deux parties, matérielle ET logicielle** — `UICR.APPROTECT = HwDisabled` **et** une écriture firmware `APPROTECT.DISABLE = SwDisable` | **défait l'attaque à une seule faute** : fauter l'initialisation matérielle ne suffit plus, le verrou logiciel tient |

**Ce que le second correctif coûte à l'attaquant, chiffré** : il impose un **multi-glitch**, donc la
pénalité mesurée de *Fill your Boots* — un double glitch réussit **36× moins** souvent que le produit
de ses taux individuels ([`parameter-search-methodology.md`](parameter-search-methodology.md)). C'est
le même effet qu'**A7** (vérification redondante ⇒ décroissance exponentielle), obtenu ici non par
répétition d'un test logiciel mais par **séparation des domaines** matériel / logiciel.

★ **Corollaire pour l'évaluation d'une cible inconnue** : la question *« la protection est-elle
activée ou désactivée par défaut ? »* prime sur *« combien de niveaux existe-t-il ? »* (A8). Et le
sens du verrou logiciel se lit dans **qui doit agir** : si le firmware doit écrire pour **fermer**
(cas `DBGSTOPCR.SWDIS` du BAT32G135, §10bis), il existe une **fenêtre de course** avant cette
écriture ; s'il doit écrire pour **ouvrir**, **il n'y a pas de course** — seulement deux fautes à
réussir.
⚠️ **Le revers défensif à ne pas oublier** : ce durcissement n'est pas rétroactif. Il dépend de la
**version de la puce** — deux composants portant la même référence commerciale peuvent relever de
régimes opposés, et le discriminant se lit sur le **marquage du boîtier** (§11bis).

★ **Le seul volet « codage défensif » évalué expérimentalement** du corpus vient du laser
[corpus, Kelly & Mayes, RHUL] : caractérisation d'un **jeu étendu de techniques de codage défensif**
au moyen d'un modèle de faute simplifié, et proposition d'une **défense hybride** qui **surpasse les
défenses individuelles** sur leur cible — le compromis explicite entre *code non défendu* et *code
sur-défendu inutilisable*.
