from datetime import datetime

def print_log(page_name: str, user_name: str, action: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} from [{page_name}]: '{user_name}' {action}.")

def max_digits_behind_comma_arrived(amount: str) -> bool:
    splitted_amout = amount.split(",")
    return len(splitted_amout) > 1 and len(splitted_amout[1]) > 1