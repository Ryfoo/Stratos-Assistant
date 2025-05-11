import json
import os

SCORE_FILE = "scores.json"

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return {"teams": {}}
    with open(SCORE_FILE, "r") as f:
        return json.load(f)

def save_scores(data):
    with open(SCORE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_point(team_id: str):
    scores = load_scores()
    if team_id not in scores["teams"]:
        scores["teams"][team_id] = {"points": 0, "eliminated": False}
    scores["teams"][team_id]["points"] += 1
    save_scores(scores)

def get_scores():
    return load_scores()
