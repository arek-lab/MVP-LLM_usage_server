from app.graph.state import State, AdditionalInfoHumanFeedback


def ask_additional_info(state: State) -> AdditionalInfoHumanFeedback:
    print(
        f"Ogólan ocena dopasowania CV do oferty: {state['comparison_result'].overall_fit_score}/10."
    )
    
    print(80*"*")
    additional_info = ''
    suggested_additions = getattr(state["comparison_result"], "suggested_additions", None)
    if suggested_additions:
        print("Sugestie do uzupełnień:", suggested_additions)
        additional_info = input("Odopowiedz na powyższe pytania. Jeżeli nie masz uzupełenień naciśnij enter: \n")
    else:
        print("Brak sugestii do uzupełnień.")

    
    print(80*"*")
    removal_acceptance = ''
    suggested_removals = getattr(state["comparison_result"], "suggested_removals", None)
    if suggested_removals:
        print(f"Informacje nierelewantne do oferty:\n\n{suggested_removals}")
        while removal_acceptance not in ("t", "n"):
            removal_acceptance = input("Czy chcesz usunąć z CV powyższe informacje (T/N):\n").lower()
    else:
        print("Brak sugestii do usunięcia.")
        
    if removal_acceptance == "t":
        removal_acceptance = True
    elif removal_acceptance == 'n': 
        removal_acceptance = False
    # else: # inna opcja do wykorzystania zamiast while
    #     additional_info += f'Dodatkowe informacje od usera, które pojawiły się w sekcji akceptacji usuwania inforamcji nierelewantnych. Do wykorzystania o ile wnoszą coś istotnego:\n{removal_acceptance}'
    
    return AdditionalInfoHumanFeedback(
        additional_info=additional_info,
        removal_acceptance=removal_acceptance)