# IoT / secure boot embarqué (bare-metal ou RTOS, hors OS complet)

> Distinct de [`linux-android-arm-socs.md`](linux-android-arm-socs.md) : ici la cible n'a pas
> de pile OS complète, le secure boot est directement porté par le firmware/RTOS. Vecteur :
> EMFI.

## 1. Banc EMFI DIY chiffré contre un SoC IoT moderne

[corpus, Toldo, SEEMOO TU Darmstadt, hardwear.io USA 2023, *Affordable EMFI Attacks Against
Modern IoT Chips*] :

- **Cible** : *« VFI protected IoT chip »*, secure boot, **processeur RISC-V mono-cœur**,
  jamais nommée en texte dans les slides. ⚠️ Seule la sérigraphie **« C3 Mini »** de la carte
  de dev est lisible sur photo — l'identification usuelle **Espressif ESP32-C3** est une
  **inférence `[ref]`**, pas `[corpus]`.
- **Budget total** : ~200 $ platine XY + ~2000 $ pulseur EMFI + ~100 $ générateur de délai
  (~2300 $). Détail équipement :
  [`../cross-cutting/equipment-cost-tiers.md`](../cross-cutting/equipment-cost-tiers.md).
- **Résultat** : *« Successful Instruction Skip »* revendiqué sur une **boucle synthétique**
  de test (GPIO haut → 100 additions → GPIO bas → vérification), **pas sur le secure boot
  réel**. Zone de fautes groupée dans un coin du die, hypothèse : le CPU — coin par ailleurs
  « protégé » par les détecteurs de brown-out.
- **Aucun taux de succès agrégé** n'est donné.

### ★ Trois obstacles de caractérisation — directement transférables

1. La toolchain compile vers **FreeRTOS avec détection de brown-out** (non dédiée à l'EMFI)
   et d'autres contrôles de sûreté qui interfèrent avec le diagnostic.
2. La boucle de test était **éliminée par l'optimisation du compilateur** — et même sans
   optimisation, échec persistant → passage en **assembleur inline** pour garantir que le
   code de test s'exécute réellement tel qu'écrit.
3. Les transferts **UART sont corrompus par l'injection elle-même** → abandon de l'UART-USB
   intégré au profit d'un **UART déporté sur GPIO**, pour ne pas perdre le canal de
   diagnostic pendant l'expérience.

- **Crashes liés à l'horloge** concentrés dans une autre zone du die, attribués à la
  proximité d'un oscillateur — des die-shots (décapsulation) permettraient une cartographie
  plus précise, non réalisée ici.
- **Scoring et outillage** : logiciel custom *EMFIControl*, scoring par position en 5
  catégories, cartographie XY grossière puis affinée. Ressources publiées :
  `github.com/unixb0y/EMFI-Resources`.
- **Conclusion imprimée** : la puce est *« sécurisée contre le VFI et les canaux auxiliaires,
  mais pas contre un attaquant sérieux »* — écho direct au principe « l'EMFI locale échappe
  aux détecteurs globaux » ([`../cross-cutting/detectors-countermeasures.md`](../cross-cutting/detectors-countermeasures.md)
  §3).

## 2. Leçon générale pour tout firmware de test EMFI

Les trois obstacles ci-dessus (brown-out non dédié, optimiseur qui élimine le test, canal de
diagnostic auto-corrompu) sont des pièges **génériques** de banc EMFI sur cible RTOS/embarqué
— à vérifier systématiquement avant d'attribuer un échec de campagne à l'absence de
vulnérabilité plutôt qu'à un artefact de banc.

## Cas ESP32 — sept write-ups `[ref]`, dont un EMFI

> ⚠️ **`[ref]`** : write-ups convertis en PDF dans `docs_pdf/writeups/`, **cités par URL, jamais par
> page**. Liste : [`../../docs/04_REFERENCES.md`](../../docs/04_REFERENCES.md) §J.

L'ESP32 est, avec le STM32, la famille la plus densément documentée du fonds : **secure boot**,
**chiffrement de flash** et **extraction de clés** y sont tombés par FI, avec **deux CVE** à la clé.

| Write-up | Vecteur | Apport |
|---|---|---|
| Raelize — *Bypassing Secure Boot using **EMFI*** | **EMFI** | reproduit **CVE-2019-15894** par voie EM là où l'original utilisait du voltage ; sonde Riscure EM-FI Transient Probe ; ★ **seule modification : retrait du capot métallique** du module ESP32-WROOM-32. Détail : [`../by-vector/emfi.md`](../by-vector/emfi.md) §10 |
| Raelize — *Bypassing Encrypted Secure Boot* | voltage | **CVE-2020-13629** |
| Raelize — *Bypassing Flash Encryption* | voltage | **CVE-2020-15048** |
| Raelize — *Controlling PC during Secure Boot* | voltage | modèle *corruption de transfert → contrôle du PC* appliqué à Xtensa (instruction `callx8`), glitcher open-source **iceGLITCH** |
| LimitedResults — *Pwn the ESP32 Secure Boot* · *…Forever* · *…crypto-core* | voltage | série de trois attaques, **extraction des clés de chiffrement de flash et de secure boot** incluse |

★ **Enseignement de méthode** : le même défaut matériel est atteignable **par deux vecteurs
différents** (voltage puis EM). Le choix du vecteur relève donc de l'**accès physique** (rail
accessible ? capot métallique ? découplage retirable ?) plus que de la nature du bug.

## Cas MediaTek — BootROM d'un SoC applicatif `[ref]`

*NCC Group — There's A Hole In Your SoC: Glitching The MediaTek BootROM* (**MT8163V**, voltage).
La BootROM charge le *preloader* depuis l'**eMMC** et **vérifie sa signature** ; le glitch vise cette
vérification. Trigger produit par un **FPGA** (sortie 3,3 V) vers un ChipWhisperer.
★ **Fait de dimensionnement de campagne** : la cadence est fixée par la cible, pas par le glitcher —
**~2 s** par tentative si l'image est valide, **~700 ms** si elle est corrompue. Les auteurs notent
que le flux *BootROM → preloader* est partagé par de nombreux SoC MediaTek.
