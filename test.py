import json
a = ["21512412421521"]
with open("blacklist.txt", "w") as f:
    json.dump(a, f)