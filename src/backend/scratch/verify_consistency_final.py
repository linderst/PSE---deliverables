
import sys
import os

# Add src/backend to path
sys.path.append(os.path.join(os.getcwd(), 'src', 'backend'))

from dependencies import search_service

def test_consistency(q, iterations=3):
    print(f"\n--- Testing Consistency for: '{q}' ---")
    results_list = []
    
    for i in range(iterations):
        print(f"Iteration {i+1}...")
        response = search_service.perform_refined_search(q)
        codes = [r.code for r in response.results]
        top_score = response.results[0].score if response.results else 0
        results_list.append((codes, top_score))
        print(f"  Codes: {codes}")
        print(f"  Top Score: {top_score}")

    # Check consistency
    first_codes = results_list[0][0]
    is_consistent = all(res[0] == first_codes for res in results_list)
    print(f"\nConsistency Check: {'PASS' if is_consistent else 'FAIL'}")
    
    # Check score cap
    is_capped = all(res[1] <= 0.801 for res in results_list) # allowing small float margin
    print(f"Score Cap (<= 0.80) Check: {'PASS' if is_capped else 'FAIL'}")

def test_normalization():
    print(f"\n--- Testing Normalization ---")
    q1 = "Kopfschmerz mit Fieber"
    q2 = " kopfschmerz mit fieber "
    
    print(f"Query 1: '{q1}'")
    res1 = search_service.perform_refined_search(q1)
    codes1 = [r.code for r in res1.results]
    
    print(f"Query 2: '{q2}'")
    res2 = search_service.perform_refined_search(q2)
    codes2 = [r.code for r in res2.results]
    
    is_same = codes1 == codes2
    print(f"Normalization Check: {'PASS' if is_same else 'FAIL'}")

if __name__ == "__main__":
    query = "kopfschmerz mit fieber"
    test_consistency(query)
    test_normalization()
