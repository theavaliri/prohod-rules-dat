#!/usr/bin/env python3
import json
import pathlib
import sys

CATEGORIES = [
    "category-ads",
    "category-finance",
    "category-gov",
    "category-media",
    "category-medicine",
    "category-public-dns",
    "category-shopping",
    "category-telecom",
    "category-transport",
    "category-video",
    "other",
    "ozon",
    "vk",
    "wildberries",
    "x5",
    "yandex",
    "private",
]


def parse(path):
    out = {"suffix": [], "full": [], "keyword": []}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        value = line.split("@", 1)[0].strip()
        if not value or value.startswith("regexp:"):
            continue
        if value.startswith("full:"):
            out["full"].append(value[5:])
        elif value.startswith("keyword:"):
            out["keyword"].append(value[8:])
        elif value.startswith("domain:"):
            out["suffix"].append(value[7:])
        else:
            out["suffix"].append(value)
    for key in out:
        out[key] = sorted(set(out[key]))
    return out


def write_set(name, data, outdir):
    rules = {}
    if data["suffix"]:
        rules["domain_suffix"] = data["suffix"]
    if data["full"]:
        rules["domain"] = data["full"]
    if data["keyword"]:
        rules["domain_keyword"] = data["keyword"]
    srs = {"version": 3, "rules": [rules] if rules else []}
    (outdir / f"{name}.srs.json").write_text(
        json.dumps(srs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    mihomo = [f"+.{d}" for d in data["suffix"]] + list(data["full"])
    (outdir / f"{name}.mrs.txt").write_text("\n".join(mihomo) + "\n", encoding="utf-8")

    shadowrocket = (
        [f"DOMAIN-SUFFIX,{d}" for d in data["suffix"]]
        + [f"DOMAIN,{d}" for d in data["full"]]
        + [f"DOMAIN-KEYWORD,{d}" for d in data["keyword"]]
    )
    (outdir / f"{name}.list").write_text("\n".join(shadowrocket) + "\n", encoding="utf-8")
    print(f"{name}: suffix {len(data['suffix'])}, full {len(data['full'])}, keyword {len(data['keyword'])}")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: rulesets.py <export dir> <outdir>")
    src = pathlib.Path(sys.argv[1])
    outdir = pathlib.Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        path = src / f"{category}.txt"
        if not path.exists():
            raise SystemExit(f"missing export: {path}")
        write_set(f"geosite-{category}", parse(path), outdir)


if __name__ == "__main__":
    main()