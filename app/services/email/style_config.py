from pydantic import BaseModel, Field
from enum import Enum

class ToneStyle(str, Enum):
    """Ton komunikacji w mailu"""
    FORMAL = "formal"  # Oficjalny, dystyngowany - do instytucji i wyższej kadry
    BUSINESS_PROFESSIONAL = "business_professional"  # Profesjonalny - standardowa komunikacja B2B
    FRIENDLY_WARM = "friendly_warm"  # Przyjazny, ciepły - budowanie relacji z klientami
    NEUTRAL = "neutral"  # Neutralny - uniwersalny do większości sytuacji
    ASSERTIVE = "assertive"  # Asertywny - reklamacje, windykacja, pilne sprawy

class LengthStyle(str, Enum):
    """Długość i szczegółowość maila"""
    CONCISE = "concise"  # Zwięzły, lakoniczny - krótkie wiadomości do punktu
    DETAILED = "detailed"  # Rozbudowany, szczegółowy - z pełnym kontekstem
    BULLET_POINTS = "bullet_points"  # Punktowy - z wyraźnymi listami i strukturą

class PurposeStyle(str, Enum):
    """Cel biznesowy maila"""
    SALES = "sales"  # Sprzedażowy - prezentacja oferty, cold mailing
    FOLLOW_UP = "follow_up"  # Followup - przypomnienia, kontynuacja wątku
    INFORMATIONAL = "informational"  # Informacyjny - komunikaty, aktualizacje
    REQUEST_INQUIRY = "request_inquiry"  # Prośba/zapytanie - pytanie o informacje
    THANK_YOU = "thank_you"  # Podziękowania - wyrażenie wdzięczności
    APOLOGY = "apology"  # Przeprosiny - handling reklamacji i problemów
    NEGOTIATION = "negotiation"  # Negocjacyjny - ustalanie warunków współpracy
    NETWORKING = "networking"  # Networkingowy - nawiązywanie kontaktów biznesowych

class IndustryStyle(str, Enum):
    """Branża/kontekst biznesowy"""
    CORPORATE = "corporate"  # Korporacyjny - dla dużych organizacji
    STARTUP = "startup"  # Startupowy - swobodny, nowoczesny
    CREATIVE = "creative"  # Kreatywny - dla branży kreatywnej, marketingu
    TECHNICAL = "technical"  # Techniczny - z żargonem branżowym IT
    LEGAL = "legal"  # Prawniczy - precyzyjny, z klauzulami

class EmailStyleConfig(BaseModel):
    """Konfiguracja stylu generowanego maila"""
    tone: ToneStyle = Field(
        description="Ton komunikacji w mailu"
    )
    length: LengthStyle = Field(
        description="Długość i poziom szczegółowości"
    )
    purpose: PurposeStyle = Field(
        description="Główny cel biznesowy maila"
    )
    industry: IndustryStyle = Field(
        description="Kontekst branżowy komunikacji"
    )
    
    class Config:
        use_enum_values = True