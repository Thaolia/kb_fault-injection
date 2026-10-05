# Linux / Android / SoC ARM applicatifs

> Cibles à OS complet (pas du bare-metal) : privesc noyau, root Android, secure boot,
> TrustZone/OP-TEE. Vecteurs : surtout voltage, un cas EMFI documenté.

## 1. Privesc Linux → root (voltage)

[corpus, Timmers & Mune, FDTC 2017 *Escalating Privileges in Linux using Fault Injection* +
BlueHat v17 *KERNELFAULT*] — ARM Cortex-A9/Linux :

- Glitcher le check noyau de **`setresuid(0,0,0)`** → shell root. **~1,3 %** de succès à la
  fenêtre **3,14–3,44 µs**, root en 5 min. Scoring 3 réponses *Expected / Mute-Reset /
  Success* directement réutilisable.
- Autres surfaces : `/dev/mem`, contrôle du PC noyau.
- **Grille contre-mesures** [corpus, KERNELFAULT] : contre-mesures **SW inefficaces**
  (détournement du flot avant leur exécution) vs **exploit-mitigations** DEP/NX/ASLR/CFI, qui
  résistent mieux car elles agissent après la corruption. Taxonomie de coût : **< 300 $**
  de tooling possible. Détail transversal des contre-mesures :
  [`../cross-cutting/detectors-countermeasures.md`](../cross-cutting/detectors-countermeasures.md)
  §5.

## 2. Root d'un SoC Android via EMFI

[corpus, Timmers, Hardwear.io NL 2025, *setresuid(): Glitching Google's TV Streamer from adb
to root*] — SoC **MediaTek MT8696** (quad-ARM, ~1,8 GHz) :

- Banc : sonde EMFI commerciale Keysight/Riscure + contrôleur Spider + platine XYZ motorisée
  + power-cycle USB.
- Faute : **corruption d'instruction** (1 bit-flip : opérande `add x1`→`add x0`, opcode
  `add`→`adrp`) sur l'appel `setresuid(0,0,0)` → retour 0 = root.
- **Méthodologie notable** : attaque **runtime SANS trigger ni délai** (la cible boucle),
  glitchs aléatoires continus ; scan initial ~40 min ; analyse par cœur (`taskset`).
- **Limite** : **SELinux non contourné** — le root obtenu ne casse pas toutes les couches de
  sécurité du système.
- Paramètres EM (tension bobine, diamètre de sonde, distance, polarité) **non communiqués**
  → à caractériser. Mécanisme EMFI général :
  [`../by-vector/emfi.md`](../by-vector/emfi.md).

## 3. Bypass secure boot (voltage, simulateur dédié)

[corpus, Bogaard & Timmers, Black Hat EU 2018, *Secure Boot Under Attack*] :

- VCC **1,2 → 0,9 V**. Viser l'étape **authenticate/jump** de la chaîne de boot (BL1 →
  U-Boot).
- **Simulateur open-source FiSim** (Unicorn + Capstone) pré-identifie les instructions
  glitchables du binaire de boot avant la campagne physique — méthode transposable à
  n'importe quel binaire de boot dont on a le désassemblage.
- Les contre-mesures **SW** sont contournées par le modèle de corruption (pas seulement de
  skip).

## 4. TrustZone / OP-TEE — fautes de bus système (EMFI)

[corpus, Mishra *et al.*, NDSS 2024, *Faults in Our Bus*] :

- **Register sweeping** : le `mov` qui charge le code retour de `verify_signature` d'OP-TEE
  est fauté vers `0x0`, le `cbnz w0, <error_out>` ne branche pas → un TA (Trusted
  Application) malveillant est chargé. **CVE-2022-47549.**
- **~40 injections indépendantes** suffisent à compromettre TrustZone une fois le point
  d'injection identifié.
- Cibles : **OP-TEE et MyTEE**, sur **RPi3 et RPi4**, sans modification de l'attaque entre
  les deux plateformes.
- **Faille de spécification exploitée** : GlobalPlatform ne précise pas comment traiter deux
  TA de même UUID ; OP-TEE préfère ouvrir une session avec un TA non persistant → un TA
  malveillant peut masquer un TA persistant légitime (y compris le Gatekeeper Linaro).
- Détecteurs qui **n'arrêtent pas** cette attaque : intégrité de flot de contrôle (bloque le
  skip, pas la faute de bus), SeCReT (la faute vient de l'attaquant, hors de son modèle de
  menace), MyTEE (protège mémoire/DMA/IO, pas la spec GP elle-même).
- Contre-mesure efficace côté OP-TEE : checks de redondance sur les valeurs de retour
  sensibles (`callee_done_not_zero`, `callee_done_memcmp`).
- Modèle et banc EMFI détaillés : [`../by-vector/emfi.md`](../by-vector/emfi.md) §4.

## 5. Hors périmètre — à ne pas confondre avec de la FI

Deux travaux souvent trouvés en cherchant « FI » sur ces cibles n'en sont pas :
*QSEE Wifi Pro* (OffensiveCon 2026) **`[corpus]`** et *Secrets of Simos18* (hardwear.io USA
2024, Ledbetter) **`[ref]`, talk vidéo hors corpus** — provenances différentes, à ne pas
fusionner. Les deux sont de l'**exploitation logicielle pure** (bugs de state machine, PRNG
faible, oracle CRC, CVEs QSEE/TrustZone → EL3), **sans injection matérielle**. Signalés ici pour
éviter de les confondre avec un cas FI lors d'une recherche future sur ces mêmes cibles
(Qualcomm IPQ5018 pour QSEE).

## Deux SoC applicatifs supplémentaires `[ref]`

> ⚠️ **`[ref]`** (`docs_pdf/writeups/`, cités par URL, jamais par page).

- **NCC Group — *Glitching the MediaTek BootROM*** (**MT8163V**) : glitch de la **vérification de
  signature du *preloader*** chargé depuis l'eMMC, en amont de tout code modifiable. Trigger produit
  par **FPGA**. Cadence dictée par la cible : **~2 s** par tentative si l'image est valide,
  **~700 ms** si elle est corrompue. Détail :
  [`iot-embedded-secure-boot.md`](iot-embedded-secure-boot.md).
- **CyberIntel — *Secure Boot Bypass in MSM8916/APQ8016*** (Qualcomm) : contournement du *secure
  boot* d'un SoC mobile par FI.

★ **Ce qu'ils confirment** : sur SoC applicatif, la cible payante n'est pas le noyau ni l'application
mais **la première vérification de signature du chargeur**, exécutée depuis une ROM immuable — même
schéma que BADFET (uBoot), le Google TV Streamer (`setresuid` en runtime restant l'exception) et le
secure boot ESP32.
