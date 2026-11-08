import random
from bisect import bisect_right
from itertools import product
from statistics import mean

CAPACITES = (20, 15, 35, 40, 15, 15, 10)
DEMANDES = (80, 90, 65, 70)
DUREES = (2, 2, 1, 1, 1, 1, 1)
NB_UNITES = len(CAPACITES)
NB_INTERVALLES = len(DEMANDES)
CAPACITE_TOTALE = sum(CAPACITES)


def construire_motifs(duree):
    return [tuple(1 if debut <= t < debut + duree else 0 for t in range(NB_INTERVALLES))
            for debut in range(NB_INTERVALLES - duree + 1)]


MOTIFS = [construire_motifs(d) for d in DUREES]


def bits(gene):
    return "".join(str(b) for b in gene)


def chromosome(individu):
    return " ".join(bits(g) for g in individu)


def individu_aleatoire():
    return [random.choice(MOTIFS[u]) for u in range(NB_UNITES)]


def population_initiale(taille):
    return [individu_aleatoire() for _ in range(taille)]


def pertes(individu):
    return [sum(individu[u][t] * CAPACITES[u] for u in range(NB_UNITES))
            for t in range(NB_INTERVALLES)]


def reserves(individu):
    p = pertes(individu)
    return [CAPACITE_TOTALE - p[t] - DEMANDES[t] for t in range(NB_INTERVALLES)]


def fitness(individu):
    return max(0, min(reserves(individu)))


def est_realisable(individu):
    for u in range(NB_UNITES):
        if individu[u] not in MOTIFS[u]:
            return False
    return True


def probabilites_loterie(scores):
    total = sum(scores)
    if total <= 0:
        return [1.0 / len(scores)] * len(scores)
    return [s / total for s in scores]


def selection_loterie(population, scores, nombre):
    probas = probabilites_loterie(scores)
    cumul = []
    somme = 0.0
    for p in probas:
        somme += p
        cumul.append(somme)
    cumul[-1] = 1.0
    return [population[bisect_right(cumul, random.random())][:] for _ in range(nombre)]


def croisement(parent1, parent2, pc):
    if random.random() > pc:
        return parent1[:], parent2[:]
    point = random.randint(1, NB_UNITES - 1)
    enfant1 = parent1[:point] + parent2[point:]
    enfant2 = parent2[:point] + parent1[point:]
    return enfant1, enfant2


def mutation_inversion(individu, pm):
    resultat = individu[:]
    for u in range(NB_UNITES):
        if random.random() < pm:
            resultat[u] = tuple(reversed(resultat[u]))
    return resultat


def mutation_aleatoire(individu, pm):
    resultat = individu[:]
    for u in range(NB_UNITES):
        if random.random() < pm:
            resultat[u] = random.choice(MOTIFS[u])
    return resultat


def mutation_echange(individu, pm):
    resultat = individu[:]
    if random.random() < pm:
        groupes = {}
        for u in range(NB_UNITES):
            groupes.setdefault(DUREES[u], []).append(u)
        candidats = [g for g in groupes.values() if len(g) > 1]
        if candidats:
            groupe = random.choice(candidats)
            i, j = random.sample(groupe, 2)
            resultat[i], resultat[j] = resultat[j], resultat[i]
    return resultat


MUTATIONS = {
    "inversion": mutation_inversion,
    "aleatoire": mutation_aleatoire,
    "echange": mutation_echange,
}


def algorithme_genetique(taille=49, generations=200, pc=0.85, pm=0.10,
                         mutation="inversion", elite=2, graine=None,
                         patience=60, cible=None):
    if graine is not None:
        random.seed(graine)
    operateur = MUTATIONS[mutation]
    population = population_initiale(taille)
    scores = [fitness(ind) for ind in population]
    indice_max = max(range(taille), key=lambda i: scores[i])
    meilleur = population[indice_max][:]
    meilleur_score = scores[indice_max]
    generation_optimum = 0
    historique = [meilleur_score]
    stagnation = 0

    for generation in range(1, generations + 1):
        classement = sorted(range(taille), key=lambda i: scores[i], reverse=True)
        nouvelle = [population[i][:] for i in classement[:elite]]
        while len(nouvelle) < taille:
            p1, p2 = selection_loterie(population, scores, 2)
            e1, e2 = croisement(p1, p2, pc)
            nouvelle.append(operateur(e1, pm))
            if len(nouvelle) < taille:
                nouvelle.append(operateur(e2, pm))
        population = nouvelle
        scores = [fitness(ind) for ind in population]
        indice_max = max(range(taille), key=lambda i: scores[i])
        if scores[indice_max] > meilleur_score:
            meilleur_score = scores[indice_max]
            meilleur = population[indice_max][:]
            generation_optimum = generation
            stagnation = 0
        else:
            stagnation += 1
        historique.append(meilleur_score)
        if cible is not None and meilleur_score >= cible:
            break
        if patience is not None and stagnation >= patience:
            break

    return {
        "individu": meilleur,
        "score": meilleur_score,
        "reserves": reserves(meilleur),
        "historique": historique,
        "generation": generation_optimum,
        "evaluations": taille * (len(historique)),
        "realisable": est_realisable(meilleur),
    }


def afficher_solution(individu, titre="Solution"):
    print("=" * 68)
    print(titre)
    print("=" * 68)
    print("Chromosome : " + chromosome(individu))
    print("Fitness    : " + str(fitness(individu)) + " MW")
    print("-" * 68)
    print("Unite  Cap(MW)  Duree  " + "  ".join("I" + str(t + 1) for t in range(NB_INTERVALLES)) + "   Gene")
    for u in range(NB_UNITES):
        etats = "   ".join("X" if individu[u][t] else "." for t in range(NB_INTERVALLES))
        print("{:<6} {:<8} {:<6} {}   {}".format(u + 1, CAPACITES[u], DUREES[u], etats, bits(individu[u])))
    print("-" * 68)
    p = pertes(individu)
    r = reserves(individu)
    print("Intervalle      " + "".join("{:>10}".format(t + 1) for t in range(NB_INTERVALLES)))
    print("Demande (MW)    " + "".join("{:>10}".format(DEMANDES[t]) for t in range(NB_INTERVALLES)))
    print("Perte (MW)      " + "".join("{:>10}".format(p[t]) for t in range(NB_INTERVALLES)))
    print("Reserve (MW)    " + "".join("{:>10}".format(r[t]) for t in range(NB_INTERVALLES)))
    print("Reserve min = {} MW".format(min(r)))
    print()


def optimum_exhaustif():
    meilleur_score = -1
    meilleur = None
    for combinaison in product(*MOTIFS):
        individu = list(combinaison)
        score = fitness(individu)
        if score > meilleur_score:
            meilleur_score = score
            meilleur = individu
    return meilleur_score, meilleur


def comparer_mutations(repetitions=20, cible=25, taille=49, generations=200, pc=0.85, pm=0.10):
    print("=" * 78)
    print("Comparaison des operateurs de mutation (selection par loterie)")
    print("=" * 78)
    print("{:<12} {:>10} {:>10} {:>10} {:>12} {:>12}".format(
        "Mutation", "Moyenne", "Meilleur", "Succes%", "Gen.moy", "Eval.moy"))
    resultats = {}
    for nom in MUTATIONS:
        scores = []
        generations_atteintes = []
        evaluations = []
        succes = 0
        for essai in range(repetitions):
            run = algorithme_genetique(taille=taille, generations=generations, pc=pc, pm=pm,
                                       mutation=nom, graine=1000 + essai, patience=60)
            scores.append(run["score"])
            generations_atteintes.append(run["generation"])
            evaluations.append(run["evaluations"])
            if run["score"] >= cible:
                succes += 1
        resultats[nom] = scores
        print("{:<12} {:>10.2f} {:>10} {:>10.1f} {:>12.1f} {:>12.0f}".format(
            nom, mean(scores), max(scores), 100.0 * succes / repetitions,
            mean(generations_atteintes), mean(evaluations)))
    print()
    return resultats


def etude_parametres(repetitions=10, cible=25):
    print("=" * 78)
    print("Etude de sensibilite (pc, pm) avec mutation par inversion")
    print("=" * 78)
    print("{:>6} {:>6} {:>12} {:>12}".format("pc", "pm", "Moyenne", "Succes%"))
    for pc in (0.6, 0.8, 1.0):
        for pm in (0.02, 0.05, 0.10, 0.25):
            scores = []
            for essai in range(repetitions):
                run = algorithme_genetique(pc=pc, pm=pm, mutation="inversion",
                                           graine=2000 + essai, patience=60)
                scores.append(run["score"])
            succes = 100.0 * sum(1 for s in scores if s >= cible) / repetitions
            print("{:>6.2f} {:>6.2f} {:>12.2f} {:>12.1f}".format(pc, pm, mean(scores), succes))
    print()


def afficher_convergence(historique, pas=5):
    print("Convergence (meilleur fitness par generation)")
    for g in range(0, len(historique), pas):
        print("gen {:>4} : {:>3} {}".format(g, historique[g], "#" * historique[g]))
    print()


def verifier_exemple_du_cours():
    individu = [(0, 1, 1, 0), (0, 0, 1, 1), (0, 0, 0, 1), (1, 0, 0, 0),
                (0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0)]
    attendu_pertes = [50, 35, 50, 50]
    attendu_reserves = [20, 25, 35, 30]
    assert pertes(individu) == attendu_pertes
    assert reserves(individu) == attendu_reserves
    assert fitness(individu) == 20
    afficher_solution(individu, "Verification : exemple du cours (fitness attendue = 20)")


if __name__ == "__main__":
    print("Capacite totale = {} MW | Espace de recherche = {} solutions".format(
        CAPACITE_TOTALE, 3 * 3 * 4 ** 5))
    print()

    verifier_exemple_du_cours()

    score_opt, solution_opt = optimum_exhaustif()
    afficher_solution(solution_opt, "Optimum global par enumeration exhaustive")

    run = algorithme_genetique(taille=49, generations=200, pc=0.85, pm=0.10,
                               mutation="inversion", graine=7, patience=60)
    afficher_solution(run["individu"], "AG : selection loterie + croisement par blocs + inversion")
    print("Generation de trouvaille : {}".format(run["generation"]))
    print("Solution realisable      : {}".format(run["realisable"]))
    print("Ecart a l'optimum        : {} MW".format(score_opt - run["score"]))
    print()
    afficher_convergence(run["historique"])

    comparer_mutations(repetitions=20, cible=score_opt)
    etude_parametres(repetitions=10, cible=score_opt)