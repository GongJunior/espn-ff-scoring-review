import json
import itertools
import csv
from pathlib import Path
import duckdb as ddb

pos_map = {1: "qb", 2: "rb", 3: "wr", 4: "te", 5: "k", 11: "dp", 16: "def", 14: "hc"}
db = Path("data.ddb")


def get_data_len(n):
    with open(n, "r") as f:
        data = json.load(f)
        print(f"file: {n} - {len(data["players"])}")


def show_player_count_in_file():
    files = Path(".").glob("*.json")
    _ = [get_data_len(f) for f in files]


def get_players(filename="2023allplayers.json"):
    data = {}
    with open(filename, "r") as f:
        data = json.load(f)["players"]
    return data


def extract_player_data(filename, player):
    records = []
    id = player["id"]
    name = player["fullName"]
    pos = player["defaultPositionId"]
    season_stats = player["stats"]
    for ss in season_stats:
        if ss["id"] == "002023" or ss["id"] == "102024":
            records.append(
                [
                    filename,
                    id,
                    name,
                    pos_map.get(pos, "dp"),
                    ss["seasonId"],
                    ss["appliedTotal"],
                    ss["appliedAverage"],
                ]
            )
    if len(records) == 0:
        records.append([filename, id, name, pos_map.get(pos, "dp"), 2023, "", ""])
    return records


def setup_csvs():
    headers = ["filename", "id", "name", "pos", "season", "total", "average"]
    files = Path("data").glob("*.json")
    for f in files:
        data = [
            extract_player_data(f.stem, x["player"]) for x in get_players(f.resolve())
        ]
        full_data = [headers, *list(itertools.chain(*data))]
        with open(f.with_name(f"{f.stem}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(full_data)


def review_data():
    if len(list(Path("data").glob("*.csv"))) == 0:
        setup_csvs()

    ddb.sql("create table pos_counts (pos varchar, cnt int);")
    ddb.sql("""
        insert into pos_counts (pos, cnt) values
        ('qb', 24),
        ('rb', 48),
        ('wr', 48),
        ('te', 36),
        ('k', 24),
        ('dp', 24),
        ('def', 24),
        ('hc', 24);
        """)
    pos_counts = ddb.sql("select * from pos_counts")
    rel = ddb.read_csv("data/*.csv")
    rel23 = rel.filter("season = 2023")

    # top 250 players
    top_250 = rel23.rank(
        "over (partition by filename order by average desc) as posrnk",
        "filename, name, pos, average",
    ).filter("posrnk <= 250")

    # # show top 10
    # print("\ntop 10: Top Players")
    # top_250.limit(10).show()

    print("\ntop 250: Gen Info")
    pos_averages = top_250.aggregate(
        "filename, pos, count(*) as cnt, round(min(average), 2) as fmin, round(max(average), 2) as fmax, round(avg(average), 2) as favg"
    )
    print(pos_averages.order("filename, favg desc"))

    # top by position
    print("\ntop in position: Gen Info")
    rnk_by_pos = rel23.rank(
        "over (partition by filename, pos order by average desc) as posrnk",
        "filename, name, pos, average",
    ).join(pos_counts, "pos").filter("posrnk <= cnt")
    pos_ranks = rnk_by_pos.aggregate(
        "filename, pos, count(*) as cnt, round(min(average), 2) as fmin, round(max(average), 2) as fmax, round(avg(average), 2) as favg"
    )
    print(pos_ranks.order("filename, favg desc"))



review_data()
