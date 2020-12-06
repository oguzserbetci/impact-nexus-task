# impact-nexus-task
## Setup
``` shell
poetry install
python -m spacy download en_core_web_md
```

## Usage
``` shell
python -m extractor -i data/ -o output/
```

```man
usage: extractor.py [-h] [--input INPUT] [--output OUTPUT]

Extract mission from scrapes.

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    Input folder where JSON files from scrape are stored
  --output OUTPUT  Output folder where mission sentences are extracted to
```
