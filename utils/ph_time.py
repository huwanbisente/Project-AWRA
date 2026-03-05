from datetime import datetime
from zoneinfo import ZoneInfo

def get_ph_time():
    """Returns the current time in Asia/Manila timezone."""
    return datetime.now(ZoneInfo("Asia/Manila"))

def get_ph_date_str():
    """Returns the current date in YYYY-MM-DD format (Manila Time)."""
    return get_ph_time().strftime("%Y-%m-%d")

if __name__ == "__main__":
    print(f"Manila Time: {get_ph_time()}")
    print(f"Date String: {get_ph_date_str()}")
