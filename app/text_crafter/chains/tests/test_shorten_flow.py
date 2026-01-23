from chains.shorten_flow.chain import get_shorten_chain
from chains.model import LLMResponseModel


def test_shorten_chain_brief_summary():
    """Test tworzenia zwięzłego streszczenia"""
    content = """Wdrożenie nowego systemu, który był rozwijany przez kilka miesięcy 
    przez nasz zespół we współpracy z zewnętrznymi konsultantami, będzie realizowane 
    etapami począwszy od przyszłego kwartału. Proces wdrożenia obejmie szkolenia 
    pracowników, migrację danych oraz stopniowe uruchamianie poszczególnych modułów.
    Przewidujemy, że pełne wdrożenie zajmie około 6 miesięcy."""
    
    chain = get_shorten_chain(
        subcategory="brief_summary",
        content=content
    )
    
    result = chain.invoke({})
    
    # Assertions
    assert isinstance(result, LLMResponseModel)
    assert result.text != content  # Tekst powinien się zmienić
    assert len(result.text) < len(content)  # Powinien być krótszy
    assert len(result.text) > 0
    assert result.confidence is None or (0 <= result.confidence <= 1)
    print(f"Original ({len(content)} chars): {content}")
    print(f"Shortened ({len(result.text)} chars): {result.text}")
    print(f"Confidence: {result.confidence}")
    print(f"Compression ratio: {len(result.text) / len(content):.2f}")


def test_shorten_chain_remove_fluff():
    """Test usuwania zbędnych słów zachowując pełną treść"""
    content = """W zasadzie można powiedzieć, że nasz zespół, który jak wiadomo 
    składa się z doświadczonych specjalistów, pracował nad tym projektem przez, 
    no cóż, dość długi okres czasu. Rezultaty są, że tak powiem, całkiem obiecujące."""
    
    chain = get_shorten_chain(
        subcategory="remove_fluff",
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content
    assert len(result.text) < len(content)
    # Sprawdź czy usunięto wypełniacze
    fluff_phrases = ["w zasadzie", "można powiedzieć", "jak wiadomo", "no cóż", "że tak powiem"]
    assert not any(phrase in result.text.lower() for phrase in fluff_phrases)


def test_shorten_chain_key_points():
    """Test wyciągania kluczowych punktów"""
    content = """Nasza firma osiągnęła w tym roku trzy główne cele. Po pierwsze, 
    zwiększyliśmy przychody o 25% w porównaniu do roku poprzedniego. Po drugie, 
    zredukowaliśmy koszty operacyjne o 15% dzięki optymalizacji procesów. Po trzecie, 
    pozyskaliśmy 50 nowych klientów z segmentu enterprise."""
    
    chain = get_shorten_chain(
        subcategory="key_points",
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content
    # Powinny pozostać liczby i kluczowe fakty
    assert "25%" in result.text or "25" in result.text
    assert "15%" in result.text or "15" in result.text


def test_shorten_chain_executive_summary():
    """Test tworzenia executive summary"""
    content = """Projekt migracji do chmury trwał 8 miesięcy i pochłonął budżet 
    500 000 PLN. Zespół składający się z 12 osób pracował w metodologii Agile, 
    realizując sprint po sprincie. Napotkaliśmy kilka wyzwań technicznych związanych 
    z integracją legacy systemów, ale ostatecznie wszystkie zostały rozwiązane. 
    Obecnie system działa stabilnie, obsługując 10 000 użytkowników dziennie. 
    ROI wyniesie 18 miesięcy."""
    
    chain = get_shorten_chain(
        subcategory="executive_summary",
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert result.text != content
    assert len(result.text) < len(content) * 0.6  # Executive summary powinien być znacznie krótszy
    # Kluczowe liczby powinny pozostać
    assert "500" in result.text or "500000" in result.text  # budżet
    assert "18" in result.text  # ROI


def test_shorten_chain_with_target_length_very_short():
    """Test skracania z określeniem bardzo krótkiej docelowej długości"""
    content = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."""
    
    chain = get_shorten_chain(
        subcategory="remove_fluff",
        content=content,
        target_length="very_short"
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert len(result.text) < len(content) * 0.4  # Powinno być max 30-40% oryginału


def test_shorten_chain_with_target_length_medium():
    """Test skracania z określeniem średniej docelowej długości"""
    content = """To jest dłuższy tekst który zawiera wiele informacji. 
    Chcemy go skrócić, ale nie za bardzo, żeby zachować kontekst i szczegóły. 
    Docelowo powinien mieć około 70% oryginalnej długości."""
    
    chain = get_shorten_chain(
        subcategory="remove_fluff",
        content=content,
        target_length="medium"
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert len(result.text) < len(content)
    assert len(result.text) > len(content) * 0.5  # Nie powinno być za krótkie


def test_shorten_chain_preserve_tone_formal():
    """Test zachowania formalnego tonu"""
    content = """Uprzejmie informuję, że w dniu dzisiejszym odbyło się spotkanie 
    zarządu, podczas którego podjęto decyzję o zwiększeniu budżetu na rozwój 
    produktu o 30%. Decyzja ta wynika z analizy rynku i prognoz wzrostu."""
    
    chain = get_shorten_chain(
        subcategory="remove_fluff",
        content=content,
        preserve_tone=True
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    assert len(result.text) < len(content)
    # Formalny ton powinien być zachowany
    assert not any(word in result.text.lower() for word in ["hej", "cześć", "super"])


def test_shorten_chain_preserve_numbers():
    """Test czy liczby i daty są zachowane"""
    content = """W 2024 roku sprzedaliśmy 15000 jednostek produktu, co dało nam 
    przychód 2.5 miliona złotych. W porównaniu do 2023 roku, gdy sprzedaliśmy 
    12000 jednostek za 2 miliony, to wzrost o 25%."""
    
    chain = get_shorten_chain(
        subcategory="brief_summary",
        content=content
    )
    
    result = chain.invoke({})
    
    assert isinstance(result, LLMResponseModel)
    # Kluczowe liczby powinny pozostać
    assert "15000" in result.text or "15 000" in result.text or "15k" in result.text.lower()
    assert "2024" in result.text


def test_shorten_chain_fallback_general():
    """Test fallback do ogólnego skracania gdy subcategory nieznana"""
    content = "Ten tekst wymaga skrócenia w jakiś sposób."