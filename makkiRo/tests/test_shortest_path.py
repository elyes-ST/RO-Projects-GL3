"""
═══════════════════════════════════════════════════════════════════════════════
MODULE DE TESTS - Chemin le moins cher avec checkpoint
═══════════════════════════════════════════════════════════════════════════════

Ce module contient plusieurs cas de test pour valider le modèle d'optimisation.
Exécuter: python -m pytest tests/test_shortest_path.py -v
Ou simplement: python tests/test_shortest_path.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.shortest_path import solve_shortest_path


def test_cas_simple():
    """
    Test basique: A->B->C->D avec checkpoints B,C
    Solution attendue: A->B->C->D (coût: 6)
    """
    print("\n" + "="*70)
    print("TEST 1: Cas simple linéaire")
    print("="*70)
    
    nodes = ['A', 'B', 'C', 'D']
    edges = [
        ('A', 'B', 2),
        ('B', 'C', 2),
        ('C', 'D', 2),
        ('A', 'D', 10)  # Chemin direct plus cher
    ]
    source = 'A'
    target = 'D'
    checkpoints = ['B', 'C']
    
    obj, chosen, details = solve_shortest_path(nodes, edges, source, target, checkpoints)
    
    print(f"✓ Coût optimal: {obj}")
    print(f"✓ Arêtes: {chosen}")
    print(f"✓ Checkpoints visités: {details['visited_checkpoints']}")
    
    assert obj == 6, f"Attendu: 6, obtenu: {obj}"
    assert len(chosen) == 3, f"Attendu 3 arêtes, obtenu {len(chosen)}"
    assert len(details['visited_checkpoints']) >= 1, "Au moins un checkpoint doit être visité"
    
    print("✓ TEST 1 RÉUSSI\n")


def test_chemin_alternatif():
    """
    Test avec choix entre plusieurs chemins
    """
    print("="*70)
    print("TEST 2: Choix entre plusieurs chemins")
    print("="*70)
    
    nodes = ['A', 'B', 'C', 'D', 'E']
    edges = [
        ('A', 'B', 1),
        ('B', 'D', 1),   # Chemin court mais ne passe pas par checkpoint
        ('A', 'C', 2),
        ('C', 'E', 2),
        ('E', 'D', 1),   # Ce chemin passe par E (checkpoint)
    ]
    source = 'A'
    target = 'D'
    checkpoints = ['C', 'E']  # Doit passer par C ou E
    
    obj, chosen, details = solve_shortest_path(nodes, edges, source, target, checkpoints)
    
    print(f"✓ Coût optimal: {obj}")
    print(f"✓ Arêtes: {chosen}")
    print(f"✓ Checkpoints visités: {details['visited_checkpoints']}")
    
    assert obj <= 6, f"Coût trop élevé: {obj}"
    assert len(details['visited_checkpoints']) >= 1
    
    print("✓ TEST 2 RÉUSSI\n")


def test_graphe_complexe():
    """
    Test sur un graphe plus complexe avec plusieurs options
    """
    print("="*70)
    print("TEST 3: Graphe complexe")
    print("="*70)
    
    nodes = ['A', 'B', 'C', 'D', 'E', 'F']
    edges = [
        ('A', 'B', 5),
        ('A', 'C', 3),
        ('B', 'D', 2),
        ('C', 'D', 4),
        ('C', 'E', 2),
        ('D', 'F', 3),
        ('E', 'F', 2),
        ('A', 'F', 20),  # Chemin direct très cher
    ]
    source = 'A'
    target = 'F'
    checkpoints = ['B', 'E']
    
    obj, chosen, details = solve_shortest_path(nodes, edges, source, target, checkpoints)
    
    print(f"✓ Coût optimal: {obj}")
    print(f"✓ Nombre d'arêtes: {len(chosen)}")
    print(f"✓ Chemin: {' → '.join([f'{u}' for u, v, c in chosen] + [chosen[-1][1]])}")
    print(f"✓ Checkpoints visités: {details['visited_checkpoints']}")
    print(f"✓ Temps de résolution: {details['solve_time']:.3f}s")
    
    assert obj < 20, "La solution doit être meilleure que le chemin direct"
    assert len(details['visited_checkpoints']) >= 1
    
    print("✓ TEST 3 RÉUSSI\n")


def test_validation_erreurs():
    """
    Test des validations d'erreur
    """
    print("="*70)
    print("TEST 4: Validation des erreurs")
    print("="*70)
    
    nodes = ['A', 'B', 'C']
    edges = [('A', 'B', 1), ('B', 'C', 1)]
    
    # Test 1: Source invalide
    try:
        solve_shortest_path(nodes, edges, 'X', 'C', ['B'])
        assert False, "Devrait lever une ValueError"
    except ValueError as e:
        print(f"✓ Erreur source invalide détectée: {e}")
    
    # Test 2: Cible invalide
    try:
        solve_shortest_path(nodes, edges, 'A', 'Z', ['B'])
        assert False, "Devrait lever une ValueError"
    except ValueError as e:
        print(f"✓ Erreur cible invalide détectée: {e}")
    
    # Test 3: Source = Cible
    try:
        solve_shortest_path(nodes, edges, 'A', 'A', ['B'])
        assert False, "Devrait lever une ValueError"
    except ValueError as e:
        print(f"✓ Erreur source=cible détectée: {e}")
    
    # Test 4: Pas de checkpoint valide
    try:
        solve_shortest_path(nodes, edges, 'A', 'C', ['X', 'Y'])
        assert False, "Devrait lever une ValueError"
    except ValueError as e:
        print(f"✓ Erreur checkpoints invalides détectée: {e}")
    
    print("✓ TEST 4 RÉUSSI\n")


def test_graphe_deconnecte():
    """
    Test avec un graphe déconnecté (doit être infaisable)
    """
    print("="*70)
    print("TEST 5: Graphe déconnecté")
    print("="*70)
    
    nodes = ['A', 'B', 'C', 'D']
    edges = [
        ('A', 'B', 1),
        ('C', 'D', 1),  # Composante séparée
    ]
    source = 'A'
    target = 'D'
    checkpoints = ['B']
    
    try:
        solve_shortest_path(nodes, edges, source, target, checkpoints)
        assert False, "Devrait lever une RuntimeError (infaisable)"
    except RuntimeError as e:
        print(f"✓ Infaisabilité détectée correctement: {e}")
    
    print("✓ TEST 5 RÉUSSI\n")


def test_un_seul_checkpoint():
    """
    Test avec un seul checkpoint disponible
    """
    print("="*70)
    print("TEST 6: Un seul checkpoint")
    print("="*70)
    
    nodes = ['A', 'B', 'C']
    edges = [
        ('A', 'B', 3),
        ('B', 'C', 2),
        ('A', 'C', 10),
    ]
    source = 'A'
    target = 'C'
    checkpoints = ['B']  # Un seul checkpoint
    
    obj, chosen, details = solve_shortest_path(nodes, edges, source, target, checkpoints)
    
    print(f"✓ Coût optimal: {obj}")
    print(f"✓ Checkpoints visités: {details['visited_checkpoints']}")
    
    assert 'B' in details['visited_checkpoints'], "B doit être visité"
    assert obj == 5, f"Attendu: 5, obtenu: {obj}"
    
    print("✓ TEST 6 RÉUSSI\n")


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "SUITE DE TESTS - VALIDATION COMPLÈTE" + " "*16 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_cas_simple,
        test_chemin_alternatif,
        test_graphe_complexe,
        test_validation_erreurs,
        test_graphe_deconnecte,
        test_un_seul_checkpoint,
    ]
    
    failed = 0
    for i, test in enumerate(tests, 1):
        try:
            test()
        except AssertionError as e:
            print(f"✗ TEST {i} ÉCHOUÉ: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ TEST {i} ERREUR: {e}\n")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RÉSULTAT: {len(tests) - failed}/{len(tests)} tests réussis")
    if failed == 0:
        print("✓ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
    else:
        print(f"✗ {failed} test(s) ont échoué")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
