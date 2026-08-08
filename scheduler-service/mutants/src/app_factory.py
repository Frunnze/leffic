from fastapi import FastAPI

from features.flashcard_scheduling.flashcard_scheduler_router import (
    flashcard_scheduler,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_create_app__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_app__mutmut)
def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(flashcard_scheduler)

    return app


def x_create_app__mutmut_orig() -> FastAPI:
    app = FastAPI()
    app.include_router(flashcard_scheduler)

    return app


def x_create_app__mutmut_1() -> FastAPI:
    app = None
    app.include_router(flashcard_scheduler)

    return app


def x_create_app__mutmut_2() -> FastAPI:
    app = FastAPI()
    app.include_router(None)

    return app

mutants_x_create_app__mutmut['_mutmut_orig'] = x_create_app__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_1'] = x_create_app__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_2'] = x_create_app__mutmut_2 # type: ignore # mutmut generated
