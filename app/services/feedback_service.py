from app.services.feedback.profanity import check_moderation_tool
from app.services.feedback.style_mapping import map_leadership_style, load_prompts
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


async def get_feedback(message: str, s_level: str, d_level: str) -> str:
    routing = map_leadership_style(d_level, s_level)
    profanity_check = check_moderation_tool(message)
    if profanity_check:
        return {
            "feedback": 'Przekazana informacja zawiera nieodpowiednie treści, mogące być odebrane jako obraźliwe. Skoryguj proszę opis sytuacji do wygenerowania feedbacku.',
            "metadata": {
                "development_level": routing["development_level"],
                "recommended_style": routing["recommended_style"],
                "applied_style": routing["final_style"],
                "is_aligned": routing["is_aligned"],
                "warning": routing["warning"],
                "tokens": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                },
            },
        }

    try:
        prompts = load_prompts(routing["development_level"], routing["final_style"])
    except ValueError as e:
        return {
            "feedback": 'Coś poszło nie tak... Spróbuj ponownie ',
            "metadata": {
                "development_level": routing["development_level"],
                "recommended_style": routing["recommended_style"],
                "applied_style": routing["final_style"],
                "is_aligned": routing["is_aligned"],
                "warning": routing["warning"],
                "tokens": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                },
            },
        }
    client = AsyncOpenAI()
    model = os.getenv("OPENAI_MODEL")

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompts["combined"]},
            {"role": "user", "content": f"Sytuacja wymagająca feedbacku: {message}"},
        ],
    )

    feedback_text = response.choices[0].message.content

    return {
        "feedback": feedback_text,
        "metadata": {
            "development_level": routing["development_level"],
            "recommended_style": routing["recommended_style"],
            "applied_style": routing["final_style"],
            "is_aligned": routing["is_aligned"],
            "warning": routing["warning"],
            "tokens": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        },
    }
