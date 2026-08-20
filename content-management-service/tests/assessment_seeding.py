import uuid
from datetime import UTC, datetime

from hypothesis import strategies as st
from sqlalchemy.orm import Session

from shared.models import Test, TestItem
from tests.folder_seeding import seeded_folder

NOT_FOUND = 404
UNREADABLE = st.sampled_from(
    ["", " ", "not-a-uuid", "home-folder", "../etc", "null", "0"]
)
UNREADABLE_ID = st.sampled_from(
    [" ", "not-a-uuid", "home-folder", "../etc", "null", "0"]
)


def seeded_test(
    session: Session, owner: uuid.UUID, item_count: int
) -> tuple[uuid.UUID, uuid.UUID, list[int]]:
    folder_id = seeded_folder(session, owner, {})
    quiz = Test(
        id=uuid.uuid4(),
        name="Quiz",
        folder_id=folder_id,
        created_at=datetime.now(UTC),
        public=False,
    )
    session.add(quiz)

    for index in range(item_count):
        quiz.test_items.append(
            TestItem(
                content={"question": f"q{index}", "true_option": "yes"},
                type="multiple_choice",
                created_at=datetime.now(UTC),
            )
        )

    session.commit()

    return folder_id, quiz.id, [item.id for item in quiz.test_items]
