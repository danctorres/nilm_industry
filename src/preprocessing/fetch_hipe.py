"""Downloads the HIPE three-month release (KIT, CC BY 4.0, https://www.energystatusdata.kit.edu/hipe.php, archived at
https://doi.org/10.5281/zenodo.14054902) and unpacks its machine files into data/raw/HIPE/Equipment and its
MainTerminal, the main meter, into data/raw/HIPE.

Example: python3 src/preprocessing/fetch_hipe.py [--raw DIR]
"""

import argparse
import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path

from common import REPO

ARCHIVE = "hipe_cleaned_v1.0.1_geq_2017-10-01_lt_2018-01-01.zip"
URL = f"https://zenodo.org/api/records/14054902/files/{ARCHIVE}/content"
SHA256 = "37ef3e733ff3de2fb13525421d9524b1e9d81c88ac0e0c22497634a964384716"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", type=Path, default=REPO / "data" / "raw" / "HIPE")
    a = p.parse_args(argv)
    archive = a.raw / ARCHIVE

    if not archive.exists():
        print(f"downloading {archive.name} (1.33 GB)")
        a.raw.mkdir(parents=True, exist_ok=True)
        part = archive.with_suffix(".part")
        with urllib.request.urlopen(URL) as response, part.open("wb") as f:
            shutil.copyfileobj(response, f)
        part.rename(archive)
    with archive.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != SHA256:
            raise SystemExit(f"{archive} is not the expected release; delete it and run again")

    with zipfile.ZipFile(archive) as z:
        files = [n for n in z.namelist() if n.endswith(".csv")]
        machines = [n for n in files if not n.startswith("MainTerminal")]
        # hipe.py reads every file in Equipment: files of another release would be taken for more machines
        if stale := {f.name for f in (a.raw / "Equipment").glob("*.csv")} - set(machines):
            raise SystemExit(f"{a.raw / 'Equipment'} holds files of another release, remove them: {sorted(stale)}")
        print(f"unpacking {len(files)} files (30.6 GB)")
        for name in machines:
            z.extract(name, a.raw / "Equipment")
        z.extractall(a.raw, set(files) - set(machines))
    print(f"{len(machines)} machine files in {a.raw / 'Equipment'}, the MainTerminal in {a.raw}")


if __name__ == "__main__":
    main()
