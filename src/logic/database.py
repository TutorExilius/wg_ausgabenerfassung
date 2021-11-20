from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.globals import DATABASE_URL
from src.model.models import User, Entry

engine = create_engine(DATABASE_URL)


def initialise_users(user_names: List[str]) -> None:
    with Session(engine) as session:
        for user_name in user_names:
            user = session.query(User).filter_by(user_name=user_name).one_or_none()

            if user is None:
                user = User(user_name=user_name)
                session.add(user)
                print(f"Created '{user_name}' in users table.")

        session.commit()

def add_amount(user_name: str, amount_in_cents: int) -> None:
    with Session(engine) as session:
        user = session.query(User).filter_by(user_name=user_name).one_or_none()

        if user is None:
            raise ValueError(f"Can't update amount for user '{user_name}', User not found.")

        entry = Entry(amount_in_cents=amount_in_cents)
        session.add(entry)

        user.entries.append(entry)
        print(f"Added '{amount_in_cents}' for user '{user_name}'.")

        session.commit()

def get_total_amount_in_cents(user_name: str, year: int) -> int:
    with Session(engine) as session:
        user = session.query(User).filter_by(user_name=user_name).one_or_none()

        if user is None:
            raise ValueError(f"Can't update amount for user '{user_name}', User not found.")

        return sum(entry.amount_in_cents for entry in user.entries)