from datetime import datetime
import json
from json import JSONDecodeError


def add_history_row(cmd: str, cmd_time: datetime, hotels: list[str]):
    """Добавляет в базу запись о команде"""

    try:
        with open("database/history.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        f = open("database/history.json", "w")
        f.close()
        data = {"history": []}
    except JSONDecodeError:
        data = {"history": []}
    
    data["history"].append({
        "cmd": cmd,
        "cmd_time": cmd_time.strftime("%Y.%m.%d %H:%M:"),
        "hotels": hotels
    })

    with open("database/history.json", "w") as f:
        json.dump(data, f)


def get_history() -> list[dict]:
    """Возвращает список словарей, 
    где каждая запись имеет вид {"cmd": ..., "cmd_time": ..., "hotels": ...}
    """

    with open("database/history.json", "rb") as f:
        data = json.load(f)
    
    return data["history"]
