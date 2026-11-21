"""Florida ZIP codes -> place and county, from GeoNames postal codes
(https://download.geonames.org/export/zip/US.zip). Writes content/fl_zips.json."""
import json, sys
src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/work/zip/US.txt"
ROOT = __file__.rsplit("/tools/", 1)[0] + "/"
fix = {"Saint ": "St. "}
out = []
for line in open(src, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if p[4] != "FL":
        continue
    county = p[5].replace("Miami-Dade", "Miami-Dade").replace("Saint ", "St. ").replace("De Soto", "DeSoto").replace("Desoto", "DeSoto")
    place = p[2]
    for a, b in fix.items():
        place = place.replace(a, b)
    out.append({"zip": p[1], "place": place, "county": county, "lat": float(p[9] or 0), "lon": float(p[10] or 0)})
out.sort(key=lambda x: x["zip"])
json.dump(out, open(ROOT + "content/fl_zips.json", "w"), indent=0, ensure_ascii=False)
print(len(out), "ZIPs;", len({x["county"] for x in out}), "counties")
