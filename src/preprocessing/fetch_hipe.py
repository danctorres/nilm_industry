"""Downloads the HIPE one-week release (KIT, CC BY 4.0, https://www.energystatusdata.kit.edu/hipe.php) and unpacks
its machine files into data/raw/HIPE/Equipment, leaving out the MainTerminal (the main meter, not a machine).

Example: python3 src/preprocessing/fetch_hipe.py [--raw DIR]
"""

import argparse
import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path

from common import REPO

URL = (
    "https://bwsyncandshare.kit.edu/s/JacGftzBH85dgGK/download?path=%2F"
    "&files=hipe_cleaned_v1.0.1_geq_2017-10-23_lt_2017-10-30.zip"
)
SHA256 = "a04344f7edf0593d9c35db68e606babfd77d28522ec0dc37ee081516836bbe2b"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", type=Path, default=REPO / "data" / "raw" / "HIPE")
    a = p.parse_args(argv)
    archive = a.raw / "hipe_cleaned_v1.0.1_geq_2017-10-23_lt_2017-10-30.zip"

    if not archive.exists():
        print(f"downloading {archive.name} (109 MB)")
        a.raw.mkdir(parents=True, exist_ok=True)
        part = archive.with_suffix(".part")
        with urllib.request.urlopen(URL) as response, part.open("wb") as f:
            shutil.copyfileobj(response, f)
        part.rename(archive)
    with archive.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != SHA256:
            raise SystemExit(f"{archive} is not the expected release; delete it and run again")

    with zipfile.ZipFile(archive) as z:
        machines = [n for n in z.namelist() if n.endswith(".csv") and not n.startswith("MainTerminal")]
        for name in machines:
            z.extract(name, a.raw / "Equipment")
    print(f"{len(machines)} machine files in {a.raw / 'Equipment'}")


if __name__ == "__main__":
    main()
