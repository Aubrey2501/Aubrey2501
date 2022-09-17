from datetime import datetime
import json


def add_history_row(cmd: str, cmd_time: datetime, hotels: list[str]):
    """Добавляет в базу запись о команде"""
    
    with open("database/history.json", "rb") as f:
        data = json.load(f)
    
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
