# ECU automobile

> Vecteurs : voltage (extraction firmware, UDS) et EMFI (bootloader BAM in-situ, seul cas
> corpus sur véhicule réel).

## 1. Surface d'attaque des protocoles de diagnostic (UDS)

[corpus, whitepaper escar EU 2018 *There Will Be Glitches*, complété par le talk
hardwear.io 2018 de Cordoba `[ref]`] :

- **`SecurityAccess`** (seed-key) est protégé par un **timeout de 10 min après 3 échecs** —
  peu praticable en direct par force brute FI.
- **`ReadMemoryByAddress` / `WriteMemoryByAddress` n'ont pas cette limite** et ne vérifient
  qu'un flag « authenticated » interne → **cible de choix pour le glitch**.
- Recherche de paramètres par diviser-pour-régner avec indicateurs comportementaux (réponse +
  consommation), sans connaissance du firmware.
- ⚠️ **Divergence non résolue entre les deux sources** : le whitepaper documente le retrait
  des condensateurs de découplage ; le talk affirme à l'oral qu'aucune autre modification n'a
  été faite sur l'ECU (« réinstallable tel quel »). À revérifier avant de trancher, ne pas
  résoudre par supposition.
- Complément `[ref]` non recoupé indépendamment : un taux de succès EMFI comparable au
  voltage glitch aurait été obtenu sur les mêmes cibles — piste à approfondir, pas une donnée
  chiffrée.

## 2. Extraction firmware complète (voltage)

[corpus, Milburn, Timmers, Wiersma, Pareja, Cordoba, escar EU 2018] : extraction de
**512 kB** de firmware d'un ECU réel — retirer les condensateurs de découplage ; caractériser
**à l'aveugle** via indicateurs comportementaux ; cibler `ReadMemoryByAddress` ou bypasser
l'interface debug. Budgets : **~3 %** de succès, **0x40 octets par glitch réussi**,
**~300 000 glitchs / ~3 jours** pour 512 kB.

## 3. Bootloader BAM — seul cas EMFI in-situ sur ECU réel du corpus

[corpus, O'Flynn, ESCAR EU 2020, *BAM BAM!!*] :

- **Cible** : bootloader **BAM** (Boot Assist Module) des MCU automobiles PowerPC
  **MPC55xx/56xx** (NXP/Freescale ; ST SPC5xx architecturalement proche). Testé sur 4
  environnements dont un **ECU GM réel** (référence E41, extrait d'un véhicule 2019).
- **Banc** : ChipSHOUTER (décharge capacitive) + ChipWhisperer-Pro (offset ajustable par pas
  de 50 ns) ; tension par défaut **444 V** ; pointe 4 mm, testée en polarité CW et CCW.
- **Fenêtre d'injection** : succès quasi constant **0,1–3,5 µs**, plage utile 0,1–5,0 µs,
  aucun succès validé au-delà de ~5,5 µs.
- **Taxonomie à 6 résultats regroupés en 5 libellés** (Normal / Err-Reset / Err-Protocol /
  Err-RunFail ×2, regroupés par les auteurs / Success) — plus fine que le scoring général, voir
  [`../cross-cutting/campaign-instrumentation-metrics.md`](../cross-cutting/campaign-instrumentation-metrics.md).
  ⚠️ « Normal » (~92–98 %) = catégorie « aucun effet », **pas un taux de succès** ; le vrai
  taux de bypass (« Success ») est **~1,2–1,9 %** sur cartes de dev, avec un outlier à
  **36,3 %** sur un environnement (mot de passe public).
- ★ **Confirmation empirique de la dépendance à la polarité de sonde sur cible réelle**
  (corrobore Ordas 2015, voir [`../by-vector/emfi.md`](../by-vector/emfi.md) §1) : sur l'ECU
  E41, **0 % de succès avec la pointe 4 mm CCW**, succès **reproduit** en CW — recherche de
  position/polarité **4-6 heures** avant configuration gagnante, contre 1-5 min sur cartes de
  dev.
- **Contre-mesure la plus robuste identifiée** : device **censuré + mot de passe public** —
  dans cette config, **aucun bypass EMFI obtenu**. Les séries plus récentes (MPC57xx, ST
  SPC57xx/58xx) désactivent le strapping externe du pin de boot, rendant l'attaque
  single-fault inopérante. Tentative sur variante ST SPC560B : **inconclusive** (comparaison
  du mot de passe déportée vers un périphérique matériel, vérifiée seulement en fin de
  téléchargement).
- **Recoupement vidéo `[ref]`, non recoupé indépendamment** : la même attaque reproduite sur
  la même puce MPC5566 avec un PicoEMP (plafond 250 V) au lieu du ChipSHOUTER (444 V) ;
  succès rapporté à seulement **~60 V** en glitchant via le bus **CAN** plutôt qu'UART —
  chiffre oral non vérifié. Méthode notable : détection d'un glitch réussi **sans firmware de
  test**, par observation à l'oscilloscope d'une dérive du pin `clock-out` du MCU.

## 4. Efficacité des contre-mesures ASIL-D — transférable au-delà de l'automobile

[corpus, *Safety != security*, deck FDTC 2017] — trois MCU automobiles anonymisés (QM =
voltage, D1 = voltage+EM, D2 = EM) :

- **Code applicatif, succès moyen** : QM 100 % · D1 16 % · D2 37 %.
- **Déverrouillage JTAG** : QM 80 % · D1 1,3 % · D2 0,34 %.
- **Classement chiffré de l'efficacité des contre-mesures** (sur D1) : voir
  [`../cross-cutting/detectors-countermeasures.md`](../cross-cutting/detectors-countermeasures.md)
  §4 (lockstep 90 %, ECC flash 68 %, parité RAM 14 %...).
- **Méthode de localisation transposable à toute cible fermée** : firmware inconnu, fenêtre
  d'injection trouvée par **analyse différentielle de consommation** (comparaison de traces
  JTAG déverrouillé vs verrouillé).
- Conclusion imprimée : **« ISO 26262 ≠ Security »**.

## 5. Ce que le corpus ne couvre pas

Aucune séquence documentée sur les bus CAN-FD/LIN/FlexRay modernes chiffrés, aucun cas
d'attaque sur un HSM (Hardware Security Module) automobile dédié. Le chiffre « ~60 V via
CAN » (§3) reste une piste orale non vérifiée, pas une donnée de campagne.

## Renesas RH850 — deux write-ups `[ref]`

> ⚠️ **`[ref]`** (`docs_pdf/writeups/`, cités par URL, jamais par page).

- **icanhack — *Bypassing the Renesas RH850/P1M-E read protection using fault injection*** : voltage
  FI contre la protection en lecture d'un MCU automobile.
- **jerinsunny — *RH850/F1L ID code check bypass via glitching*** : voltage FI contre la
  **vérification du code d'identification**.

Ces deux cas complètent le fonds automobile du corpus — bootloader **BAM** des MPC55xx/56xx par EMFI
[corpus, O'Flynn], **UDS ReadMemoryByAddress** [corpus, escar 2018] et MCU **ASIL-D** [corpus, Pareja
& Wiersma] — en apportant la famille **Renesas**, absente jusqu'ici. Le **STM8AF6266** de
*Fill your Boots* [corpus] relève du même domaine : il équipe des **antidémarrages**.

★ **Convergence à noter** : sur ces cibles, la protection cassée est presque toujours une
**vérification unique** (code d'identification, mot de passe, niveau de protection) — ce que
l'anti-pattern **A7** de *Fill your Boots* formalise : *le taux de succès décroît **exponentiellement**
avec chaque vérification redondante*. Voir
[`../cross-cutting/detectors-countermeasures.md`](../cross-cutting/detectors-countermeasures.md).
