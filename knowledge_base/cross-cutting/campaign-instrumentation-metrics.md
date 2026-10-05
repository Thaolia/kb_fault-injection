# Instrumentation de campagne et métriques — vue transversale

## 1. Scoring — trois taxonomies documentées

**Générale, 5 catégories** (extension TCHES'24 + SCIS 2019) :

| Catégorie | Signification |
|---|---|
| positive | faute injectée **et** détectée par la cible |
| negative | pas de faute, pas de détection |
| false positive | pas de faute mais alarme → sur-sensibilité |
| false negative | faute **et** pas de détection → ★ objectif |
| crash / reset | device hangé/redémarré → **mode dominant, à mesurer** |

**Automobile, 6 résultats → 5 libellés** [corpus, O'Flynn ESCAR 2020] : le papier énumère
*« six potential results »* — ① pas d'effet (mot de passe refusé) = **Normal** · ② reset cible
= **Err-Reset** · ③ mot de passe accepté, erreur pendant le téléchargement = **Err-Protocol** ·
④ code téléchargé mais ne démarre pas et ⑤ code démarre mais flash toujours verrouillée =
**tous deux Err-RunFail** · ⑥ code démarre et imprime le mot de passe = **Success**.
⚠️ **Les auteurs regroupent explicitement ④ et ⑤** (*« differentiating between (4) and (5)
unreliable »*) — d'où **6 résultats mais 5 libellés distincts** ; ne pas chercher une 6ᵉ
étiquette qui n'existe pas. ⚠️ « Normal » (~92–98 %) est la catégorie « aucun effet », **pas un
taux de succès** ; le taux de bypass effectif (« Success ») est une ligne séparée.

**Évaluation professionnelle, 3 catégories** [corpus, Yuce p. 14] : vert = sans effet,
jaune = reset, rouge = succès observable — tracé dans les plans (largeur × tension) et
(largeur × wait cycles). Cohérent avec le scoring 5-catégories ci-dessus ; les plans 2D sont
la représentation à reprendre pour visualiser une zone de succès.

## 2. Métriques scalaires

| Métrique | Définition | Source |
|---|---|---|
| **Fault Intensity (FI)** | `1/T_glitch` (clock) ; profondeur × durée du creux (tension) | Ghalaty éq. 3.1 |
| **Fault Bias (FB)** | chemins violés / chemins totaux, à FI donnée ∈ [0,1] | Ghalaty éq. 3.2 |
| **r_fault** | `N_effective / N_max` (fautes observées / possibles) | CASA éq. 4 |
| **Leniency Factor** | `1 − t_attack/t_safe` — largeur de la fenêtre aveugle du détecteur | Deshpande éq. 4.3 |
| **Δ (f_max = 1/Δ)** | temps min entre 2 injections — borne physique du setup (recharge du condensateur) | Martín Déf. 2 ; DSN'21 p. 405 |

## 3. Facteurs de dérive environnementale

| Facteur | Effet chiffré | Source |
|---|---|---|
| **Température (voltage/clock)** | Bozzato : ±3 °C décale le timing optimal ; **compensation ~0,1 %/°C** sur le délai. *Peak Clock* : tout mesuré à 30,0 °C, « a few degrees already significantly shift the sensitivity thresholds » | Bozzato p. 215 ; Peak Clock p. 88 |
| **Jitter de trigger** | ±2 µs sur un cas RC interne + transmission de commande | Bozzato p. 214 |
| **Données traitées** | délais dépendants des données → un plaintext/état différent déplace le seuil | Ghalaty §3.2.4 |
| **Variabilité de l'exemplaire** | seuils détecteur ±20 % (process), −3,5 %/10 ans (vieillissement) | Deshpande pp. 31–32 |
| **Recharge du condensateur (Δ)** | si le condensateur ne se recharge pas assez vite, le multi-glitch devient **physiquement impossible** | DSN'21 p. 405 |

### ★ Le cas « chauffage » — source directe et ses réserves exactes

[corpus, Ege, Korak, Hutter, Batina — *Clock Glitch Attacks in the Presence of Heating*, deck
FDTC 2014] — sur un ATmega162, entre **25 °C et 100 °C** :

- **Le seuil de faute se DÉPLACE** de **+1,4 à +2,9 ns** (moyenne ≈ +2,2 ns), même sens dans
  35 mesures sur 36. ★ **Identique en ns absolues à 10 MHz et 20 MHz** — signature d'un
  **allongement du délai de propagation** (pas un effet de période), ce qui rend le résultat
  transposable au-delà du clock glitching. *(Valeurs lues sur graphe, non imprimées.)*
- La chaleur fait **apparaître des types de faute absents à froid** (et en fait disparaître
  d'autres) — l'espace des fautes atteignables change, pas seulement leur timing.
- ⚠️ **Ce qu'il ne faut PAS dire : « chauffer élargit la fenêtre »**. L'énoncé imprimé est
  prudent — *« SOME types of faults are easier to induce due to increased time frame with
  heat »* — et les mesures le confirment : la largeur **augmente pour certaines catégories,
  diminue pour d'autres, reste stable pour d'autres encore**. Ce qui est robuste, c'est le
  **déplacement** du seuil, pas son **élargissement**.
- ⚠️ **Aucun taux de succès n'est publié** ; deux points de température ⇒ **aucun coefficient
  en %/°C mesurable**. Ordre de grandeur si nécessaire : **≈ 0,03 ns/°C** (≈ +2,2 ns / 75 °C),
  à étiqueter *estimation deux points dérivée de graphe* — **ne pas confondre** avec les
  **0,1 %/°C** de Bozzato ci-dessus, qui compensent une autre grandeur (un délai relatif, pas
  un paramètre de glitch d'horloge).
- ⚠️ **Le couplage température × sous-alimentation n'est mesuré nulle part** — les deux
  moitiés de la recommandation « sous-alimenter + chauffer » restent sourcées séparément.
- ⚠️ **Deux catégories de faute observées** (*« Repeat Same »*, *« Repeat & Modified »* :
  instruction ré-exécutée) supposent un **front d'horloge supplémentaire** — sans équivalent
  attendu en voltage FI ; ne pas les reporter hors du clock glitching.

**Conséquence opératoire générale** : après tout changement de température notable,
**re-caractériser l'offset** plutôt que le compenser au premier ordre.

## 4. Le mode d'échec dominant : « rien » ou « crash »

[corpus, SCIS 2019, résultat négatif sur Xoroshiro128+] : entre « glitch sans effet »
(≤14 injections) et « crash complet » (≥15) il n'y a **quasiment aucune fenêtre
exploitable**. Deux règles : balayer largeur ET offset à résolution fine (la répétition n'est
pas un substitut à l'intensité), et scorer explicitement en 5 catégories.

## 5. Pratiques de reproductibilité

- **Mesurer Δ** de la chaîne complète (contrôleur → cible, câble compris) — c'est la borne
  dure du multi-glitch [corpus, DSN'21 p. 405 ; Martín Déf. 2].
- **Power-cycle propre** entre tentatives (load switch) ; respecter le **délai de POR**
  (Power-On Reset, souvent 1,5–4,5 ms) avant re-trigger.
- **Répéter chaque point ~100 fois** — les effets sont subtils, la répétabilité est
  elle-même une donnée [corpus, TCHES'24].
- **nop-slide** (~160 instructions) avant le code d'analyse du firmware de test [corpus, Peak
  Clock p. 89] ; mesurer la fréquence cœur réelle via un timer togglant une GPIO à f_CPU/4
  pour caractériser la cible avant l'attaque.
- **Squelette de firmware de test réutilisable** [corpus, Korak & Höfler sl. 19] :
  `handshake "ready" → arm → trigger → instruction cible entourée de nop → renvoi du résultat`.
- **Obstacles de caractérisation transférables** [corpus, Toldo, hardwear.io 2023, p. 16] :
  détection de brown-out non dédiée à l'injection qui interfère ; boucle de test **éliminée
  par l'optimiseur du compilateur** → passer en assembleur inline ; transferts UART
  **corrompus par l'injection elle-même** → déporter la communication sur GPIO plutôt que
  sur l'UART-USB intégré.
- **Justification du power-cycle obligatoire** [corpus, *Peak Clock* p. 88] : **64,2 % de
  crashes** observés sur une campagne AES sans coupure propre entre tentatives.

## Mesurer le jitter AVANT de choisir un trigger — le cas des cibles à cache `[ref]`

Sur MCU, le trigger est un front franc (I/O, NRST, montée d'alimentation) et son jitter se compte en
ns. Sur **CPU complexe**, deux faits `[corpus]` déplacent le problème :

- **Fraunhofer** impose un **trigger matériel** *« pour éviter le délai du trigger logiciel »* ;
- **Trouchkine** mesure **~700 ns** de latence trigger → cible et désigne le ***jitter de cache
  miss*** — et non la fréquence d'horloge — comme **l'obstacle temporel dominant**.

⇒ La question opératoire n'est donc pas *« quel délai ? »* mais ***« quel délai est
reproductible ? »***. C'est une grandeur qui se **mesure**, et un outil public le fait :

**`mmiotic`** (Christopher Domas, C, 2026 — https://github.com/xoreaxeaxeax/mmiotic) chronomètre
n'importe quelle **adresse physique** et rapporte, par adresse, **`min` / `max` / `stdev`** en cycles.
★ **C'est le `stdev` qui en fait un instrument de campagne** : il distingue une latence *longue* d'une
latence *stable*. Son option `--find-target <s>` cherche une adresse dont le temps d'accès **atteint
une durée voulue**, en deux phases — scan aligné 4 octets retenant les N meilleurs candidats, puis
**escalade de largeur d'accès** (`4 o non aligné → 8 → 16 xmm → 32 ymm → 64 zmm → 512 fxrstor`,
vérifié dans `scan.c`) — ce qui fournit un ***stall* calibré** utilisable comme repère temporel.

> ⚠️ **Trois limites de portée.**
> ① ★ **Ce n'est pas un trigger, et encore moins un remplacement du trigger matériel** : c'est un
> **instrument de mesure et de sélection** de latence, en amont.
> ② ★ **Il s'exécute en root sur la cible** — l'accès que le FI cherche à obtenir. Son usage est donc
> la **caractérisation d'une plateforme déjà possédée** (réplique de banc), pas l'attaque.
> ③ ★ **x86-64 exclusivement** — `arch_timing.h` fait `#error` sur `__i386__`, `__arm__` et
> `__aarch64__`, et mesure par `rdtsc`/`rdtscp`. **Aucune transposition ARM.**
> ⚠️ Il trouve aussi des adresses dont la simple lecture **redémarre la machine** (déni de service
> matériel, hors périmètre FI) — à savoir avant de scanner une plateforme qu'on veut garder vivante.

---

## ★★★ Valider l'ORACLE avant d'interpréter quoi que ce soit `[fait]`

> **Provenance : `[fait]`** — mesuré sur banc le 2026-08-31 (campagne BAT32G135, `docs/07` §0bis).
> Étiquette hors des trois d'origine du projet : `[fait]` = **mesuré sur matériel réel**, et prime
> sur `[corpus]` pour la cible mesurée. Artefacts dans `tplink_tapo-20260909.tgz`.

**Rien de ce qui précède ne vaut si l'instrument de lecture ment.** Trois pièges, tous génériques
— aucun n'est propre à une famille de MCU.

### A. Un lien de debug trop rapide imite PARFAITEMENT une puce verrouillée

**~7 000 tirs** classés « le port de debug ne répond pas », conclusion tirée *« cible verrouillée,
il faut gagner la course »*. **Faux : la puce était grande ouverte depuis le début.** Cause :
horloge SWD à la vitesse maximale, sur fils volants sans résistances série ⇒ l'échantillonnage
tombe à côté.

| Signature observée | Ce qu'elle démontre |
|---|---|
| **`ACK = 0x7`** | `0b111` n'est **aucun** des trois codes valides (`OK=1`, `WAIT=2`, `FAULT=4`). Une cible qui **refuse** renvoie un code **valide** ; un code impossible dénonce une lecture **décalée** |
| **`DPIDR = 0x1780_28EF`** | c'est **exactement** `(0x0BC0_1477 << 1) \| 1`, soit un identifiant ARM canonique **décalé d'un bit**. ★ Du bruit ne tombe pas par hasard sur le décalage binaire d'une valeur valide |

⚠⚠ **Et cela FABRIQUE une fausse fenêtre** : taux de « réussite » ~**1 %**, avec un **pic apparent
à 520 µs** et zéro ailleurs — l'allure exacte d'une fenêtre de course. C'était un **artefact
d'échantillonnage**. Une campagne entière pouvait s'optimiser autour d'un maximum inexistant.

> ★ **Règle** : *avant de déclarer une cible protégée, ralentir l'horloge du lien de debug et
> relire son identifiant. Si la valeur lue est le décalage binaire d'un identifiant valide, le
> problème est électrique, pas cryptographique.* La vitesse maximale sert au **débit d'un dump**,
> **jamais à rendre un verdict**.

### B. Un état d'erreur COLLANT contamine la mesure suivante

Une lecture qui faute peut verrouiller un bit d'erreur persistant (sur ARM ADI : `STICKYERR` dans
`CTRL/STAT`), après quoi **toutes** les transactions échouent jusqu'à un effacement explicite.
L'opération d'après paraît alors échouer **pour une raison sans rapport**. ⇒ **effacer l'état
d'erreur entre deux mesures**, sinon le scoring impute à l'injection un résidu de la mesure
précédente.

⚠ Variante rencontrée : un registre d'état **write-1-to-clear** combiné à une primitive d'écriture
qui **auto-vérifie** ⇒ l'écriture correcte (écrire `0x1F`, relire `0x00`) est rapportée comme un
**échec**. Prévoir une exception **là et seulement là**.

### C. Un verdict négatif n'est pas une preuve — la sonde différentielle

Si la cible se bloque sur **toute** erreur de bus, le blocage ne dit **pas laquelle**. ⇒ rejouer la
même lecture sur une **adresse qui n'existe pas** : si le comportement est identique, l'instrument
**ne discrimine rien**.

★ C'est ainsi qu'une hypothèse séduisante a été **falsifiée** sur banc : on expliquait un blocage
par « le gestionnaire d'exception vit dans la mémoire protégée » ; en relocalisant la table de
vecteurs **et** le gestionnaire en RAM, le blocage **persistait** — et une adresse non mappée
bloquait **identiquement**. La vraie cause était bien plus simple : *ce cœur escalade toute erreur
de bus en blocage*. ⚠ **Corollaire opératoire** : un cœur bloqué **le reste** ⇒ **reset +
reconnexion + réinstallation entre chaque passe**, et **encadrer la série par deux contrôles
positifs** (un au début, un à la fin) pour prouver que le banc n'a pas dérivé en route.
