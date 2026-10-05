# 02 — Nomenclature matérielle (BOM) & comparatif acheter/construire

> **Nature du document — RECOMMANDATION.** Les composants **[corpus]** sont ceux **nommés dans
> Bozzato (TCHES'19)** — ils sont attestés dans un montage V-FI qui a extrait du firmware STM32. Les
> composants **[reco]** sont des propositions d'ingénierie de ma part : **familles et points d'achat
> réels, mais références et prix à vérifier en disponibilité** avant commande (Mouser / Digi-Key /
> LCSC). Les prix sont **indicatifs** (ordre de grandeur, 2025). Rien ici n'est extrait des PDF hors
> mentions **[corpus]**.
>
> 📄 **Datasheets** des composants nommés dans [`../datasheet/`](../datasheet/) (specs vérifiées).
> Le **crowbar par défaut est l'AO3400A** (N-canal, RDS(on) basse, pulsé 30 A) ; l'IRLML6402 est un
> **canal P** → réservé au load switch, jamais au crowbar.

---

## 1. BOM — Palier 1 (crowbar, à construire en premier)

| # | Fonction | Référence | Spéc clé | Source | Prix ind. |
|---|---|---|---|---|---|
| 1 | Contrôleur de timing | **Raspberry Pi Pico 2** (RP2350A) ou puce nue RP2350 | 150 MHz, 3× PIO / 12 SM, IOVDD 1,8–3,3 V (utilisé à 3,3 V) | [reco] (brief off.) | 5–10 € |
| 2 | MOSFET crowbar (**défaut**) | **AO3400A** (N-canal) | 30 V · Id 5,7 A / **pulsé 30 A** · RDS(on) 19–32 mΩ @4,5 V · Qg 6–7 nC · Vgs(th) 0,65–1,45 V · SOT-23 — *vérifié datasheet* | [reco] + [`datasheet/`](../datasheet/) | < 0,20 € |
| 2-bis-ctrl | ★ **Contrôle du MOSFET AVANT soudure** | multimètre en **mode diode** | SOT-23 : **1 = G, 2 = S, 3 = D** (la broche seule en face des deux autres est le **drain**). Rouge sur br. 2, noir sur br. 3 ⇒ **0,5–0,7 V** · sens inverse ⇒ **OL** · grille isolée ⇒ **OL**. ★ **Tout autre résultat = rebut** (contrefaçon) | `[reco]` + [`09`](09_BANC_BAT32_FAULTYCAT_RAIDEN.md) §4.1 | — |
| 2-alt | MOSFET crowbar (alternatives) | **IRLML2502** (N, 20 V, 45 mΩ datasheet / **35 mΩ** annoncé par O'Flynn, SOT-23) · **VN2222** (réf. historique) · **IRF7807** (N, **14 mΩ, 88 A pulsé**) | ★ **IRLML2502 n'est plus une simple alternative** : c'est le MOSFET **effectivement employé sur ATMega328P**, soit la classe de cible du projet **[corpus, O'Flynn p. 2-3]** — « lower gate charge… can be switched faster ». **IRF7807** = variante forte puissance, réservée aux **SoC/FPGA à rail basse impédance**. VN2222 = montage de référence Bozzato | **[corpus, O'Flynn p. 2-3]** + **[corpus, Bozzato p. 216]** (VN2222) | < 1 € |
| 2-bis | **Organe de glitch alternatif** (au lieu du MOSFET) | **Maxim MAX4619** (MUX analogique 3 canaux) | commute le rail entre `VCC` nominal et une **tension basse réglable** au lieu de le court-circuiter → **largeur ET profondeur commandées séparément**. Employé par **Gerlinsky** (origine) et **chip.fail** (qui casse ainsi un **STM32F2**). ⚠️ **Ne convient pas à un rail de cœur basse impédance** — *vérifié datasheet* : **3× SPDT CMOS**, **R_on 10 Ω @5 V / 20 Ω @3 V**, **±75 mA continus**, **t_ON 15 ns / t_OFF 10 ns** | **[corpus, Gerlinsky sl. 27-28/33 ; chip.fail sl. 65-66]** + [`datasheet/`](../datasheet/) | ~2–3 € |
| 3 | Driver de grille | **ADP3623** (driver MOSFET rapide) | *« temps de commutation rapides et nets »* | **[corpus, p. 216]** | 2–4 € |
| 3-alt | Driver de grille | UCC27321 / EL7158 (**à valider**) | fort courant de grille, faible délai de propagation | [reco] | 1–3 € |
| 4 | Résistance de limitation de courant `Rs` | R série alim → Vcc cible, **non bobinée**, **≥ 0,25 W**, sur **borne à vis** | **valeur non donnée par le corpus** → ★ **se MESURE** : `C_résid = τ_remontée / Rs` tranche entre **4,3 Ω** (`C_résid ≳ 5 µF`) et **10 Ω** (`≲ 1 µF`) ; **> 22 Ω : non**. ⚠ Ordre de grandeur = **unités d'ohms**, pas le « 10–100 Ω » d'origine | [corpus, Fig. 1a] + `[reco]` [`05`](05_SCHEMAS_ELECTRONIQUES.md) §4 | < 1 € |
| 4-bis | **Réservoir de rail `C_res`** | **100 µF faible ESR // 100 nF**, **côté SOURCE** de `Rs` | **non optionnel** : le tir tire ~0,77 A, soit ~15 µC sur 20 µs ⇒ sur 100 µF **ΔV ≈ 150 mV** (rail stable), sur 10 µF **1,5 V** = brownout | `[reco]` + [`09`](09_BANC_BAT32_FAULTYCAT_RAIDEN.md) §3.3 | < 1 € |
| 4-ter | **Amortissement de drain `R_damp`** | jeu de **0,15 / 0,47 / 1,2 Ω**, **1 W**, **non bobinées** | ★ sans elle le nœud **oscille jusqu'à −2,37 V**. Règle `R_damp ≈ √(L_boucle/C_résid)` ⇒ **choisie après** la mesure de `C_résid` | `[reco]` recoupé ngspice + [`09`] §4.4 | < 1 € |
| 4-quater | **Pull-down de grille `R_pd`** + **protection ADC `R_adc`** | **`R_pd` 1 kΩ** (grille→source, sur la carte MOSFET) · **`R_adc` 2 × 1 kΩ** (vers GP26/GP27) | ★ **`R_pd` obligatoire** — erratum **RP2350-E9** (120 µA dans un pad en entrée) : 1 kΩ ⇒ 0,12 V, **pas 10 kΩ** ⇒ 1,20 V qui allume le MOSFET. `R_adc` : le nœud passe sous 0 V contre −0,3 V de maximum absolu | `[ref]` E9 + [`09`] §4.2/§4.4 | < 1 € |
| 5 | Load switch high-side | **TPS22918** (intégré) **ou** **IRLML6402** (P-canal, −20 V, 65 mΩ) + inverseur **2N7002** | power-cycle du DUT ; **obligatoire** | [reco] + [corpus, Peak Clock p. 88] | 1–3 € |
| 6 | Entrée trigger | comparateur rapide (ex. TLV3501 **à valider**) + connecteur **SMA** | front propre ; utile si NRST lent (pull-up ~40 kΩ) | [reco] + [corpus, p. 209] | 2–5 € |
| 7 | Interface cible | headers SWD (Cortex 10-pin) + UART + broches BOOT0/NRST | pilotées par le RP2350 | [reco] | < 2 € |
| 8 | Support cible | breakout du STM32 **sans condensateurs de découplage** | réduit Δ (recharge) ; sonde < 10 mm de la broche d'alim | [corpus, p. 203] | 2–5 € |
| 9 | Protections | TVS bidirectionnel sur le rail cible, clamp sur les lignes exposées, LEDs d'état, découplage RP2350 | ★ **Dimensionner le TVS pour un overshoot de plusieurs fois VDD, pas pour un simple undershoot** : à la relâche du crowbar, O'Flynn mesure ≈ **5,6 V sur un rail 1,3 V** et une excursion **−0,35 → +4,95 V sur un rail 3,2 V** *(lu sur graphe)* | **[corpus, O'Flynn p. 4, p. 6]** | 1–3 € |

**Sous-total Palier 1 : ~22–45 €** (hors cible et hors instrumentation).

★ **Révision du 2026-09-16, après campagne de banc.** Les lignes **4-bis** (`C_res`), **4-ter**
(`R_damp`), **4-quater** (`R_pd` + 2 × `R_adc`) sont **nouvelles** : ce sont quatre passifs et un
condensateur, soit **~2 à 5 €** de plus — négligeable en euros, **mais aucun d'eux n'est
optionnel**. ⚠ **C'est le point à retenir de cette révision** : le coût du crowbar n'a pas bougé,
**ce qui a changé est la liste minimale**. Un Palier 1 sans `R_pd` peut allumer son MOSFET hors
firmware ; sans `R_damp` il envoie le nœud à −2,37 V ; sans les `R_adc` il dépasse le maximum
absolu des entrées du contrôleur. Voir [`05`](05_SCHEMAS_ELECTRONIQUES.md) §4.

---

## 2. BOM — Palier 2 (forme d'onde arbitraire, évolution)

| # | Fonction | Référence | Spéc clé | Source | Prix ind. |
|---|---|---|---|---|---|
| 10 | DAC rapide | DAC **≥ 12 bits**, rapide, piloté par le RP2350 (parallèle/SPI) — famille AD97xx / DAC80xx (**à valider selon BP visée**) | 12 bits **impératif** (170 mV de dérive = attaque KO) | [reco] + [corpus, p. 218] | 5–20 € |
| 10-alt | Générateur DDS externe | **FeelTech FY3200S** | ±10 V, 2048 pts, 12 bits, 6 MHz, USB — la brique exacte de Bozzato | **[corpus, p. 203]** | ~50 $ |
| 11 | Ampli de glitch | **TI THS3062** (current-feedback, high slew-rate) | **145 mA**, non-inverseur 2 étages, alimente la cible en continu | **[corpus, p. 204]** | 5–10 € |
| 12 | Coupure d'alim | **relais reed** en sortie d'ampli | hard reset + protection pendant le rechargement de forme | **[corpus, p. 204]** | 2–5 € |

**Sur-coût Palier 2 : ~20–70 €** selon DAC intégré vs générateur DDS externe.

> **Contraintes de conception à ne pas rogner** [corpus] : sortie **±10 V** (glitchs sous 0 V
> courants), BP **6 MHz** (suffit pour MCU sub-GHz, limite pour SoC rapides), débit de
> reconfiguration de forme visé **~200 ms**, courant cible **< 100 mA**.

---

## 3. Matériel de banc (instrumentation)

Liste minimale, d'après Skorobogatov (**[corpus, slide 7]**) et Bozzato :

| Équipement | Usage | Prix ind. |
|---|---|---|
| **Oscilloscope** (≥ 200 MHz, idéalement ≥ 1 GS/s) | visualiser la forme du glitch, calibrer, mesurer Δ | 300–3000 € |
| **Alimentation programmable** | VDD nominal réglable, underpowering (reco n°1 : 1,0 → 0,93 V) | 80–400 € |
| **Bus Pirate 5** (option compacte, **[ref]**) | PSU 1–5 V/300 mA + UART (8E1) + mesure V/I + détection SWD réunis dans un outil ; sert de **support de banc EMFI** avec un FaultyCat (cf. [`06_EMI_INJECTOR_EMFI.md`](06_EMI_INJECTOR_EMFI.md) §5.2). **300 mA ⇒ MCU only, pas x86.** | ~30–40 € |
| **Analyseur logique** | trigger, UART/SWD, séquencement | 10–200 € |
| Station de soudage/dessoudage | dessouder la cible, breakout | 50–300 € |
| Sonde de température (PT100 / thermistance) + éventuel chauffage | compensation ~0,1 %/°C ; chauffer élargit la fenêtre | 10–50 € |
| PC + framework Python (USB) | orchestration, recherche de paramètres | — |

---

## 4. Comparatif « acheter vs construire »

Positionnement de la carte DIY RP2350 face aux solutions du marché (**[corpus]** pour PicoGlitcher /
ChipWhisperer / ChipShouter cités dans le SoK 2025 ; **[ref]** pour le PicoEMP modifié, sourcé d'un
talk vidéo — cf. [`06`](06_EMI_INJECTOR_EMFI.md) §2.1 ; le reste est du positionnement **[reco]**) :

| Solution | Type | Prix ind. | Pour | Contre |
|---|---|---|---|---|
| **Carte DIY RP2350** (ce projet) | crowbar + AGW | **~20–110 €** | maîtrise totale, agnostique VDD/VCAP, évolutif Palier 1→2, PIO déterministe | à concevoir/valider, pas de support |
| **PicoGlitcher v2** | RP2040/RP2350, crowbar | **~50 $** [corpus, SoK réf. 81] | prêt à l'emploi, même classe de puce | architecture non décrite dans le corpus (à investiguer) |
| **ChipWhisperer-Nano / Lite / Husky** | clock + voltage | **~50 → 600 $+** [corpus, SoK réf. 82] | écosystème mûr, scope intégré (Husky), très documenté (utilisé dans DSN'21) | fermé matériellement, coût croissant |
| **Faultier** (Hextree) | crowbar, éducatif | ~bas coût | pédagogique, bien documenté | fonctionnalités volontairement limitées |
| **PicoEMP** | **EMFI** (pas voltage) | **~133 $** (kit Tindie, vérifié) | vecteur *local* (échappe aux détecteurs globaux, cf. DATE'14) ; ~250 V | hors périmètre voltage ; ~1 impulsion/s |
| **PicoEMP modifié** (RECESSIM, `[ref]`) | EMFI | ~150–250 $ (fourchette orale **non recoupée**) | ~500 V à 1 kHz démontré ; comble le vide PicoEMP↔ChipShouter — cf. [`06`](06_EMI_INJECTOR_EMFI.md) §2.1 | modification **tierce**, non affiliée NewAE ; refroidissement actif obligatoire ; sécurité d'origine dégradée |
| **ChipShouter** (NAE-CW520) | EMFI pro | **~4 000 $** [corpus, SoK] | puissant, local ; >1000 imp/s sans refroidissement actif | cher, hors périmètre |

> **Recommandation.** Pour valider la chaîne et les attaques RDP STM32F103 rapidement et à moindre
> risque, **un PicoGlitcher v2 ou un ChipWhisperer-Nano** sert d'étalon de référence pendant que la
> **carte DIY Palier 1** est mise au point. La carte DIY se justifie par le contrôle du timing en PIO,
> l'agnosticité VDD/VCAP et l'évolution vers le Palier 2 (AGW), là où Bozzato **[corpus]** montre un
> gain de 63 % sur les cibles résistantes.

---

## 5. Budget récapitulatif

| Configuration | Coût matériel (hors instrumentation) |
|---|---|
| **Palier 1 seul** (crowbar) | **~22–45 €** |
| **Palier 1 + Palier 2** (AGW intégré) | **~42–115 €** |
| + étalon commercial (PicoGlitcher / CW-Nano) | **+ ~50–120 €** |
| Instrumentation de banc (si à acquérir) | **~450–3 700 €** (dominée par l'oscilloscope) |

> ⚠ **Les fourchettes ci-dessus intègrent la révision du 2026-09-16** (+2 à 5 € de passifs
> obligatoires au Palier 1, §1). Elles restent des **ordres de grandeur**, pas des devis.

Repère de cadrage : Barenghi *et al.* (cité par Bozzato p. 199) définit *« low cost »* comme
**< 3 000 $ d'équipement** — la présente carte y est très largement.

### 5.1 Repères de coût `[corpus]` ajoutés par les sources du gist `dev-zzo`

Ces chiffres viennent de **bancs qui ont effectivement cassé une cible**, ce qui les rend plus utiles
qu'un prix catalogue. Ils encadrent le budget de la carte du projet (~20–110 €).

| Banc | Coût imprimé | Ce qu'il a cassé | Source |
|---|---|---|---|
| **chip.fail** — glitcher voltage complet | **≈ 92 $** : Digilent Cmod A7 **~70 $** + MUX PMOD **~1,80 $** + alim DPS3003 **~20 $** | **STM32F2** (Trezor One), nRF52840, ESP32, SAM L11 | [corpus] sl. 63 |
| **chip.fail** — « le glitcher à 5 $ » | **5 $** | **SAM L11** (secure bootloader) | [corpus] sl. 116-117 |
| **COSIC** — injecteur **EMFI** complet | **≈ 40 €** | **STM32F411** (fautes sur `STM`) | [corpus] p. 12 |
| **RHUL** — station **laser** | diode **< 40 $** + switch **70 $** + FPGA **35 $** | AVR / ARM (skip d'instruction) | [corpus] p. 2 |
| **Kraken/Trezor** — estimation des auteurs | *« a glitching device that could be sold for about **$75** »* | **STM32F205** (*seed*) | `[ref]`, §J de [`04`](04_REFERENCES.md) |
| **jrainimo** — glitcher à **NE555** | quelques euros | **STM8** (dump firmware) | `[ref]` |

> ★ **Deux enseignements de budget.** (1) **Le coût du glitcher n'est pas le facteur limitant** : un
> banc à ~92 $ casse un STM32F2, un banc à 5 $ casse un SAM L11 — ce qui coûte cher, c'est
> **l'instrumentation de mesure** (§3) et le **temps de caractérisation**. (2) ★ **L'EMFI n'est plus
> réservé au haut de gamme** : à **≈ 40 €**, l'injecteur COSIC se situe **sous** le PicoEMP (133 $) et
> le FaultyCat, tout en étant le seul banc `[corpus]` à avoir fauté un **STM32** par voie EM
> (cf. [`06`](06_EMI_INJECTOR_EMFI.md) §1.7 et §4.1).

*Suite : [`03_METHODOLOGIE_CAMPAGNE.md`](03_METHODOLOGIE_CAMPAGNE.md) — comment mener l'attaque.*
