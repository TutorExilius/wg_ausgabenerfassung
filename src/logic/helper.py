import asyncio
from datetime import datetime
from pathlib import Path
from shutil import copy2

TRY_SYNCING = False


def print_log(page_name: str, user_name: str, action: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} from [{page_name}]: '{user_name}' {action}.")


def max_digits_behind_comma_arrived(amount: str) -> bool:
    splitted_amout = amount.split(",")
    return len(splitted_amout) > 1 and len(splitted_amout[1]) > 1


def amount_in_cents_to_str(amount_in_cents: int) -> str:
    amount = str(amount_in_cents)

    if len(amount) == 1:
        amount = "0,0" + amount
    elif len(amount) == 2:
        amount = "0," + amount
    else:
        digits = list(amount)
        digits.insert(-2, ",")
        amount = "".join(digits)

    return amount + " €"


async def sync_database(soure_database_file: Path, target_database_file: Path) -> None:
    if not soure_database_file.is_file():
        raise FileNotFoundError(f"File not found '{soure_database_file}'")

    if not target_database_file.is_dir():
        raise NotADirectoryError(f"Directory not found '{soure_database_file}'")

    global TRY_SYNCING

    while not TRY_SYNCING:
        try:
            TRY_SYNCING = True
            copy2(soure_database_file, target_database_file)
            print("Database synced.")
            TRY_SYNCING = False
            break
        except Exception as e:
            secs = 60
            print("Failed sync.\n")
            print(e)
            print(f"\nRetry in {secs} sec...")

            await asyncio.sleep(secs)