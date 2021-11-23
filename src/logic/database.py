from datetime import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src import globals
from src.model.models import Entry, User

engine = create_engine(globals.DATABASE_URL)


def initialise_users(user_names: List[str]) -> None:
    with Session(engine) as session:
        for user_name in user_names:
            user = session.query(User).filter_by(user_name=user_name).one_or_none()

            if user is None:
                user = User(user_name=user_name, created_at=datetime.utcnow())
                session.add(user)
                print(f"Created '{user_name}' in users table.")

        session.commit()


def add_amount(user_name: str, amount_in_cents: int) -> None:
    with Session(engine) as session:
        user = session.query(User).filter_by(user_name=user_name).one_or_none()

        if user is None:
            raise ValueError(f"Can't update amount for user '{user_name}', User not found.")

        entry = Entry(amount_in_cents=amount_in_cents, created_at=datetime.utcnow())
        session.add(entry)

        user.entries.append(entry)
        print(f"Added '{amount_in_cents}' for user '{user_name}'.")

        session.commit()


def get_total_amount_in_cents(user_name: str, year: int) -> int:
    with Session(engine) as session:
        user = session.query(User).filter_by(user_name=user_name).one_or_none()

        if user is None:
            raise ValueError(f"Can't update amount for user '{user_name}', User not found.")

        entries_in_year = (entry.amount_in_cents for entry in user.entries if entry.created_at.year == year)
        return sum(entry for entry in entries_in_year)


def get_oldest_year() -> int:
    with Session(engine) as session:
        user_names = globals.USERS

        oldest_year = datetime.utcnow().year

        for user_name in user_names:
            user = session.query(User).filter_by(user_name=user_name).one_or_none()

            if user is None:
                raise ValueError(f"Can't update amount for user '{user_name}', User not found.")

            if user.entries:
                year = user.entries[0].created_at.year
                if oldest_year > year:
                    oldest_year = year

    return oldest_year
