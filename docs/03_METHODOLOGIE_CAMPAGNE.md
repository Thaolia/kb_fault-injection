# 03 — Méthodologie de campagne (voltage glitching STM32)

> **Nature du document — SOURCÉ + pratique.** Les séquences d'attaque et les paramètres sont
> **extraits du corpus** (marqués **[corpus]** avec page) ; l'organisation en playbook est une
> recommandation d'usage.
> ★ **Depuis la campagne de banc de septembre 2026, une étiquette de plus** : **`[fait]`** =
> **mesuré sur un banc réel** (date citée). Elle porte le §1.1 (validité de l'oracle) et la
> stratégie 8 du §5. Une mesure de première main **prime sur le corpus** quand les deux se
> contredisent — mais elle ne vaut que pour la cible mesurée. Les **seules** séquences STM32 pleinement documentées dans le corpus sont
> **F103** et **F373** (Bozzato). Le reste est extrapolé et **à valider sur banc**.

---

## 1. Cadre général — le mode d'échec à anticiper

Sur MCU, le voltage glitch passe le plus souvent de **« aucun effet »** directement à
**« crash/reset »** sans traverser la zone d'*instruction skip* exploitable (SCIS 2019, résultat
négatif : 14 glitchs = rien, 15 = device mort). Deux règles fondatrices en découlent :

1. **Balayer largeur ET offset à résolution fine ; la répétition n'est pas un substitut à
   l'intensité.**
2. **Scorer chaque tentative en 5 catégories** (extension de TCHES'24 p. 162 + SCIS) :

   | Catégorie | Signification |
   |---|---|
   | **positive** | faute injectée **et** détectée par la cible |
   | **negative** | pas de faute, pas de détection |
   | **false positive** | pas de faute mais alarme → sur-sensibilité |
   | **false negative** | faute **et** pas de détection → **★ objectif** |
   | **crash / reset** | device hangé/redémarré → **mode dominant, à mesurer** |

### 1.1 ★★★ Valider l'ORACLE avant de croire la cible protégée `[fait]`

> **Nature : `[fait]`**, mesuré le **2026-08-31**. Rien ici n'est spécifique à une famille de MCU :
> c'est une règle de méthode, et elle a coûté une campagne entière avant d'être comprise.

**Le scoring des 5 catégories ci-dessus ne vaut rien si l'instrument de lecture ment.** Sur un banc
réel, **~7 000 tirs** ont été classés `no_dp` — « le port de debug ne répond pas » — et la
conclusion tirée était *« la puce est verrouillée, il faut gagner la course »*. **C'était faux : la
puce était en niveau 0, grande ouverte, depuis le début.** La cause était l'**horloge SWD réglée
trop vite** (`SWD SPEED 0`, aucun délai de bit, sur des fils volants sans résistances série) :
l'échantillonnage tombait à côté.

★ **Les deux signatures qui trahissent un problème ÉLECTRIQUE et non cryptographique :**

| Symptôme | Ce qu'il faut voir |
|---|---|
| **`ACK = 0x7`** | `0b111` n'est **aucun** des trois codes valides — `OK=1`, `WAIT=2`, `FAULT=4`. Une cible qui refuse renvoie un code **valide** ; un code impossible dénonce une lecture décalée |
| **`DPIDR = 0x1780_28EF`** | c'est **exactement un DPIDR ARM canonique décalé d'un bit** : `(0x0BC0_1477 << 1) \| 1`. ★ Un mot de bruit ne tombe pas par hasard sur le décalage binaire d'une valeur valide |

⚠⚠ **Le piège dans le piège : ça fabrique une fausse fenêtre.** Le taux de « réussite » atteignait
**~1 %**, avec un **pic apparent à 520 µs** et zéro à 100/300/900/1400 µs. Cela **ressemble
exactement à une fenêtre de course** — c'était un **artefact d'échantillonnage**. Une campagne
entière pouvait s'optimiser autour d'un maximum qui n'existait pas.

> ★★ **Règle générale à appliquer avant toute conclusion** : *avant de déclarer une cible protégée,
> RALENTIR l'horloge du lien de debug et relire son identifiant. Si la valeur lue est le décalage
> binaire d'un identifiant valide, le problème est dans le câblage, pas dans la puce.*
> Corollaires : **ne jamais utiliser la vitesse maximale pour un oracle** (elle est faite pour le
> débit d'un dump, pas pour un verdict), et **poser des résistances série de ~100 Ω** sur les lignes
> de debug (voir [`05`](05_SCHEMAS_ELECTRONIQUES.md) §8 règle 7).

★ **Second cas, même famille de piège : un état d'erreur COLLANT.** Une lecture qui faute peut
verrouiller un bit d'erreur persistant (sur ARM ADI : `STICKYERR` dans `CTRL/STAT`), après quoi
**toutes** les transactions suivantes échouent jusqu'à un effacement explicite — et l'opération
d'après semble échouer *pour une raison sans rapport*. ⇒ **effacer l'état d'erreur entre deux
mesures**, sinon le scoring attribue à l'injection ce qui n'est qu'un résidu de la mesure
précédente.

★ **Troisième : un verdict négatif n'est pas toujours une preuve.** Si la cible se bloque
(`LOCKUP`) sur **toute** erreur de bus, le blocage ne dit **pas** *laquelle*. La parade est une
**sonde différentielle** : rejouer la même lecture sur une **adresse qui n'existe pas**. Si le
comportement est identique, l'instrument ne discrimine rien, et il faut changer de sonde avant
d'interpréter. (Cas développé en [`07`](07_BAT32G135_FAULTYCAT.md) §2ter.2.)

---

## 2. Cibles STM32 et sémantique RDP

### 2.1 Readout Protection (RDP) — la protection à défaire

Sémantique confirmée pour la série F3 (Bozzato Table 1, **[corpus, p. 209]**), représentative :

| Niveau | Valeur RDP | Effet |
|---|---|---|
| **Level-0** | `0xAA` (`~RDP = 0x55`) | aucune protection |
| **Level-1** | **toute autre valeur** | debug autorisé mais **flash inaccessible** en bootloader/debug ; flash lue seulement en user mode |
| **Level-2** | `0xCC` (`~RDP = 0x33`) | bootloader **et** debug désactivés ; **irréversible** (y compris pour STMicroelectronics) |

> **Conséquence pour le modèle de faute.** Passer de **L2 → L1** ne demande de corrompre **qu'un
> seul bit** (L1 = « toute valeur ≠ 0xCC33 et ≠ 0xAA55 »). C'est cohérent avec le modèle **set/reset
> mono-bit** atteignable par voltage glitch ([`00`](00_SYNTHESE_CORPUS.md) §3.2). **Descendre en L0
> exigerait d'écrire exactement `0xAA55` → jugé non faisable par glitch** [corpus, p. 209].
>
> ★ **Généralisation : compter l'espace des valeurs avant de choisir la cible du glitch**
> [corpus, Gerlinsky, deck RECON BRX 2017, sl. 6]. Sur le **LPC1343**, **4 mots de 32 bits activent**
> la protection contre **4 294 967 292 qui la désactivent** : *n'importe quelle* corruption de ce mot
> ouvre la puce. C'est l'**anti-pattern A6 « default to unprotected »** de *Fill your Boots*
> [corpus, p. 19], et c'est **la configuration la plus favorable à l'attaquant**.
> ⚠️ **La RDP STM32 est bâtie dans l'autre sens** — Level 1 = « toute valeur **sauf** `0xAA` » —
> donc **elle ne présente pas cette faiblesse** au niveau L0. **Mais le downgrade L2 → L1 rejoue
> exactement la même asymétrie** (« toute valeur sauf `0xCC` »), ce qui explique qu'il soit la
> séquence la plus reproductible du corpus. ★ **Et chip.fail montre la version extrême du problème**
> sur **STM32F2** : la bootROM désassemblée ne teste **que** `0xAA` (§3.3) — il suffit alors de faire
> apparaître `0xAA`, ce qui ramène le cas STM32 au cas LPC.

### 2.2 Où injecter selon la famille (agnostique)

| Famille | Rail à attaquer | Point d'injection logique | Trigger |
|---|---|---|---|
| **F1 (F103)** | **VDD** | phase de vérification RDP après `Read Memory`, avant ACK/NACK | activité I/O UART (bootloader) |
| **F3 (F373)** | broche condensateur régulateur | chargement du RDP **au power-up** (~11 µs après boot) | **front sur NRST** (bootloader désactivé en L2) |
| **F2/F4/F7** | **VCAP1/VCAP2** (cœur 1,2–1,8 V) | selon scénario (bootloader ou power-up) | I/O ou NRST |
| **L4/G0/G4/U5** | **à vérifier datasheet** (LDO/SMPS, TZEN) | **non documenté dans le corpus** | à caractériser |

> ⚠️ Le mapping « broche condensateur → VCAP » est une **inférence à valider sur le datasheet de la
> cible** ; Bozzato ne prononce jamais « VCAP ».
>
> ★ **Nouveauté sur la ligne F2/F4/F7** : le corpus contient désormais un **cas de voltage FI réussi
> sur un STM32F4** — le **STM32F415RG** de *Controlling PC on ARM* (deck FDTC 2016, sl. 52), dont la
> carte expose bien **VCAP1 (br. 31) et VCAP2 (br. 47)**. ⚠️ **Mais le deck ne dit jamais quel rail a
> été glitché** (la ligne est simplement étiquetée `vcc`) : cela **confirme qu'un F4 est attaquable en
> voltage**, cela **ne valide pas** l'inférence VCAP. Les familles modernes (protections RDP/TZEN
> renforcées) **ne sont pas couvertes par le corpus** : les traiter en terrain inconnu.
>
> ★★ **L'inférence VCAP est désormais confirmée — par une source `[ref]`, pas `[corpus]`.**
> Le write-up **Anvil Secure, *Glitching STM32 Read Out Protection*** (`[ref]`,
> `docs_pdf/writeups/STMicro_STM32F401CC_anvilsecure_…pdf`, §9.3 ci-dessous) décrit **explicitement**
> le point d'injection sur un **STM32F401CC** : *« **VCAP_1 Pin: a cable was soldered to the VCAP_1
> pin to facilitate VFI. Relevant bypassing capacitors were desoldered** »*, en justifiant que
> **VCAP_1 et VCAP_2 sont directement connectés au cœur**. C'est **le premier document du projet à
> nommer le rail**, et il valide la ligne F2/F4/F7 du tableau.
> ⚠️ **Statut à respecter** : write-up de praticien converti en PDF → **`[ref]`, cité par URL, jamais
> par page** ; il **confirme une pratique**, il ne remplace pas la vérification du datasheet de
> **votre** référence exacte (le brochage VCAP varie selon le boîtier).

---

## 3. Les séquences documentées (à reproduire en premier)

### 3.1 STM32F103 — bypass RDP sur `Read Memory` [corpus, §1.6]

1. Entrer en **bootloader série** (BOOT0=1).
2. Envoyer la commande **`Read Memory`** sur un bloc (max **256 octets**).
3. **Trigger** sur l'activité UART ; balayer le **délai** (résolution ≤ 10 ns) pour couvrir la phase
   de vérification RDP entre la commande et la réponse.
4. **Injecter le glitch.** Si **ACK** au lieu de NACK → le bloc est renvoyé en clair.
5. Itérer bloc par bloc.

**Résultats de référence** : **128 kB en < 1 min**, **~9 000 glitchs**, **~5 %** de succès,
recherche de paramètres **20 min**, répétabilité **haute**. Le F103 est *« quite sensitive to
voltage glitches »* [corpus, p. 210].
**Tension nominale / profondeur / largeur : non données par le papier → à caractériser.**

> ★ **Réglage accéléré par optimisation d'hyperparamètres** [corpus, Werner, thèse VERIMAG 2022,
> p. 117-119] : **cette exacte attaque** (bypass RDP du **STM32F103RB** par `Read Memory`) a été
> rejouée en réglant la **forme du glitch par optimisation bayésienne (SMAC)** au lieu d'un algorithme
> génétique. SMAC atteint **0,79** de probabilité de faute contre **0,37** pour un GA à **6 000
> injections**, et contourne la RDP *« deux fois plus vite qu'avec un GA »* (qui n'y parvient qu'à
> 12 000). ⇒ **quiconque construit ce glitcher peut régler la forme avec SMAC** ; méthode, table
> comparative et garde-fous (pas de classement transitif avec Carpi) en §5 (stratégie 9) et
> [`00`](00_SYNTHESE_CORPUS.md) §5.

### 3.2 STM32F373 — downgrade RDP L2 → L1 au power-up [corpus, §1.6]

1. **Couper puis rétablir VCC** (relais reed / load switch).
2. **Surveiller NRST** pour détecter la sortie de POR — le Power-On Reset maintient le reset pendant
   **1,5 à 4,5 ms** ; la pull-up interne (~40 kΩ) ralentit le front (comparateur conseillé).
3. **Injecter le glitch à ~11 µs** après le début effectif du boot (chargement du RDP).
4. Vérifier l'accès **JTAG/SWD** et le bootloader.

**Résultats** : **~25 glitchs**, **~4 %**, recherche **2 h**, répétabilité **modérée**.
**Un dump flash complet n'a PAS été obtenu par FI seule** : la ligne correspond à **un
déclenchement** du downgrade.
**Exploitation post-downgrade** : en L1, le debugger lit **RAM + registres** (pas le flash) → soit
attacher le debugger pendant une routine sensible, soit exploiter un **auto-test CRC-32 au boot**
(ARM App Note 277) pour dumper RAM/registres pendant le calcul — **un downgrade réussi requis par
octet extrait** [corpus, p. 209].

### 3.3 STM32F2 — downgrade RDP2 → RDP1 au power-up [corpus, chip.fail, deck 2019]

**Deuxième séquence de downgrade du corpus**, indépendante de Bozzato et sur une autre famille.
Elle est **plus instructive que le F373** parce que les auteurs **expliquent pourquoi elle marche**.

1. ★ **Le fondement, obtenu par reverse et non par essai** : la **bootROM du STM32F2 est lisible en
   RDP0**. Désassemblée, elle révèle que *« **no check found, all checks only for RDP0 (0xAA)** »*
   (sl. 129-130) — **il n'existe aucun test de la valeur RDP2 `0xCC`**. La protection se réduit donc
   à un test d'égalité à `0xAA` : **faire retourner `0xAA` à une seule lecture suffit**.
2. **Power-cycle**, puis glitch pendant la **lecture de l'octet RDP depuis la NVM interne** par la
   bootROM (sl. 135-136) — **même fenêtre que le F373**.
3. **Repérer la fenêtre par analyse de consommation** plutôt qu'à l'aveugle (sl. 137-144) : le boot
   dure **1,8 ms**, et sur les **200 µs** qui suivent le reset on distingue nettement
   *BootROM Execution* → **lectures Flash / Option Bytes** → *Application Execution*.
4. **Résultat** : **RDP2 → RDP1**, ce qui donne **accès à la SRAM** — où les secrets ont été copiés
   (sl. 151). C'est exactement le modèle d'exploitation post-downgrade du §3.2.

**Paramètres publiés** (sl. 149, libérés après correctifs du fabricant) : `Delay ≈ 17900`,
`Pulse = 50`. ⚠️ **Unités non imprimées** : ce sont des **compteurs du glitcher FPGA** (cadencé à
100 MHz), **pas des nanosecondes** — les citer tels quels, ne pas les convertir.
⚠️ **Organe de glitch : un MUX analogique MAX4619, pas un crowbar** (sl. 65-66) — la transposition à
la carte du projet demande de refaire la caractérisation (voir [`05`](05_SCHEMAS_ELECTRONIQUES.md) §4.2).

### 3.4 STM32F401CC — bypass RDP1 sur `Read Memory` `[ref]`

> ⚠️ **Statut `[ref]`** : write-up de praticien (Anvil Secure), converti en PDF dans
> `docs_pdf/writeups/` — **cité par URL, jamais par page**. C'est la **troisième attaque voltage-FI
> sur STM32 documentée** dont dispose le projet, et la **plus proche du F103 de Bozzato**.

Même logique que le §3.1, mais avec **tous les paramètres de timing publiés** :

1. **Bootloader série**, commande **`Read Memory` (0x11)**.
2. ★ **Point d'injection : `VCAP_1`** (câble soudé, condensateurs de découplage dessoudés) — cf. §2.2.
3. **Trigger** sur `USART_TX` du convertisseur USB-UART (entrée TIO4 du **ChipWhisperer-Lite
   CW1173**) ; `RESET` sur TIO3.
4. ★ **Déterminer l'offset à l'analyseur logique, pas par balayage aveugle** : émission de la commande
   mesurée à **182,300 µs**, réponse à **196,800 µs**. À **10 ns** par cycle, le plancher de
   `ext_offset` vaut donc **18 230 cycles**.
5. **Fenêtre utile trouvée : `ext_offset` entre 18 300 et 18 370 cycles**, soit ≈ **183,0–183,7 µs**
   après le trigger — une fenêtre d'environ **700 ns**.
6. **Résultat** : ACK au lieu de NACK → firmware dumpé bloc par bloc, secret extrait ; script publié.

> ★ **Ce qu'il faut en retenir pour la carte RP2350** : la **mesure préalable du protocole** (deux
> horodatages à l'analyseur logique) remplace des heures de balayage. C'est la version « bootloader
> série » du profilage préalable de *Fill your Boots* (§5, étape 6).

---

## 4. Le régime clock-glitch (conditionnel, en complément)

Le clock glitch sur STM32 **n'est exploitable que si la PLL est sourcée sur HSE** (*Peak Clock*,
**[corpus]**). Si applicable (cristal / OSC_IN accessible) :

- Méthode : **burst haute fréquence sur l'entrée d'horloge** pour forcer la PLL à se sur-cadencer
  (pas une impulsion courte).
- STM32F0308R : nominal **48 MHz** (PLL ×12 depuis 4 MHz externe) ; burst de **~100 µs** amène le
  cœur à ~110 MHz ; **fenêtre de succès ~119–134 µs** (flanc de discrimination de **2 µs**),
  **crash > 138 µs** [corpus, p. 89].
- **Instruction shadowing** : le burst couvrant des dizaines d'instructions, ce sont les
  **branchements** (`beq`) qui échouent en premier [corpus, p. 91].

**Second régime documenté — glitch de période, sur MCU à horloge externe** [corpus, Korak & Höfler,
deck FDTC 2014, **ajouté**]. Là où *Peak Clock* sur-cadence une PLL par un **burst soutenu**, ce deck
insère **une période raccourcie** `TGlitch` dans l'horloge (`T | TGlitch | T−TGlitch`, sl. 17) sur deux
MCU cadencés **par l'attaquant** :

- Horloge de travail **24 MHz** ; `TGlitch` balayé **5–18 ns** ; fautes reproductibles sur
  **[6,0 ; 20,0] ns** (sl. 17, 28). Alimentation **3,3 V**.
- ★ **L'underpowering élargit la fenêtre de glitch** (sl. 29, Cortex-M0) : en abaissant `UGlitch` de
  **1,5 V à 1,0 V**, la plage de `TGlitch` produisant une faute passe de quelques **dixièmes de ns** à
  **~3 ns** (fetch) et **~7,7 ns** (execute) *(valeurs **lues sur le graphe**, non imprimées)*.
  → **appui empirique direct à l'étape 0 ci-dessus**, sur MCU réel. ⚠️ Mais l'axe élargi est la fenêtre
  du **glitch d'horloge**, pas la largeur d'un glitch de tension : c'est un **analogue du mécanisme**,
  pas un transfert de chiffres.
- **Effets par étage de pipeline** (skip au fetch, corruption à l'execute, decode intact ; branchement
  en execute = *« no effects »*) → voir [`00`](00_SYNTHESE_CORPUS.md) §3.5 : ces résultats-là décrivent
  un **pipeline**, donc se transposent au voltage glitch.
- **Squelette de firmware de test réutilisable** (sl. 19) : `handshake "ready" → arm → trigger →
  instruction cible entourée de `nop` → renvoi du résultat` — à rapprocher du *nop-slide* de
  *Peak Clock* (§7).
- ⚠️ **Aucun taux de succès n'est publié** dans ce deck, et **le vecteur n'est pas le voltage** :
  l'underpowering y est un sensibilisateur, jamais un vecteur autonome.

Si le firmware boote en **HSI**, **abandonner le clock glitch** → voltage glitch uniquement.
C'est le cas des deux MCU de Korak & Höfler *à l'envers* : leur Fault Board fournit l'horloge **et**
l'alimentation (sl. 13), ce qui rend leur régime inapplicable tel quel à un STM32 autonome.

---

## 5. Recherche des paramètres — procédure recommandée

**Étape 0 — élargir la fenêtre avant de chercher (reco n°1) :**

- **Sous-alimenter** : abaisser VDD sous le nominal. TCHES'24 [corpus, p. 173] : **1,0 → 0,93 V**
  fait passer le taux de faux-négatifs de ~50 % à ~100 %. Mécanisme : `t_pLH ∝ 1/(V_DD − V_th)²`.
- **Chauffer** (35 → 85–100 °C) : même effet sur les délais (Ghalaty, Martín [corpus]).
  ★ **Désormais sourcé en direct** [corpus, Ege/Korak/Hutter/Batina, deck FDTC 2014, **ajouté**] :
  entre **25 °C et 100 °C**, le seuil de faute **se déplace de ≈ +2,2 ns** (plage +1,4 à +2,9 ns,
  même sens dans 35 mesures sur 36) — et ce décalage est **identique en ns absolues à 10 et 20 MHz**,
  signature d'un **allongement du délai de propagation** et non d'un effet lié à la période. C'est
  précisément ce qui le rend transposable au voltage glitching. *(Valeurs **lues sur graphe**, non
  imprimées.)*
  ⚠️ **Trois réserves à respecter** : ① l'énoncé imprimé du deck est *« **SOME** types of faults are
  easier to induce »* — la fenêtre **s'élargit pour certaines catégories de faute et se rétrécit pour
  d'autres** ; ce qui est fiable est le **déplacement** du seuil, pas son élargissement ; ② **aucun
  taux de succès** n'est publié, et deux points de température ne permettent **aucun coefficient en
  %/°C** ; ③ le deck **ne teste pas la tension** — le couplage *chauffage × underpowering* n'est
  mesuré nulle part, les deux moitiés de l'étape 0 restent sourcées séparément.
  → **Conséquence de banc** : après tout changement de température, **re-caractériser l'offset**
  plutôt que le compenser au premier ordre (cf. §7).

**Étapes 1→3 — recherche proprement dite :**

1. **Balayage monotone du délai** — Skorobogatov [corpus, sl. 42] : *« augmenter lentement le délai
   jusqu'à observer l'effet »*. Pas de balayage **25 ns** [corpus].
2. **Récursion en précision** — DSN'21 [corpus, p. 405] : partir d'un glitch large, affiner d'un
   facteur `1/(10·profondeur)` jusqu'à 100 % de succès (convergence **16–59 min**).
3. **Algorithme génétique sur la forme (Palier 2)** — Bozzato [corpus, pp. 206–207] : 50 tests/candidat
   au départ, crossover uniforme `p=0,5`, **mutation la plus forte sur la durée**, replace-worst,
   convergence **30 min–10 h**. Partir d'un **petit ensemble de formes prédéfinies** (compromis
   perf/durée, [corpus, p. 218]).
4. ★ **Dichotomie 2D « adaptive zoom & bound » — la stratégie à essayer en premier**
   [corpus, Carpi *et al.*, CARDIS 2013]. C'est la mieux classée des quatre comparées par les auteurs,
   *« it completes the first stage of the search with the least number of measurements, and it has the
   best ratio of SUCCESSFUL measurements »* (p. 14) :

   | Stratégie | Mesures, 1ʳᵉ étape | Taux de succès |
   |---|---|---|
   | Monte Carlo (aléatoire) | — | **0 %** (0 succès / 3072 ; il en faut **76 800 pour 11 succès**, p. 8) |
   | FastBoxing | 2048 | 0,295 % |
   | Algorithme génétique | 1560 | 0,313 % |
   | ★ **Adaptive zoom & bound** | **192** | **1,175 %** |

   **Plancher théorique** de la 1ʳᵉ étape, formule réutilisable telle quelle (p. 10) :
   `N = n · ⌈max(log₂(rangeV/resolutionV), log₂(rangeL/resolutionL))⌉` → **112 mesures** pour
   [−5 ; −0,05] V × [2 ; 150] ns aux résolutions 0,05 V / 2 ns.

   **Le modèle de recherche** (p. 5-6) : deux phases — **la forme d'abord** (tension, longueur),
   **l'instant ensuite** — et l'on vise la **frontière de décision** entre la région NORMAL et la
   région RESET/MUTE, matérialisée par deux verdicts : **INTERESTING** (proche de la frontière) et
   **CHANGING** (deux mesures identiques → verdicts différents). ★ **C'est en ciblant la zone CHANGING
   et en répétant 3× chaque mesure** (pour absorber le jitter d'horloge interne) que les auteurs
   cassent une carte **certifiée Common Criteria EAL4+** annoncée protégée contre le VCC FI (p. 11-12).
   ★ **Règle de portabilité** (p. 11) : les paramètres de **forme** sont **les mêmes d'un exemplaire à
   l'autre** du même composant — **les paramètres temporels, non**. C'est ce qui décide de ce qu'il
   faut recalibrer en changeant de puce.
   ⚠️ **Citer les pourcentages de Carpi avec leur définition** : Tables 2/3 = **médianes par test**,
   Tables 5/6 = **meilleur run observé** — deux définitions pour les mêmes cellules.

6. ★ **Profiler chaque glitch séparément AVANT de les combiner — *grey-box glitching***
   [corpus, *Fill your Boots*, p. 10]. Sur un bootloader qui ne renvoie **rien** tant que la
   protection tient, la recherche à l'aveugle **explose combinatoirement** (p. 14). La parade des
   auteurs : **flasher les sections critiques du bootloader comme application utilisateur** pour les
   instrumenter. **Transposition STM32** : la bootROM n'est pas reflashable, mais elle est
   **désassemblable** (chip.fail l'a fait sur F2, §3.3) et la routine équivalente peut être
   **rejouée en flash utilisateur** pour caractériser la fenêtre.
7. **Prédire l'offset plutôt que le balayer** (même papier, §5) : exécution symbolique du bootloader
   pour compter les cycles jusqu'à la section visée. ⚠️ **Ne pas en attendre un meilleur taux** —
   Table 4 p. 18 : Bozzato (AGW + génétique) reste devant (**4,2 % / 6,8 %** contre **3,2 % / 4,3 %**).
   L'apport est de **supprimer la recherche d'offset**. Version « bootloader série », bien plus
   simple et directement applicable : **mesurer le protocole à l'analyseur logique** (§3.4).
8. ★ **Descendre depuis la région de CRASH plutôt que monter depuis le silence** `[fait]`.
   Les stratégies 1 à 4 partent toutes du bas — « augmenter lentement jusqu'à observer l'effet ».
   Une campagne EMFI réelle sur bootloader LPC1114 a fait l'**inverse**, et c'est plus économique :

   | Étape | Réglage | Observation |
   |---|---|---|
   | 1. **Ancrer sur le crash** | intensité **maximale**, offset balayé largement | trouver un point à **100 % de crashs** |
   | 2. **Descendre jusqu'à les faire cesser** | pas grossier (5 % de la plage) | noter le point à **0 % de crash** |
   | 3. **Remonter finement** | pas fin (1 % de la plage) | ★ le **succès est juste au-dessus** de ce point |

   Mesuré : 100 % de crashs à intensité haute · **0 %** au point bas · et au **premier pas
   au-dessus** : **50 % de crashs et 10 % de succès**, les deux pas précédents ne donnant rien.
   ⇒ **le succès vit au BORD de la région de crash**, et on l'atteint par le haut.

   ★ **Pourquoi c'est plus efficace** : c'est la même **frontière de décision** que la zone
   `CHANGING` de Carpi (stratégie 4), mais **la région de crash est large et bruyante, donc facile
   à trouver**, là où la région de succès est étroite. Partir du crash offre un **point d'ancrage
   gratuit** ; partir du silence oblige à balayer à l'aveugle jusqu'à tomber dessus.
   ⚠ **Deux réserves** : on **traverse une zone à 100 % de crashs** — à réserver aux cibles qu'on
   accepte de redémarrer sans cesse, et à éviter si le découplage transforme les crashs en
   brownouts prolongés ; et la mesure citée porte sur **n = 10**, ce n'est pas un taux établi.
   Détail et paramètres : [`06`](06_EMI_INJECTOR_EMFI.md) §1.8.

9. ★ **Optimisation d'hyperparamètres — bandit (SHA) + optimisation bayésienne (SMAC)**
   [corpus, Werner, thèse VERIMAG 2022]. **Décomposer en deux étapes** : (1) optimiser la **forme du
   glitch sur un test de caractérisation** (indépendant de l'application, délai ignoré) avec **SMAC**
   ou **SHA**, puis (2) balayer le **délai** sur la cible par RS/GS. **SMAC (bayésien) domine
   un algorithme génétique (GA — famille de recherche de Bozzato, stratégie 3) et la recherche aléatoire** en < 10 000 injections
   (Cortex-M4 : 0,95 vs GA 0,81 vs RS 0,71), et contourne la RDP du **STM32F103RB 2× plus vite qu'un
   GA** (§3.1). ⚠️ Tête-à-tête **vs GA/RS seulement — pas vs Carpi** (stratégie 4), dont Werner ne se
   distingue que sur la **méthode** (test de caractérisation vs optimisation directe sur
   l'application) ; grandeurs non commensurables. Table complète : [`00`](00_SYNTHESE_CORPUS.md) §5.

> ★★ **Garde-fou multi-glitch — à lire avant de budgéter une campagne à deux impulsions.**
> [corpus, *Fill your Boots*, p. 13] mesure sur STM8L deux glitchs individuels à **0,6 %** et
> **0,1 %**, dont la combinaison devrait donner **≈ 0,0036 %**. Le taux réellement obtenu est
> **0,0001 %** — **36 fois moins**. Cause imprimée : le **pipeline 3 étages**. Après le premier
> glitch, le flot d'exécution n'est plus le même, donc **le contenu du pipeline au moment du second
> glitch diffère de celui du profilage**. **Ne jamais multiplier les taux individuels pour estimer un
> multi-glitch** : recaractériser dans la séquence complète. ⚠️ Un STM32 étant lui aussi un Cortex-M à
> **3 étages**, tabler sur le même type d'écart.
>
> Ordres de grandeur associés, utiles au dimensionnement : glitchs devant tomber à **± 20 ns** de
> l'offset ; **100 000 tentatives ≈ 2,5 min** reset compris ; temps de reset **≈ 78 µs** (STM8A)
> contre **≈ 26 µs** (STM8L), le jitter de l'oscillateur interne étalant les offsets sur **≈ 6 µs**
> [corpus, p. 13].

**Règles de balayage :**

- **Fixer les données traitées** pendant la caractérisation (délais dépendants des données, Ghalaty
  §3.2.4 [corpus]).
- **Monter l'intensité par pas fins depuis le point de non-effet** ; la zone utile est **étroite** et
  juste après le seuil de première faute — au-delà, le comportement **sature** (bit-flip → 0,5,
  ~4 bits/8) et n'apporte plus rien [corpus, Ghalaty p. 128].
- **Commencer par les fautes faiblement biaisées** (1 bit → 7 valeurs candidates ; 2 bits → 55) ;
  séquence 1-bit → 2-bit → 3-bit [corpus, Ghalaty p. 43].
- **Stratégie différentielle multi-intensité** plutôt qu'à seuil unique : plus robuste au **jitter de
  trigger** du RP2350 [corpus, Ghalaty Table 5.1].
- ★ **Mesurer la période de ringing du PDN de la carte AVANT de balayer la largeur**
  [corpus, Zussa HOST 2014]. La faute ne naît pas sur le plateau de l'impulsion commandée mais au
  ***tip* d'une oscillation négative** (p. 7) — et l'amplitude commandée n'est pas celle vue par le
  silicium (**−14 V → ~400 mV au die**, p. 6). Trois régimes se déduisent de la période de ringing,
  et ce sont eux qui donnent le contrôle réel :

  | Effet | Largeur d'impulsion | Bénéfice mesuré |
  |---|---|---|
  | **Addition** | = **demi-période** du ringing | même creux au die pour **8 V au lieu de 14 V** → moins de stress, donc moins de resets |
  | **Sharping** | ≪ période (10 ns) | tip **rétréci à ~10 ns** (au prix de 22 V) — **c'est le vrai levier de finesse**, fixé par la carte et non par le tick du contrôleur |
  | **Offsetting** | = **période complète** | annule la seconde oscillation négative → **évite d'injecter une faute parasite**, utile pour un scoring propre (1 injection = 1 tentative) |

  ⚠️ **Réordonnancement à noter** : Zussa mesure que *« the **pulse width value had no significant
  effect** on the induced voltage perturbations. The main parameters… were the **pulse amplitude and
  DC component values** »* (p. 7). La largeur ne redevient décisive **que par le recouvrement**
  ci-dessus. Balayer donc **amplitude + composante DC d'abord**, largeur ensuite et **relativement à
  la période de ringing**. Cohérent avec *False Injections* (§9.1) et avec « résolution de commande
  ≠ largeur de glitch » ([`00`](00_SYNTHESE_CORPUS.md) §4).
- ★ **Balayer profondeur et largeur ENSEMBLE, le long de la diagonale** [corpus, *Controlling PC on
  ARM*, sl. 61/63/65] : la zone de succès mesurée sur STM32F415RG est une **crête diagonale** (plus la
  tension est négative, plus le glitch peut être court), pas un point — balayer un axe puis l'autre
  la manque.
- ★ **Cartographier le seuil plutôt que balayer en aveugle** [corpus, Zussa p. 7, Fig. 8] : à chaque
  pas de temps, **faire descendre la composante DC depuis une valeur sûre jusqu'à la première faute**.
  On obtient une carte de **seuil de sensibilité par instant**, bien plus informative qu'un balayage
  uniforme.

---

## 6. Contourner les détecteurs (si la cible en a)

Aucun détecteur n'est prouvé présent dans un STM32 par le corpus, mais si l'on en soupçonne un :

- **Cartographier le seuil d'alarme AVANT de chercher la faute** : dans TCHES'24 la région
  intermédiaire est purement *faux-positive* (bruit détecté sans gain). Viser la **fenêtre aveugle**
  `[t_attack, t_safe]` (Leniency Factor) [corpus].
- **Exploiter la latence des capteurs analogiques VDD** : un glitch plus court que le temps de
  réponse du comparateur passe ; ces capteurs ne voient souvent que les glitchs **positifs**
  [corpus, Deshpande p. 16].
- **Sous-alimenter** relâche simultanément la contrainte de bande passante **et** dilue les seuils de
  détecteur (les zones « s'étirent dans le temps », TCHES'24 [corpus, p. 173]).
- **Caractériser l'exemplaire, pas la datasheet** : ±20 % de dispersion process sur les seuils, die
  vieilli = cible plus facile [corpus, Deshpande p. 31].

> **Vecteur alternatif si détecteur global** : l'**EMFI** est *local* et **échappe aux détecteurs de
> glitch globaux** (DATE'14) là où le voltage glitch est vu. Voir le module dédié
> [`06_EMI_INJECTOR_EMFI.md`](06_EMI_INJECTOR_EMFI.md) (ajoute un balayage spatial à cette méthodo).

---

## 7. Instrumentation et reproductibilité du banc

- **Mesurer Δ** (temps min entre 2 injections) de la chaîne complète RP2350 → cible, câble compris —
  c'est la **borne dure** du multi-glitch (recharge du condensateur) [corpus, DSN'21 p. 405 ; Martín
  Déf. 2]. Découplage cible **minimal** (breakout sans condensateurs) [corpus, p. 203].
- **Power-cycle propre** entre tentatives (load switch) ; respecter le **POR 1,5–4,5 ms** avant
  re-trigger [corpus].
- **Compensation thermique ~0,1 %/°C** et log de température à chaque essai [corpus, Bozzato p. 215] ;
  attention aux campagnes multi-jours (ex. chauffage coupé la nuit).
  ⚠️ **La compensation au premier ordre ne suffit pas pour un grand écart de température.**
  [corpus, Ege *et al.*, FDTC 2014] mesure un **déplacement du seuil de ≈ +2,2 ns pour ΔT = 75 °C**
  (25 → 100 °C), et surtout un déplacement **qui n'est pas uniforme selon le type de faute visé** :
  certaines catégories voient leur fenêtre s'élargir, d'autres se rétrécir. → au-delà de quelques
  degrés, **re-caractériser l'offset** plutôt que l'extrapoler (cf. §5, étape 0).
  ⚠️ **Ne pas mélanger les deux grandeurs** : les **0,1 %/°C** de Bozzato compensent un *délai relatif*,
  tandis que le **≈ 0,03 ns/°C** dérivé d'Ege est une *estimation deux points lue sur graphe* portant
  sur un paramètre de glitch d'horloge. Elles ne sont ni interchangeables, ni cumulables.
- **Répéter chaque point ~100 fois** (les effets sont subtils, la répétabilité est elle-même une
  donnée) [corpus, TCHES'24].
- **nop-slide (~160 instructions)** avant le code d'analyse du firmware de test [corpus, Peak Clock
  p. 89] ; mesurer f_CPU via un timer togglant une GPIO à f_CPU/4 pour caractériser la cible avant
  l'attaque [corpus, p. 89].

---

## 8. Checklist opératoire (résumé)

- [ ] Cible dessoudée/isolée, breakout **sans découplage**, sonde < 10 mm de la broche d'alim.
- [ ] Sortie de glitch câblée sur le **bon rail** (VDD ou VCAP selon famille — **vérifier datasheet**).
- [ ] **Load switch** opérationnel (power-cycle) + surveillance **NRST** (POR).
- [ ] Alim programmable réglée pour **underpowering**, sonde de température en place.
- [ ] Scoring **5 catégories** instrumenté, **Δ mesuré**.
- [ ] Balayage **délai → largeur → offset** à pas fin (pas la répétition).
- [ ] Séquence de référence choisie (**F103 Read Memory** ou **F373 downgrade**) et reproduite.
- [ ] Étalon commercial (PicoGlitcher / CW-Nano) disponible pour comparaison.

---

## 9. Exploitation sur cibles réelles & desserrage des contraintes de timing (Raelize/Riscure)

> **[corpus]**, cités par slide/page. Ces exposés élargissent la méthodo **au-delà du STM32**
> (ARM/Linux, secure boot, automobile, SoC applicatifs). **Vecteur = voltage** sauf mention EMFI ;
> plusieurs decks (No Hat 2022, Data Transfers) sont **agnostiques du vecteur** (modèle/méthodo).

### 9.1 Desserrer les contraintes de timing (le plus transférable au RP2350)

- **Changer de modèle de faute** : viser la **corruption d'instruction** (> skip) sur les
  **transferts de données** (`memcpy`, `ldm/stm`, UART/USB/Flash→RAM) — une instruction de transfert
  corrompue charge une donnée attaquant dans le **PC** (No Hat 2022 sl. 29-42 ; Data Transfers PoC'19
  sl. 24-56).
- ★ **La formalisation d'origine est maintenant au corpus, et elle est plus précise que ses reprises**
  [corpus, *Controlling PC on ARM*, deck FDTC 2016, `2016_FDTC_Controlling-PC-on-ARM-…_TSW.pdf`] :
  - **Vecteur voltage, cible STM32F415RG** (sl. 52, 57, 78-84) — c'est la **deuxième** attaque
    voltage-FI sur STM32 du corpus après Bozzato.
  - **Les instructions visées à l'origine sont `LDR` et `LDMIA`** (boucles de copie), pas
    `ret`/`blr` — ce cadrage-là vient du deck PoC 2019, postérieur. Critère de choix imprimé
    (sl. 21-24) : données **contrôlées par l'attaquant**, exécutées **en série**, **non protégées**.
  - ★ **`LDMIA` ≫ `LDR`, et la raison est arithmétique** : passer `LDR r3` à `LDR PC` demande de
    mettre **2 bits** à 1 ; passer `LDMIA {r3-r10}` à `{r3-r10, PC}` n'en demande **qu'un**. Résultat
    observé à banc identique sur les campagnes « 10k » : **~1 succès** pour `LDR`, **~26** pour
    `LDMIA` (sl. 63, 65) — ⚠️ **comptés sur le nuage de points, non imprimés** (à lire comme un ordre
    de grandeur). La phrase imprimée est *« The instruction encoding matters »* (sl. 78-84).
    → **choisir l'instruction cible par sa distance de Hamming avant d'améliorer le glitcher.**
  - **Le *pointer sled* est déjà là** (sl. 35-41) : un tapis de pointeurs en flash, la faute étant
    injectée **pendant la copie Flash → DDR**.
  - ⚠️ **Ne pas surcoller les encodages** : les opcodes imprimés sont en **ARM/A32** alors que la
    carte est un **Cortex-M4 (Thumb-2)** — le deck ne réconcilie jamais les deux. Le concept se
    transpose, **les motifs binaires imprimés non**. Et **le deck ne dit pas quel rail** a été
    glitché (ligne étiquetée `vcc`) : **ne pas conclure VCAP**.
  - **Contre-mesures** (sl. 66-77) : *deflect* (délais aléatoires) / *detect* (double check) /
    *react* (reset), plus des mitigations d'exploitation (n'exécuter depuis la mémoire que quand
    nécessaire, **randomiser l'adresse de destination des copies**). Verdict imprimé : *« **You can
    lower the probability but you cannot rule it out!** »*
- **Pointer sled** : charger un tapis de pointeurs vers le shellcode et glitcher pendant **n'importe
  quel** transfert → faible localité, **précision de glitch non requise** (No Hat 2022 sl. 42-52).
- **Longueur de transfert contrôlée** → fenêtre élargie à volonté ; **transferts multiples** →
  **attaques quasi-triggerless** (No Hat 2022 sl. 49-52).
- ⚠ **Le glitch n'a pas besoin d'être « sharp » / sous-cycle** : *False Injections* (Dartmouth 2025,
  **ESP32/Xtensa, voltage**) obtient des succès avec des largeurs de **721 et 3944 ns** (58× et 316× le
  cycle de 12,5 ns à 80 MHz ; balayage 200–5000 ns, sl. 30/32), et des glitchs **peu profonds + longs**
  passent les détecteurs → confirme « résolution de commande ≠ largeur »
  ([`00`](00_SYNTHESE_CORPUS.md) §4) et **renforce la reco n°1** (sous-alimenter + fenêtre élargie).

### 9.2 Cas réels documentés & budgets d'essais

- **Privesc Linux → root** (FDTC 2017, **voltage**) : glitch du check noyau de `setresuid(0,0,0)` →
  shell root ; **~1,3 %** @ fenêtre **3,14–3,44 µs**, root /5 min (sl. 21-23). Scoring 3 réponses
  *Expected / Mute-Reset / Success* directement réutilisable.
- **Root d'un SoC via EMFI** (Google TV Streamer, hwio NL 2025, **EMFI**) : voir
  [`06`](06_EMI_INJECTOR_EMFI.md) §1.1 — attaque **runtime sans trigger**, SELinux **non** contourné.
- **Bypass secure boot** (BHEU 2018, **voltage** VCC 1,2→0,9 V) : viser l'étape **authenticate/jump** ;
  le simulateur open-source **FiSim** (Unicorn + Capstone) pré-identifie les instructions glitchables
  du binaire de boot ; les contre-mesures **SW** sont contournées par la corruption (sl. 88-94).
- **Extraction firmware** (escar 2018, **voltage**) : retirer les **condensateurs de découplage** ;
  caractériser **à l'aveugle** via indicateurs comportementaux (réponse + consommation) ; cibler
  **UDS ReadMemoryByAddress** (éviter le timeout de `SecurityAccess`) ou **bypasser l'interface
  debug** (dump en heures) ; budgets : **~3 %**, **0x40 o/glitch réussi**, **~300 k glitchs / ~3 j**
  pour 512 kB (p. 3).
- **Protocoles de diagnostic automobile — UDS** (whitepaper escar 2018 ci-dessus, **[corpus]** ;
  complété par le talk hardwear.io 2018 de Cordoba, **[ref]**) : **SecurityAccess** (seed-key) protégé
  par un **timeout de 10 min après 3 échecs** — peu praticable en direct ; **ReadMemoryByAddress /
  WriteMemoryByAddress n'ont pas cette limite** et ne vérifient qu'un flag « authenticated » interne →
  **cible de choix pour le glitch** (whitepaper p. 3). Recherche de paramètres par
  **diviser-pour-régner** avec indicateurs comportementaux (whitepaper p. 2). Complément `[ref]` non
  recoupé indépendamment (talk 2018) : les mêmes auteurs rapportent avoir obtenu un **taux de succès
  EMFI comparable au voltage glitch** sur les mêmes cibles — piste à approfondir, pas une donnée EMFI
  chiffrée à ce stade. ⚠ **Divergence non résolue entre les deux sources** : le whitepaper documente le
  retrait des condensateurs de découplage (p. 2), le talk affirme à l'oral qu'aucune autre modification
  n'a été faite sur l'ECU (« réinstallable tel quel ») — à revérifier avant de trancher, ne pas résoudre
  par supposition.
- **Cas EMFI in-situ sur ECU automobile réel** (O'Flynn, ESCAR EU 2020, **EMFI**) : voir
  [`06`](06_EMI_INJECTOR_EMFI.md) §1.2 — bootloader BAM des MPC55xx/56xx, taux de succès effectif
  ~1,2–1,9 % (jusqu'à 36,3 % sur un environnement), dépendance à la polarité de sonde confirmée.

### 9.3 Write-ups de praticiens `[ref]` — `docs_pdf/writeups/`

> **Statut.** 27 write-ups web, convertis en PDF pour archivage et listés en
> [`04`](04_REFERENCES.md) §J. Ils sont **`[ref]` : cités par URL, jamais par page** (leur pagination
> est un artefact de notre conversion). Ils n'entrent pas dans le compte des 68 PDF du corpus.
> Ce qui suit est le sous-ensemble dont la méthode se transpose directement au projet.

- ★★ **Anvil Secure — *Glitching STM32 Read Out Protection*** (STM32F401CC, voltage) : détaillé en
  **§3.4**. Seul document du projet à **nommer le rail d'injection sur STM32 (`VCAP_1`)**, et à
  publier la **méthode de calcul de l'offset par mesure du protocole** plutôt que par balayage.
- ★ **Kraken Security Labs — *Critical Flaw in Trezor Hardware Wallets*** (STM32F205, voltage) :
  extraction du *seed* chiffré en **15 minutes d'accès physique**, puis cassage du PIN (1 à 9
  chiffres). Les auteurs estiment qu'un glitcher dédié à cette attaque pourrait se vendre **~75 $** —
  ordre de grandeur cohérent avec les **~92 $** du banc chip.fail `[corpus]`. **Contourne les
  mitigations posées par Trezor après wallet.fail** : utile comme repère de « durée de vie » d'un
  correctif logiciel face au FI.
- ★ **Riscure — *Glitching the KeepKey hardware wallet*** (STM32F205, ★ **EMFI**) : ⚠️ **vecteur
  relevé par extraction**. ★★ **Le critère de choix du vecteur est imprimé, et il est directement
  réutilisable** : *« Due to the fact that **USB is used for both communication and powering the
  device**, **EMFI was used** since it increases the chances of successful glitching »*. **Quand la
  cible est alimentée par le même lien que celui qui sert à communiquer, le rail n'est pas librement
  manipulable — l'EMFI devient le vecteur praticable.** C'est le pendant concret de l'argument
  « touchless » de [`06`](06_EMI_INJECTOR_EMFI.md) §1, et un critère à appliquer **avant** de choisir
  entre le Palier 1 (crowbar) et le module EM. La cible implémente par ailleurs une **détection de
  clock glitching** — que ce choix contourne d'office. Fautes observées : longueur de message
  corrompue, **compteur de boucle modifié**, octets mis à zéro, **un bit corrompu**.
  ★ **Chaîne d'exploitation élégante à retenir** : *skip* du test « device already initialized » →
  pose d'un **nouveau PIN en RAM** → `fsm_msgChangePin()` pour le committer — **le *seed* n'est jamais
  lu**, il est simplement **ré-autorisé**. Modèle « changer la serrure » plutôt que « lire le secret ».
- ★★ **LimitedResults — *nRF52 Debug Resurrection (APPROTECT Bypass)*, parties 1 et 2**
  (**nRF52840**, puis nRF52832 et nRF52833, voltage) : ★ **le cas qui généralise la notion de « rail
  cœur » hors du STM32**, et le seul du projet à viser une cible **sans bootROM**.
  ★★ **Ce qui se transpose, et c'est un changement de nature de la fenêtre** : le nRF52 n'ayant
  **aucune bootROM**, l'initialisation des ports de debug est *« achieved by **pure Hardware**… before
  the CPU start to load from Flash and execute Code »*. La fenêtre n'est donc **pas une routine de
  code** (comme la vérification RDP du F103 en §3.1, ou la bootROM du F2 en §3.3) mais un **transfert
  matériel** : celui de `UICR.APPROTECT` (`0x10001208`) par le contrôleur mémoire vers l'AHB-AP. Le
  corollaire méthodologique compte : **aucun désassemblage n'est possible**, la fenêtre se trouve
  **uniquement par analyse de consommation** (activité Flash au trigger, **CPU démarrant à 19 µs**,
  motif NVMC isolé en comparant deux rails).
  ★ **Point d'injection : `DEC1`**, la broche de découplage du cœur (*« definitively the CPU power
  line »*, 0,8–0,9 V) — l'homologue nRF du `VCAP_1` d'Anvil Secure. `DEC4` (alim système) sert de
  trigger. ★ **Nuance de découplage à retenir** : les condensateurs sont retirés, **puis un 100 nF est
  RE-SOUDÉ** sur le rail cœur *« to have more stability of the CPU power during boot-up »* — troisième
  position entre le « tout retirer » de Bozzato et l'« exploiter le ringing » d'O'Flynn
  (cf. [`05`](05_SCHEMAS_ELECTRONIQUES.md) §8).
  ★ **Économie de campagne identique à celle du BAT32G135** ([`07`](07_BAT32G135_FAULTYCAT.md)
  §9bis.3) : dump → `ERASEALL` → reflash avec l'octet de protection patché ⇒ **une seule faute réussie
  suffit à vie**. Glitcher maison **< 5 $**.
  ⚠️ **Aucun paramètre de glitch n'est publié** → tout est **à caractériser**. ⚠️ **Le nRF52820 n'a pas
  été testé** et **aucun CVE n'existe** — détail des coupures de provenance et URL :
  [`04`](04_REFERENCES.md) §J.
- ★ **Fork raiden-pico d'`iceman1001`** (branche `feat/unique-dump-paths` @ `90b547e`) — ⚠️ **`[ref]`,
  docs d'outil sur GitHub, cité par URL SHA-figée, PAS dans `docs_pdf/writeups/`** et **non compté dans
  les 68**. Documente, sur le **même moteur crowbar RP2350** que ce projet, **trois cibles** :
  - **nRF52840** (`TARGET GLITCH APPROTECT`, crowbar `DEC1`) : **second banc public** de l'attaque
    LimitedResults ci-dessus, avec un **point de fonctionnement** publié et cinq apports concrets
    (garde-fou `NVMC ERASEALL`, *cold-boot-only*, bouton d'amplitude `Rsrc`, oracle `FICR.PART`, bypass
    transitoire) — développé en [`08`](08_NRF52820_APPROTECT.md) §3bis. ⚠️ **3ᵉ raiden** (ni upstream
    AdamLaurie, ni fork local v0.14), et **nRF52840, pas 52820**.
  - **EFM32LG Leopard Gecko** (Silicon Labs, Cortex-M3) : debug-lock levé en fautant le **Debug Lock
    Word** pendant la fenêtre **`tRESET ≈ 163 µs`**, crowbar sur **`DECOUPLE`** (rail cœur ~1,8 V, LDO
    interne), `VDD` abaissé à **~2,0 V** pour un dip net ; recovery officielle = **AAP `DEVICEERASE`**
    (destructive, ne *lit* jamais). ⚠️ **Distinct du write-up LimitedResults EFM32** listé plus bas
    (deux sources, une même famille). ⚠️ iceman le signale lui-même (*caveats, à vérifier au banc*) :
    `DPIDR 0x2BA01477` est la valeur **SW-DP générique Cortex-M3/M4** (partagée STM32F1 / LPC17xx) —
    **exactement celle que le même fork lit sur sa cible nRF52** — donc elle **ne confirme aucune puce** ;
    l'identification positive est la lecture du mot *Device-Info PART*. Même piège d'oracle qu'au §1.1.
  - **PIC18** (Microchip, cible **neuve** pour le projet) : ni SWD ni UART → accès **ICSP**
    (PGC/PGD + MCLR/VPP), entrée **LVP** (clé `"MCHP"` ou broche PGM, **sans VPP 9–13 V**). ★ **Modèle
    de faute distinct** : la code-protect **gate la sortie du table-latch sur PGD** (une lecture
    protégée rend `0x00`, la donnée étant *fetchée* mais non sortie) → on faute **le clock-out de
    lecture**, pas le *fetch* ; crowbar sur **`VDD`** (pas de rail cœur exposé, comme le BAT32G135).
    Rendement single-shot **~0,24 %**, mais la gate est **ré-évaluée par octet** ⇒ une cellule
    (delay, width) se rejoue adresse par adresse pour un dump complet — même économie que les campagnes
    du projet. ⚠️ L'analogue **optique** (bunnie, *Hacking the PIC 18F1320*) est **écarté du corpus** en
    [`04`](04_REFERENCES.md) §F comme **non-FI** (UV/optique) : ce cas-ci est **voltage/ICSP**, vecteur
    différent — pas de contradiction. Détail :
    [`../knowledge_base/by-domain/microcontrollers-mcu.md`](../knowledge_base/by-domain/microcontrollers-mcu.md) §13.
- **jrainimo — *Dumping Firmware With a 555*** (STM8, voltage) : glitcher réduit à un **NE555**.
  Borne basse absolue du coût, à mettre en regard des ~92 $ de chip.fail et des ~50 $ du PicoGlitcher.
- **NCC Group — *Glitching the MediaTek BootROM*** (MT8163V, voltage) : trigger produit par un
  **FPGA** vers un ChipWhisperer ; cadence dictée par la cible — **~2 s** par tentative si l'image du
  *preloader* est valide, **~700 ms** si elle est corrompue. Rappel utile : **le débit de campagne est
  souvent fixé par le temps de boot de la cible, pas par le glitcher**.
- **toothless — *NXP LPC1343 Bootloader Bypass* (3 parties)** : pendant pratique du deck Gerlinsky
  `[corpus]` — dialogue bootloader, construction du glitcher, mise bout à bout.
- **icanhack (RH850/P1M-E)**, **jerinsunny (RH850/F1L)**, **fail0verflow (RL78, PS4 syscon)**,
  **collshade (RX65)**, **RECESSIM (SAM4C32)**, **0x01team (SAM E70/S70/V70/V71)**,
  **LimitedResults (EFM32 Gecko, M2351/TrustZone-M)**,
  **CyberIntel (MSM8916)**, **Zeus WPI (CC2510)** : neuf familles de MCU/SoC dont la **protection en
  lecture** tombe par voltage FI. Leur valeur ici est surtout **statistique** — ils montrent que le
  cas STM32 n'a rien d'une exception. ⚠️ **Ces neuf-là ne sont pas lus en détail** : leur vecteur
  est retenu du filtrage automatique (occurrences `glitch` / `fault injection`), pas d'une extraction
  ligne à ligne comme pour les write-ups développés ci-dessus. **Vérifier le vecteur à la source
  avant de citer l'un d'eux** — le cas KeepKey ci-dessus montre qu'un write-up « de glitching » peut
  être de l'EMFI. ★ **Le nRF52 est sorti de cette liste** : les deux write-ups LimitedResults ont
  depuis été lus intégralement et sont développés ci-dessus.
- **Espressif ESP32** : sept write-ups (Raelize ×4, LimitedResults ×3), dont ★ **un seul en EMFI**
  (*Bypassing Secure Boot using EMFI*) — exploité dans [`06`](06_EMI_INJECTOR_EMFI.md) §1.

> **Hors périmètre FI** : *QSEE Wifi Pro* (OffensiveCon 2026) et *Secrets of Simos18* (hardwear.io
> USA 2024, Ledbetter, `[ref]`) sont de l'**exploitation logicielle** (bugs de state machine, PRNG
> faible, oracle CRC pour Simos18 ; CVEs QSEE/TrustZone → EL3 pour l'autre), **sans injection
> matérielle** — le seul lien FI de QSEE est un renvoi vers un EMFI-EL3 antérieur sur le même
> Qualcomm IPQ5018 (`[ref]`, hors corpus).

*Voir aussi : [`00`](00_SYNTHESE_CORPUS.md) (fondements sourcés), [`01`](01_PRECONISATIONS_ARCHITECTURE.md)
(carte), [`04`](04_REFERENCES.md) (bibliographie).*
