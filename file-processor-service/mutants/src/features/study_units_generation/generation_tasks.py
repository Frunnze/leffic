from typing import TypedDict

from features.study_units_generation.content_management_client import (
    save_study_unit,
)
from features.study_units_generation.prompts.flashcards_prompt import (
    get_flashcards_system_prompt,
)
from features.study_units_generation.prompts.notes_prompt import (
    get_notes_system_prompt,
)
from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)
from shared.ai_manager import ai_factory
from shared.celery_app import celery_app

_DECK_NAME = "deck_name"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


class FlashcardsMetadata(TypedDict):
    comprehensiveness: str
    verbosity: str
    types: list[str] | None
    amount: int | None
mutants_x__generate_flashcards_task__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__generate_flashcards_task__mutmut)
def _generate_flashcards_task(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_orig(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_1(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = None
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_2(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(None)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_3(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = None
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_4(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=None,
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_5(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=None,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_6(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_7(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_8(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=None,
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_9(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=None,
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_10(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=None,
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_11(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=None,
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_12(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_13(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_14(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_15(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_16(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["XXcomprehensivenessXX"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_17(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["COMPREHENSIVENESS"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_18(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["XXverbosityXX"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_19(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["VERBOSITY"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_20(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["XXamountXX"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_21(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["AMOUNT"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_22(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(None),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_23(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] and ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_24(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["XXtypesXX"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_25(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["TYPES"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_26(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = None

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_27(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(None)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_28(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = None

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_29(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        None,
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_30(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        None,
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_31(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_32(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_33(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "XX/save-flashcardsXX",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_34(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/SAVE-FLASHCARDS",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_35(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "XXflashcardsXX": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_36(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "FLASHCARDS": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_37(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "XXdeck_nameXX": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_38(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "DECK_NAME": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_39(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "XXfolder_idXX": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_40(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "FOLDER_ID": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_41(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "XXuser_idXX": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_42(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "USER_ID": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_43(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "XXflashcard_deck_idXX": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_44(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "FLASHCARD_DECK_ID": saved.get("flashcard_deck_id"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_45(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get(None),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_46(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("XXflashcard_deck_idXX"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_47(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("FLASHCARD_DECK_ID"),
        "deck_name": deck_name,
    }


def x__generate_flashcards_task__mutmut_48(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "XXdeck_nameXX": deck_name,
    }


def x__generate_flashcards_task__mutmut_49(
    ai_model: str | None,
    extracted_text: str,
    flashcards_metadata: FlashcardsMetadata,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata["comprehensiveness"],
            verbosity=flashcards_metadata["verbosity"],
            amount=flashcards_metadata["amount"],
            flashcard_types=tuple(flashcards_metadata["types"] or ()),
        ),
        user_prompt=extracted_text,
    )
    deck_name = flashcards.pop(_DECK_NAME)

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-flashcards",
        {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "flashcard_deck_id": saved.get("flashcard_deck_id"),
        "DECK_NAME": deck_name,
    }

mutants_x__generate_flashcards_task__mutmut['_mutmut_orig'] = x__generate_flashcards_task__mutmut_orig # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_1'] = x__generate_flashcards_task__mutmut_1 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_2'] = x__generate_flashcards_task__mutmut_2 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_3'] = x__generate_flashcards_task__mutmut_3 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_4'] = x__generate_flashcards_task__mutmut_4 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_5'] = x__generate_flashcards_task__mutmut_5 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_6'] = x__generate_flashcards_task__mutmut_6 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_7'] = x__generate_flashcards_task__mutmut_7 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_8'] = x__generate_flashcards_task__mutmut_8 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_9'] = x__generate_flashcards_task__mutmut_9 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_10'] = x__generate_flashcards_task__mutmut_10 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_11'] = x__generate_flashcards_task__mutmut_11 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_12'] = x__generate_flashcards_task__mutmut_12 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_13'] = x__generate_flashcards_task__mutmut_13 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_14'] = x__generate_flashcards_task__mutmut_14 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_15'] = x__generate_flashcards_task__mutmut_15 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_16'] = x__generate_flashcards_task__mutmut_16 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_17'] = x__generate_flashcards_task__mutmut_17 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_18'] = x__generate_flashcards_task__mutmut_18 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_19'] = x__generate_flashcards_task__mutmut_19 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_20'] = x__generate_flashcards_task__mutmut_20 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_21'] = x__generate_flashcards_task__mutmut_21 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_22'] = x__generate_flashcards_task__mutmut_22 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_23'] = x__generate_flashcards_task__mutmut_23 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_24'] = x__generate_flashcards_task__mutmut_24 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_25'] = x__generate_flashcards_task__mutmut_25 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_26'] = x__generate_flashcards_task__mutmut_26 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_27'] = x__generate_flashcards_task__mutmut_27 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_28'] = x__generate_flashcards_task__mutmut_28 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_29'] = x__generate_flashcards_task__mutmut_29 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_30'] = x__generate_flashcards_task__mutmut_30 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_31'] = x__generate_flashcards_task__mutmut_31 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_32'] = x__generate_flashcards_task__mutmut_32 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_33'] = x__generate_flashcards_task__mutmut_33 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_34'] = x__generate_flashcards_task__mutmut_34 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_35'] = x__generate_flashcards_task__mutmut_35 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_36'] = x__generate_flashcards_task__mutmut_36 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_37'] = x__generate_flashcards_task__mutmut_37 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_38'] = x__generate_flashcards_task__mutmut_38 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_39'] = x__generate_flashcards_task__mutmut_39 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_40'] = x__generate_flashcards_task__mutmut_40 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_41'] = x__generate_flashcards_task__mutmut_41 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_42'] = x__generate_flashcards_task__mutmut_42 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_43'] = x__generate_flashcards_task__mutmut_43 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_44'] = x__generate_flashcards_task__mutmut_44 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_45'] = x__generate_flashcards_task__mutmut_45 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_46'] = x__generate_flashcards_task__mutmut_46 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_47'] = x__generate_flashcards_task__mutmut_47 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_48'] = x__generate_flashcards_task__mutmut_48 # type: ignore # mutmut generated
mutants_x__generate_flashcards_task__mutmut['x__generate_flashcards_task__mutmut_49'] = x__generate_flashcards_task__mutmut_49 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__generate_note_task__mutmut)
def _generate_note_task(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_orig(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_1(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = None
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_2(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(None)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_3(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = None

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_4(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=None,
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_5(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=None,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_6(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_7(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_8(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = None

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_9(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        None,
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_10(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        None,
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_11(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_12(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_13(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "XX/save-noteXX",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_14(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/SAVE-NOTE",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_15(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "XXnote_contentXX": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_16(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "NOTE_CONTENT": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_17(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get(None),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_18(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("XXnote_contentXX"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_19(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("NOTE_CONTENT"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_20(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "XXnote_nameXX": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_21(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "NOTE_NAME": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_22(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get(None),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_23(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("XXnote_nameXX"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_24(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("NOTE_NAME"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_25(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "XXfolder_idXX": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_26(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "FOLDER_ID": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_27(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "XXuser_idXX": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_28(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "USER_ID": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_29(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "XXnote_idXX": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_30(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "NOTE_ID": saved.get("note_id"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_31(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get(None),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_32(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("XXnote_idXX"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_33(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("NOTE_ID"),
        "note_name": note.get("note_name"),
    }


def x__generate_note_task__mutmut_34(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "XXnote_nameXX": note.get("note_name"),
    }


def x__generate_note_task__mutmut_35(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "NOTE_NAME": note.get("note_name"),
    }


def x__generate_note_task__mutmut_36(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get(None),
    }


def x__generate_note_task__mutmut_37(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("XXnote_nameXX"),
    }


def x__generate_note_task__mutmut_38(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text,
    )

    # Save the flashcards in the content's db
    saved = save_study_unit(
        "/save-note",
        {
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "note_id": saved.get("note_id"),
        "note_name": note.get("NOTE_NAME"),
    }

mutants_x__generate_note_task__mutmut['_mutmut_orig'] = x__generate_note_task__mutmut_orig # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_1'] = x__generate_note_task__mutmut_1 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_2'] = x__generate_note_task__mutmut_2 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_3'] = x__generate_note_task__mutmut_3 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_4'] = x__generate_note_task__mutmut_4 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_5'] = x__generate_note_task__mutmut_5 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_6'] = x__generate_note_task__mutmut_6 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_7'] = x__generate_note_task__mutmut_7 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_8'] = x__generate_note_task__mutmut_8 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_9'] = x__generate_note_task__mutmut_9 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_10'] = x__generate_note_task__mutmut_10 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_11'] = x__generate_note_task__mutmut_11 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_12'] = x__generate_note_task__mutmut_12 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_13'] = x__generate_note_task__mutmut_13 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_14'] = x__generate_note_task__mutmut_14 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_15'] = x__generate_note_task__mutmut_15 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_16'] = x__generate_note_task__mutmut_16 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_17'] = x__generate_note_task__mutmut_17 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_18'] = x__generate_note_task__mutmut_18 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_19'] = x__generate_note_task__mutmut_19 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_20'] = x__generate_note_task__mutmut_20 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_21'] = x__generate_note_task__mutmut_21 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_22'] = x__generate_note_task__mutmut_22 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_23'] = x__generate_note_task__mutmut_23 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_24'] = x__generate_note_task__mutmut_24 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_25'] = x__generate_note_task__mutmut_25 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_26'] = x__generate_note_task__mutmut_26 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_27'] = x__generate_note_task__mutmut_27 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_28'] = x__generate_note_task__mutmut_28 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_29'] = x__generate_note_task__mutmut_29 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_30'] = x__generate_note_task__mutmut_30 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_31'] = x__generate_note_task__mutmut_31 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_32'] = x__generate_note_task__mutmut_32 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_33'] = x__generate_note_task__mutmut_33 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_34'] = x__generate_note_task__mutmut_34 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_35'] = x__generate_note_task__mutmut_35 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_36'] = x__generate_note_task__mutmut_36 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_37'] = x__generate_note_task__mutmut_37 # type: ignore # mutmut generated
mutants_x__generate_note_task__mutmut['x__generate_note_task__mutmut_38'] = x__generate_note_task__mutmut_38 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__generate_test_task__mutmut)
def _generate_test_task(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_orig(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_1(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = None
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_2(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(None)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_3(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = None

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_4(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=None,
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_5(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=None,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_6(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_7(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_8(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = None

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_9(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        None,
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_10(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        None,
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_11(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_12(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_13(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "XX/save-testXX",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_14(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/SAVE-TEST",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_15(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "XXtest_itemsXX": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_16(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "TEST_ITEMS": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_17(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get(None),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_18(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("XXmultiple_choice_test_itemsXX"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_19(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("MULTIPLE_CHOICE_TEST_ITEMS"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_20(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "XXtest_nameXX": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_21(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "TEST_NAME": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_22(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get(None),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_23(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("XXtest_nameXX"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_24(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("TEST_NAME"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_25(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "XXfolder_idXX": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_26(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "FOLDER_ID": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_27(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "XXuser_idXX": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_28(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "USER_ID": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_29(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "XXtest_idXX": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_30(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "TEST_ID": saved.get("test_id"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_31(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get(None),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_32(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("XXtest_idXX"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_33(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("TEST_ID"),
        "test_name": test.get("test_name"),
    }


def x__generate_test_task__mutmut_34(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "XXtest_nameXX": test.get("test_name"),
    }


def x__generate_test_task__mutmut_35(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "TEST_NAME": test.get("test_name"),
    }


def x__generate_test_task__mutmut_36(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get(None),
    }


def x__generate_test_task__mutmut_37(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("XXtest_nameXX"),
    }


def x__generate_test_task__mutmut_38(
    ai_model: str | None,
    extracted_text: str,
    folder_id: str,
    user_id: str,
) -> dict[str, object]:
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text,
    )

    saved = save_study_unit(
        "/save-test",
        {
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        },
    )

    return {
        "test_id": saved.get("test_id"),
        "test_name": test.get("TEST_NAME"),
    }

mutants_x__generate_test_task__mutmut['_mutmut_orig'] = x__generate_test_task__mutmut_orig # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_1'] = x__generate_test_task__mutmut_1 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_2'] = x__generate_test_task__mutmut_2 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_3'] = x__generate_test_task__mutmut_3 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_4'] = x__generate_test_task__mutmut_4 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_5'] = x__generate_test_task__mutmut_5 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_6'] = x__generate_test_task__mutmut_6 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_7'] = x__generate_test_task__mutmut_7 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_8'] = x__generate_test_task__mutmut_8 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_9'] = x__generate_test_task__mutmut_9 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_10'] = x__generate_test_task__mutmut_10 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_11'] = x__generate_test_task__mutmut_11 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_12'] = x__generate_test_task__mutmut_12 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_13'] = x__generate_test_task__mutmut_13 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_14'] = x__generate_test_task__mutmut_14 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_15'] = x__generate_test_task__mutmut_15 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_16'] = x__generate_test_task__mutmut_16 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_17'] = x__generate_test_task__mutmut_17 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_18'] = x__generate_test_task__mutmut_18 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_19'] = x__generate_test_task__mutmut_19 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_20'] = x__generate_test_task__mutmut_20 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_21'] = x__generate_test_task__mutmut_21 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_22'] = x__generate_test_task__mutmut_22 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_23'] = x__generate_test_task__mutmut_23 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_24'] = x__generate_test_task__mutmut_24 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_25'] = x__generate_test_task__mutmut_25 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_26'] = x__generate_test_task__mutmut_26 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_27'] = x__generate_test_task__mutmut_27 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_28'] = x__generate_test_task__mutmut_28 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_29'] = x__generate_test_task__mutmut_29 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_30'] = x__generate_test_task__mutmut_30 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_31'] = x__generate_test_task__mutmut_31 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_32'] = x__generate_test_task__mutmut_32 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_33'] = x__generate_test_task__mutmut_33 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_34'] = x__generate_test_task__mutmut_34 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_35'] = x__generate_test_task__mutmut_35 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_36'] = x__generate_test_task__mutmut_36 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_37'] = x__generate_test_task__mutmut_37 # type: ignore # mutmut generated
mutants_x__generate_test_task__mutmut['x__generate_test_task__mutmut_38'] = x__generate_test_task__mutmut_38 # type: ignore # mutmut generated


generate_flashcards_task = celery_app.task(_generate_flashcards_task)
generate_note_task = celery_app.task(_generate_note_task)
generate_test_task = celery_app.task(_generate_test_task)
