from app.text_crafter.state import State, QualityCheckResult
import re

def quality_check(state: State) -> State:
    """
    Sprawdza podstawową jakość przepisanego tekstu.
    """
    original = state['original_text']
    rewritten = state['result'].text
    confidence = state['result'].confidence
    
    issues = []
    suggestions = []
    score = 1.0
    
    # 1. Czy tekst nie jest pusty/za krótki
    if len(rewritten.strip()) < 10:
        issues.append("Tekst jest zbyt krótki")
        score -= 0.5
    
    # 2. Czy nie straciliśmy kluczowych informacji
    # Proste heurystyki: liczby, daty, nazwy własne
       
    # Sprawdź liczby
    original_numbers = set(re.findall(r'\d+', original))
    rewritten_numbers = set(re.findall(r'\d+', rewritten))
    if original_numbers and not rewritten_numbers.issubset(original_numbers):
        issues.append("Możliwa utrata ważnych liczb/dat")
        score -= 0.2
    
    # 3. Sprawdź długość - czy nie jest za bardzo rozdęta
    length_ratio = len(rewritten) / len(original) if len(original) > 0 else 1
    if length_ratio > 2.0:
        suggestions.append("Tekst został znacznie wydłużony (może być zbyt rozwlekły)")
    elif length_ratio < 0.5:
        issues.append("Tekst został bardzo skrócony (możliwa utrata informacji)")
        score -= 0.1
    
    # 4. Sprawdź confidence z LLM
    if confidence < 0.7:
        suggestions.append(f"Model miał niską pewność ({confidence:.1%}) - warto zweryfikować")
    
  
    quality_result = QualityCheckResult(
        passed=len(issues) == 0,
        score=max(0.0, min(1.0, score)),
        issues=issues,
        suggestions=suggestions
    )
    
    # Aktualizuj stan
    state['quality_result'] = quality_result
    
    # Jeśli są krytyczne problemy, możesz ustawić flagę
    # if not quality_result.passed:
    #     state['needs_review'] = True
    
    return state