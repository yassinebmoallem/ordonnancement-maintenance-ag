# Ordonnancement de la maintenance par algorithme génétique

## Présentation

Ce projet résout un problème d’ordonnancement de la maintenance de sept unités de production électrique sur quatre intervalles.

L’objectif est de planifier les périodes de maintenance afin de maximiser la réserve minimale de puissance disponible pendant l’ensemble des intervalles.

Le programme utilise un algorithme génétique, puis vérifie le meilleur résultat avec une énumération exhaustive de toutes les solutions possibles.

## Données du problème

### Unités de production

| Unité | Capacité | Durée de maintenance |
|---:|---:|---:|
| 1 | 20 MW | 2 intervalles |
| 2 | 15 MW | 2 intervalles |
| 3 | 35 MW | 1 intervalle |
| 4 | 40 MW | 1 intervalle |
| 5 | 15 MW | 1 intervalle |
| 6 | 15 MW | 1 intervalle |
| 7 | 10 MW | 1 intervalle |

La capacité totale disponible est de **150 MW**.

### Demande par intervalle

| Intervalle | Demande |
|---:|---:|
| 1 | 80 MW |
| 2 | 90 MW |
| 3 | 65 MW |
| 4 | 70 MW |

## Représentation d’une solution

Chaque unité est représentée par un gène binaire de quatre bits.

- `1` indique que l’unité est en maintenance.
- `0` indique que l’unité est disponible.

Exemples :

- `1100` : maintenance pendant les intervalles 1 et 2.
- `0110` : maintenance pendant les intervalles 2 et 3.
- `0010` : maintenance pendant l’intervalle 3.

Un chromosome complet contient les sept gènes des sept unités.

```text
1100 1100 0010 0001 0010 0001 1000
```

## Fonction d’évaluation

Pour chaque intervalle, la réserve est calculée avec la formule suivante :

```text
Réserve = Capacité totale - Puissance perdue en maintenance - Demande
```

La fitness d’un chromosome correspond à sa plus petite réserve parmi les quatre intervalles.

```text
Fitness = max(0, min(réserves))
```

Une réserve négative donne une fitness égale à zéro.

## Algorithme génétique

Le programme applique les étapes suivantes :

1. Génération aléatoire d’une population initiale.
2. Calcul de la fitness de chaque individu.
3. Conservation des meilleurs individus par élitisme.
4. Sélection des parents par loterie.
5. Croisement des chromosomes entre deux blocs représentant des unités.
6. Mutation des enfants.
7. Création d’une nouvelle population.
8. Répétition jusqu’à la limite de générations, la stagnation ou l’atteinte de la cible.

### Paramètres par défaut

| Paramètre | Valeur |
|---|---:|
| Taille de la population | 49 |
| Nombre maximal de générations | 200 |
| Probabilité de croisement | 0,85 |
| Probabilité de mutation | 0,10 |
| Nombre d’élites | 2 |
| Patience | 60 générations |

## Opérateurs de mutation

Le programme compare trois opérateurs :

- **Inversion** : inverse les bits d’un gène sélectionné.
- **Aléatoire** : remplace un gène par un motif valide choisi aléatoirement.
- **Échange** : échange les gènes de deux unités ayant la même durée de maintenance.

Toutes les opérations conservent la structure des blocs de quatre bits.

## Structure du projet

```text
ordonnancement-maintenance-ag/
├── main.py
└── README.md
```

## Prérequis

- Python 3.10 ou une version plus récente
- Aucune bibliothèque externe

Le programme utilise uniquement les modules standards suivants :

- `random`
- `bisect`
- `itertools`
- `statistics`

## Exécution

Ouvrir un terminal dans le dossier du projet, puis exécuter :

```powershell
python main.py
```

## Résultats obtenus

L’espace de recherche contient **9 216 solutions**.

L’énumération exhaustive trouve une fitness optimale de **25 MW** avec le chromosome suivant :

```text
1100 1100 0010 0001 0010 0001 1000
```

Réserves obtenues :

| Intervalle | Perte | Demande | Réserve |
|---:|---:|---:|---:|
| 1 | 45 MW | 80 MW | 25 MW |
| 2 | 35 MW | 90 MW | 25 MW |
| 3 | 50 MW | 65 MW | 35 MW |
| 4 | 55 MW | 70 MW | 25 MW |

Avec la graine `7`, l’algorithme génétique trouve également une fitness de **25 MW** à la génération **2** :

```text
1100 1100 0001 0010 0001 0010 1000
```

La solution est réalisable et son écart par rapport à l’optimum global est de **0 MW**.

## Comparaison des mutations

Résultats obtenus sur 20 exécutions :

| Mutation | Fitness moyenne | Meilleure fitness | Taux de succès | Génération moyenne | Évaluations moyennes |
|---|---:|---:|---:|---:|---:|
| Inversion | 25,00 | 25 | 100 % | 1,4 | 3 060 |
| Aléatoire | 24,50 | 25 | 90 % | 1,3 | 3 053 |
| Échange | 25,00 | 25 | 100 % | 3,3 | 3 151 |

La mutation par inversion et la mutation par échange atteignent l’optimum dans 100 % des essais. La mutation par inversion atteint cependant l’optimum avec moins de générations et moins d’évaluations en moyenne que la mutation par échange.

## Étude des paramètres

L’étude de sensibilité teste les valeurs suivantes :

- Probabilité de croisement : `0.60`, `0.80` et `1.00`
- Probabilité de mutation : `0.02`, `0.05`, `0.10` et `0.25`

La majorité des configurations atteignent un taux de succès de **100 %**. Les résultats montrent que la configuration `pc = 0.85` et `pm = 0.10` constitue un choix efficace pour ce problème.

## Conclusion

L’algorithme génétique trouve une solution optimale avec une réserve minimale de **25 MW**. Le résultat est confirmé par l’énumération exhaustive. Le croisement par blocs et les mutations proposées permettent de conserver des calendriers de maintenance valides pendant toute l’exécution.

## Auteur

**Yassine Ben Maalem**
