# Cartes à puce / éléments sécurisés (JavaCard, EAL-certifiés)

> Vecteur : voltage (VCC FI). Méthodologie de recherche associée :
> [`../cross-cutting/parameter-search-methodology.md`](../cross-cutting/parameter-search-methodology.md).

## 1. Trois cibles documentées, du non protégé au certifié

[corpus, Boix Carpi *et al.*, CARDIS 2013, *Glitch it if you can*] :

| Cible | Description | Contre-mesures |
|---|---|---|
| **Target A** | ATMega163 + 24C256, révision matérielle 2003, « Training Card 6 » Riscure | **aucune** (SCA ni FI) |
| **Target B** | carte achetée en 2013, design IC fin 2004, JavaCard OS 2.2.1/GlobalPlatform 2.1.1 | logique de détection FI, capteurs lumière/température/horloge |
| **Target C** | même matériel que B | **certifiée Common Criteria EAL4+ en 2008** |

Code attaqué sur A : vérification de PIN à 4 chiffres (`if (digits_ok==4)`). Sur B/C :
applet double boucle imbriquée 2×1000 avec compteurs et checksum. **Plusieurs exemplaires de
chaque carte utilisés** — une conséquence directe du risque de destruction permanente propre
au VCC FI.

## 2. Résultat central — une cible certifiée EAL4+ cassée

★ La stratégie de recherche **adaptive zoom & bound** (détail complet :
[`../cross-cutting/parameter-search-methodology.md`](../cross-cutting/parameter-search-methodology.md))
casse **Target C**, annoncée protégée contre le VCC FI : *« As far as the authors know, this
target was not known to be vulnerable to VCC FI attack before »*. Clé du succès : cibler
spécifiquement la zone de verdict **CHANGING** (deux mesures identiques donnant des verdicts
différents — signature de proximité de la frontière de décision) et **répéter 3× chaque
mesure** pour absorber le jitter d'horloge interne.

⚠️ Sur **Target B**, aucune des 4 stratégies comparées n'a produit de succès — un
échec de recherche ne prouve donc pas l'absence de vulnérabilité, seulement l'insuffisance
du budget de mesures alloué à cette carte précise.

## 3. Portabilité — ce qui se transfère d'un exemplaire à l'autre

★ **Règle de portabilité mesurée** : les paramètres de **forme** (tension, longueur de
glitch) sont **les mêmes d'un exemplaire à l'autre** du même composant — réutilisables tels
quels sur un nouveau lot. **Les paramètres temporels (offset, délai), non** — à recalibrer à
chaque nouvel exemplaire, y compris de la même référence. C'est la règle qui décide ce qu'il
faut re-caractériser en changeant de carte au sein d'un même modèle.

## 4. Ce que le corpus ne couvre pas ici

Aucun détail sur le matériel de glitching employé (modèle d'instrument, seulement une
précision d'offset de 2 ns mentionnée). Aucune identité de fabricant pour les Targets B/C.
Pas de cas de carte à puce paiement (EMV) documenté dans ce corpus — seulement des cartes
JavaCard génériques et une carte de formation Riscure.

## Mémoires sécurisées et IC d'authentification — deux cas laser

> Vecteur : **laser**, détaillé dans [`../by-vector/laser-fi.md`](../by-vector/laser-fi.md).

**ATECC508A (Microchip), dans un portefeuille matériel Coldcard Mk2** [corpus, Hériveaux, deck BH USA
2020]. La puce sert de **mémoire sécurisée** à côté d'un **STM32L4** et stocke le *seed* (clé privée),
protégé par authentification.

★ **Le profil de contre-mesures est l'argument central du vecteur laser** (sl. 4) : surface d'attaque
logicielle réduite · firmware confidentiel · **capteurs de glitch de tension** · **bouclier
top-metal** · **générateur d'horloge interne** — **et *« No laser counter-measures »***.
**Une cible durcie contre le voltage FI peut rester nue face au laser.**

Cible logique : le bit **`is_secret`** de la configuration du slot PIN1 — la commande `ReadMemory`
renvoie `EXECUTION_ERROR` quand il est posé. Résultat : **PIN1 et le *pairing secret* révélés**, ce
qui **donne accès au slot Seed1** ; *« Coldcard Mk2 vulnerable »*, *« realistic attack »* (sl. 68).
Banc : source laser + fibre + objectif **50×** + platine **XYZ** + carte **Scaffold** (open-source).
⚠️ **Coût de campagne** : **343 617 injections sans succès**, puis succès en **2 minutes** après
re-caractérisation (sl. 62, 68) ; et *« Did we killed chips? Yes! »* (sl. 69). La puce a depuis été
remplacée par l'**ATECC608A**.

**IC d'authentification bas coût à logique câblée** [corpus, Skorobogatov, PAINE 2020] — le type
employé contre la contrefaçon de consommables (cartouches, batteries), **sans microprocesseur**.
★ **La surface d'attaque est l'ECC de la NVM** : les codes correcteurs des blocs NVM et leur logique
de contrôle rendent l'application vulnérable à une **terminaison précoce de l'écriture**, jusqu'à
**ramener le niveau de sécurité matériel au mode test/debug d'usine** en contournant la machine à
états. S'y ajoute une **FI optique** classique (1064 nm, > 40 mW, face arrière déprocessée).
⚠️ Les auteurs préviennent que des **dispositifs plus sophistiqués (médical, bancaire)** pourraient
être vulnérables de la même façon.
