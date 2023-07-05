import sruthi
import csv
import sys
import traceback

records = sruthi.searchretrieve(
    "https://amsquery.stadt-zuerich.ch/SRU/",
    query="isad.reference = V.B.b.43.:1 AND isad.descriptionlevel = Dossier",
)

try:
    header = [
        "reference",
        "title",
        "year",
        "url",
    ]
    writer = csv.DictWriter(
        sys.stdout,
        header,
        delimiter=",",
        quotechar='"',
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()

    for record in records:
        row = {
            "reference": record["reference"],
            "title": record["title"],
            "year": record["date"],
            "url": record["extra"]["link"],
        }
        writer.writerow(row)
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
finally:
    sys.stdout.flush()
