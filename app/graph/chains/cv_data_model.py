from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "liceum"
    BACHELOR = "licencjat"
    ENGINEER = "inżynier"
    MASTER = "magister"
    PHD = "doktor"
    POSTDOC = "habilitacja"
    OTHER = "inne"


class LanguageProficiency(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    NATIVE = "native"


class ContactInfo(BaseModel):
    """Dane kontaktowe kandydata"""

    email: Optional[EmailStr] = Field(None, description="Adres email")
    phone: Optional[str] = Field(None, description="Numer telefonu")
    linkedin: Optional[str] = Field(None, description="Profil LinkedIn")
    github: Optional[str] = Field(None, description="Profil GitHub")
    portfolio: Optional[str] = Field(None, description="Portfolio/strona WWW")
    location: Optional[str] = Field(None, description="Lokalizacja (miasto, kraj)")


class Education(BaseModel):
    """Pojedynczy wpis edukacyjny"""

    institution: str = Field(..., description="Nazwa uczelni/szkoły")
    degree: Optional[EducationLevel] = Field(None, description="Poziom wykształcenia")
    field_of_study: Optional[str] = Field(None, description="Kierunek studiów")
    start_date: Optional[str] = Field(
        None, description="Data rozpoczęcia (rok lub rok-miesiąc)"
    )
    end_date: Optional[str] = Field(
        None,
        description="Data zakończenia (rok lub rok-miesiąc), 'present' jeśli w trakcie",
    )
    description: Optional[str] = Field(
        None, description="Dodatkowe informacje, osiągnięcia"
    )
    gpa: Optional[str] = Field(None, description="Średnia ocen jeśli podana")


class WorkExperience(BaseModel):
    """Pojedynczy wpis doświadczenia zawodowego"""

    company: str = Field(..., description="Nazwa firmy")
    position: str = Field(..., description="Stanowisko")
    start_date: Optional[str] = Field(
        None, description="Data rozpoczęcia (rok lub rok-miesiąc)"
    )
    end_date: Optional[str] = Field(
        None, description="Data zakończenia, 'present' jeśli aktualne"
    )
    location: Optional[str] = Field(None, description="Lokalizacja pracy")
    responsibilities: List[str] = Field(
        default_factory=list, description="Lista obowiązków i osiągnięć"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Użyte technologie/narzędzia"
    )


class Project(BaseModel):
    """Projekt osobisty lub zawodowy"""

    name: str = Field(..., description="Nazwa projektu")
    description: str = Field(..., description="Opis projektu")
    technologies: List[str] = Field(
        default_factory=list, description="Użyte technologie"
    )
    url: Optional[str] = Field(None, description="Link do projektu/repo")
    role: Optional[str] = Field(None, description="Rola w projekcie")


class Language(BaseModel):
    """Znajomość języka"""

    language: str = Field(..., description="Nazwa języka")
    proficiency: Optional[LanguageProficiency] = Field(
        None, description="Poziom zaawansowania"
    )


class Certification(BaseModel):
    """Certyfikat lub ukończony kurs"""

    name: str = Field(..., description="Nazwa certyfikatu/kursu")
    issuer: Optional[str] = Field(None, description="Organizacja wydająca")
    date: Optional[str] = Field(None, description="Data uzyskania")
    credential_id: Optional[str] = Field(None, description="ID certyfikatu")
    url: Optional[str] = Field(None, description="Link do weryfikacji")


class CVData(BaseModel):
    """Kompletna struktura danych z CV"""

    # Dane podstawowe
    full_name: Optional[str] = Field(None, description="Imię i nazwisko")
    professional_title: Optional[str] = Field(
        None, description="Tytuł zawodowy/stanowisko docelowe"
    )
    summary: Optional[str] = Field(None, description="Podsumowanie/opis kandydata")

    # Kontakt
    contact: ContactInfo = Field(
        default_factory=ContactInfo, description="Informacje kontaktowe"
    )

    # Doświadczenie i edukacja
    work_experience: List[WorkExperience] = Field(
        default_factory=list, description="Doświadczenie zawodowe"
    )
    education: List[Education] = Field(
        default_factory=list, description="Wykształcenie"
    )

    # Umiejętności
    technical_skills: List[str] = Field(
        default_factory=list, description="Umiejętności techniczne"
    )
    soft_skills: List[str] = Field(
        default_factory=list, description="Umiejętności miękkie"
    )

    # Języki
    languages: List[Language] = Field(
        default_factory=list, description="Znajomość języków"
    )

    # Projekty
    projects: List[Project] = Field(default_factory=list, description="Projekty")

    # Certyfikaty
    certifications: List[Certification] = Field(
        default_factory=list, description="Certyfikaty i kursy"
    )

    # Dodatkowe
    interests: List[str] = Field(default_factory=list, description="Zainteresowania")
    volunteer_experience: Optional[str] = Field(
        None, description="Wolontariat/działalność społeczna"
    )
    publications: List[str] = Field(
        default_factory=list, description="Publikacje naukowe"
    )
    awards: List[str] = Field(default_factory=list, description="Nagrody i wyróżnienia")
