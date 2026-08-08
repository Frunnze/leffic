from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from features.authentication.authentication_router import auth
from shared.database import Base, engine

_ = load_dotenv()


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_create_app__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_create_app__mutmut)
def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_orig() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_1() -> FastAPI:
    app = None

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_2() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        None,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_3() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_4() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=None,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_5() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=None,
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_6() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=None,
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_7() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_8() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_9() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_10() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_11() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_12() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["XX*XX"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_13() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_14() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["XX*XX"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_15() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["XX*XX"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_16() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(None)

    Base.metadata.create_all(bind=engine)

    return app


def x_create_app__mutmut_17() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)

    Base.metadata.create_all(bind=None)

    return app

mutants_x_create_app__mutmut['_mutmut_orig'] = x_create_app__mutmut_orig # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_1'] = x_create_app__mutmut_1 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_2'] = x_create_app__mutmut_2 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_3'] = x_create_app__mutmut_3 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_4'] = x_create_app__mutmut_4 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_5'] = x_create_app__mutmut_5 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_6'] = x_create_app__mutmut_6 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_7'] = x_create_app__mutmut_7 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_8'] = x_create_app__mutmut_8 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_9'] = x_create_app__mutmut_9 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_10'] = x_create_app__mutmut_10 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_11'] = x_create_app__mutmut_11 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_12'] = x_create_app__mutmut_12 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_13'] = x_create_app__mutmut_13 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_14'] = x_create_app__mutmut_14 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_15'] = x_create_app__mutmut_15 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_16'] = x_create_app__mutmut_16 # type: ignore # mutmut generated
mutants_x_create_app__mutmut['x_create_app__mutmut_17'] = x_create_app__mutmut_17 # type: ignore # mutmut generated
