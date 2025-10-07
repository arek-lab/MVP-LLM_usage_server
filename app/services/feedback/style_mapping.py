from app.services.feedback.prompts.system_prompts import system_prompt
from app.services.feedback.prompts.development_levels import D1, D2, D3, D4
from app.services.feedback.prompts.leadership_styles import S1, S2, S3, S4


def map_leadership_style(d_level: str, s_level: str = None) -> dict:
    """
    Mapuje poziom rozwoju pracownika na odpowiedni styl przywództwa
    zgodnie z teorią Blancharda.

    Args:
        d_level: Poziom rozwoju (D1-D4)
        s_level: Opcjonalny styl przywództwa podany przez usera (S1-S4)

    Returns:
        dict z kluczami:
            - recommended_style: zalecany styl według teorii
            - user_style: styl podany przez usera (jeśli był)
            - is_aligned: czy styl usera jest zgodny z teorią
            - development_prompt: prompt dla poziomu D
            - leadership_prompt: prompt dla stylu S (zalecany lub user)
            - warning: opcjonalne ostrzeżenie o niezgodności
    """

    # Mapowanie według teorii Blancharda
    BLANCHARD_MAPPING = {"D1": "S1", "D2": "S2", "D3": "S3", "D4": "S4"}

    # Walidacja D level
    valid_d_levels = ["D1", "D2", "D3", "D4"]
    valid_s_levels = ["S1", "S2", "S3", "S4"]

    d_level_upper = d_level.upper()

    if d_level_upper not in valid_d_levels:
        raise ValueError(
            f"Nieprawidłowy poziom rozwoju. Dozwolone: {', '.join(valid_d_levels)}"
        )

    recommended_style = BLANCHARD_MAPPING[d_level_upper]

    # Jeśli user podał styl S
    if s_level:
        s_level_upper = s_level.upper()

        if s_level_upper not in valid_s_levels:
            raise ValueError(
                f"Nieprawidłowy styl przywództwa. Dozwolone: {', '.join(valid_s_levels)}"
            )

        is_aligned = s_level_upper == recommended_style
        final_style = s_level_upper

        warning = None
        if not is_aligned:
            warning = (
                f"Uwaga: Dla poziomu rozwoju {d_level_upper} teoria Blancharda "
                f"rekomenduje styl {recommended_style}, a wybrano {s_level_upper}. "
                f"To może być mniej efektywne."
            )
    else:
        # Brak stylu od usera - użyj zalecanego
        is_aligned = True
        final_style = recommended_style
        warning = None

    return {
        "recommended_style": recommended_style,
        "user_style": s_level.upper() if s_level else None,
        "final_style": final_style,
        "is_aligned": is_aligned,
        "development_level": d_level_upper,
        "warning": warning,
    }


def load_prompts(d_level: str, s_level: str) -> dict:
    """
    Ładuje odpowiednie prompty dla danej kombinacji D i S.

    Args:
        d_level: Poziom rozwoju (D1-D4)
        s_level: Styl przywództwa (S1-S4)

    Returns:
        dict z promptami: base, development, leadership, combined
    """

    # Import promptów (zakładając strukturę jak wcześniej opisana)
    DEVELOPMENT_PROMPTS = {
        "D1": D1,
        "D2": D2,
        "D3": D3,
        "D4": D4,
    }

    LEADERSHIP_PROMPTS = {
        "S1": S1,
        "S2": S2,
        "S3": S3,
        "S4": S4,
    }

    base_prompt = system_prompt
    development_prompt = DEVELOPMENT_PROMPTS.get(d_level.upper())
    leadership_prompt = LEADERSHIP_PROMPTS.get(s_level.upper())

    if not development_prompt:
        raise ValueError(f"Brak promptu dla poziomu rozwoju {d_level}")

    if not leadership_prompt:
        raise ValueError(f"Brak promptu dla stylu przywództwa {s_level}")

    combined_prompt = (
        base_prompt + "\n\n" + development_prompt + "\n\n" + leadership_prompt
    )

    return {
        "base": base_prompt,
        "development": development_prompt,
        "leadership": leadership_prompt,
        "combined": combined_prompt,
    }
