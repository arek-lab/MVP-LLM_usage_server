# tests/test_rewrite_chain.py

import pytest
from chains.rewrite_flow.chain import get_rewrite_chain
from chains.model import LLMResponseModel


def test_rewrite_chain_formal_to_informal():
    """Test przepisania tekstu z formalnego na nieformalny"""
    content = "Uprzejmie informuję, że Pana wniosek został przyjęty do rozpatrzenia."
    
    chain = get_rewrite_chain(
        subcategory="formal_to_informal",
        content=content
    )
    
    result = chain.invoke({})
    
    # Assertions
    assert isinstance(result, LLMResponseModel)
    assert result.text != content  # Tekst powinien się zmienić
    assert len(result.text) > 0
    assert result.confidence is None or (0 <= result.confidence <= 1)
    print(f"Original: {content}")
    print(f"Rewritten: {result.text}")
    print(f"Confidence: {result.confidence}")


def test_rewrite_chain_improve_clarity():
    """Test poprawy czytelności tekstu"""
    content = """Wdrożenie nowego systemu, który był rozwijany przez kilka miesięcy 
    przez nasz zespół we współpracy z zewnętrznymi konsultantami, będzie realizowane 
    etapami począwszy od przyszłego kwartału."""
    
    chain = get_rewrite_chain(
        subcategory="improve_clarity",
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content



def test_rewrite_chain_with_audience():
    """Test adaptacji do odbiorcy"""
    content = "Nasza aplikacja wykorzystuje zaawansowane algorytmy ML do optymalizacji."
    
    chain = get_rewrite_chain(
        subcategory="audience_adaptation",
        content=content,
        target_audience="ogół społeczeństwa bez wiedzy technicznej"
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content
    assert "ML" not in result.text or "machine learning" in result.text.lower()  # Powinno wyjaśnić skrót


def test_rewrite_chain_platform_adaptation():
    """Test adaptacji do platformy"""
    content = """Szanowni Państwo, w załączeniu przesyłam raport kwartalny. 
    Proszę o zapoznanie się z dokumentem i przekazanie uwag."""
    
    chain = get_rewrite_chain(
        subcategory="platform_adaptation",
        content=content,
        target_platform="LinkedIn"
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content
    assert len(result.text) < len(content) * 1.5  # LinkedIn preferuje krótsze teksty


def test_rewrite_chain_fallback_general():
    """Test fallback do ogólnego rewrite gdy subcategory nieznana"""
    content = "Ten tekst wymaga poprawy."
    
    chain = get_rewrite_chain(
        subcategory="nieistniejaca_kategoria",
        content=content
    )
    
    result = chain.invoke({})
    
    # Powinno użyć fallback do "general"
    assert isinstance(result, LLMResponseModel)
    assert result.text != content


@pytest.mark.parametrize("subcategory", [
    "formal_to_informal",
    "informal_to_formal",
    "improve_clarity",
    "creative_rephrase",
    "make_persuasive"
])
def test_all_subcategories(subcategory):
    """Test wszystkich głównych podkategorii"""
    content = "To jest testowy tekst do przepisania w różnych stylach."
    
    chain = get_rewrite_chain(
        subcategory=subcategory,
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text
  