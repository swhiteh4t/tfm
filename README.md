# DarkNetScraper: Tor crawler and BERT-based content classifier

This is the code for a Master's thesis (TFM) on automatically discovering and classifying illicit content on Tor hidden services. It has three parts:

1. **`scraper/`**: *DarkNetScraper*, a command-line crawler that browses `.onion` sites through Tor, pulls text and indicators (e-mails, phone numbers, crypto wallets, IPs, cloud buckets), stores results in MongoDB and can classify each page with a fine-tuned BERT model.
2. **`dataset-construction/`**: a notebook that turns raw HTML snapshots of historical dark-net markets into a labelled CSV dataset.
3. **`trainer/`**: notebooks that fine-tune `bert-base-uncased` on that dataset for multi-class page classification.

```
.
├── scraper/                  # Tor crawler CLI (Python package: DarkNetScraper)
│   ├── DarkNetScraper/
│   │   ├── main.py           # CLI arguments and entry point
│   │   ├── binder.py         # Recursive crawl loop that ties everything together
│   │   ├── torconnector.py   # pycurl over SOCKS5 + stem (new Tor identity)
│   │   ├── extractors/       # HTML → title, meta tags, text, onion links (BeautifulSoup)
│   │   ├── parsers/          # Text cleanup, regex IOC extraction, vendored reStalker
│   │   ├── nlp/              # spaCy summariser, BERT inference (darkbert.py)
│   │   ├── datamodels.py     # MongoDB persistence and JSON/CSV export
│   │   ├── output/           # Coloured terminal output
│   │   └── config.py         # All settings, read from environment variables
│   ├── run.py
│   ├── requirements.txt
│   └── .env.example
├── dataset-construction/
│   └── dataset_parser.ipynb  # Raw market HTML → title,content,category CSV
├── trainer/
│   ├── notebooks/
│   │   ├── 01_tokenize.ipynb               # How BERT tokenisation works
│   │   └── 02_train_validate_predict.ipynb # Fine-tuning, evaluation, inference
│   └── requirements.txt
├── models/                   # Put the fine-tuned checkpoints here (not in git)
└── LICENSE                   # GPL-3.0
```

---

## 1. Scraper

### Requirements

- Python 3.9+
- A running **Tor** daemon with SOCKS (default `9050`) and **ControlPort** (default `9051`) turned on, using password authentication:
  ```
  # torrc
  SOCKSPort 9050
  ControlPort 9051
  HashedControlPassword <output of: tor --hash-password "your-password">
  ```
- A **MongoDB** instance (for example `docker run -d -p 27017:27017 mongo`)
- `libcurl` (needed by `pycurl`) and `libmagic` (needed by `python-magic`)

### Installation

```bash
cd scraper
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env        # edit the values
set -a; source .env; set +a
```

### Configuration

All settings live in `DarkNetScraper/config.py` and can be overridden with environment variables:

| Variable               | Default                                   | Purpose                              |
|------------------------|-------------------------------------------|--------------------------------------|
| `TOR_SOCKS_HOST`       | `127.0.0.1`                               | Tor SOCKS proxy host                 |
| `TOR_SOCKS_PORT`       | `9050`                                    | Tor SOCKS proxy port                 |
| `TOR_CONTROL_PORT`     | `SOCKS_PORT + 1`                          | Tor control port (identity renewal)  |
| `TOR_CONTROL_PASSWORD` | *(empty)*                                 | Tor control port password            |
| `MONGO_URI`            | `mongodb://127.0.0.1:27017/`              | MongoDB connection string            |
| `MONGO_DB_NAME`        | `DarkNetScraper`                          | Database name                        |
| `DARKNET_MODEL_PATH`   | `models/finetuned_BERT_epoch_1.model`     | BERT checkpoint used by `--predict`  |

### Usage

```bash
python run.py -u http://<address>.onion/ [options]
```

| Flag                  | Description                                                                    |
|-----------------------|--------------------------------------------------------------------------------|
| `-u, --url`           | Starting URL                                                                   |
| `-d, --depth N`       | Maximum recursion depth (default `1`)                                          |
| `-v, --verbose`       | Show exit-node IP, meta tags, an extractive summary and page content           |
| `-m, --mail`          | Extract e-mail addresses                                                       |
| `-t, --telephone`     | Extract phone numbers                                                          |
| `-a, --additional`    | Extract IPv4/IPv6 addresses, AWS S3 domains and crypto wallets                 |
| `-p, --predict`       | Classify each page with the fine-tuned BERT model                              |
| `-c, --classify`      | Label each page by hand (builds a dataset, exported to JSON/CSV)               |
| `-anon, --anonimity`  | Random User-Agent and a new Tor circuit for every request                      |
| `--ip`, `--port`      | Override the Tor SOCKS proxy address                                           |
| `--version`           | Print the version                                                              |

Example: crawl a directory site two levels deep and classify every page:

```bash
python run.py -v -p -d 2 -u http://<directory>.onion/
```

#### How it works

1. `TorConnector` fetches the page with `pycurl` through Tor's SOCKS5 proxy. Every request has a 10% chance of triggering a new Tor identity (`NEWNYM`); with `-anon` it happens on every request.
2. `Extractor` parses the HTML (title, meta tags, raw text, `.onion` links).
3. `Parser` cleans the text and runs the regex extractors. Part of the extraction uses a vendored copy of [reStalker](https://github.com/junquera/restalker) (MIT, © Javier Junquera Sánchez).
4. If `-p` is set, `DarkBert` tokenises the text (first 128 tokens) and prints the probability of each class.
5. Results go into a MongoDB collection named `Search-<timestamp>`. Visited URLs are kept in `visited.json` so the next run skips them.
6. The crawler follows every `.onion` link it finds, recursively, until it reaches `--depth`.

---

## 2. Dataset construction

`dataset-construction/dataset_parser.ipynb` walks through how raw HTML snapshots of historical dark-net markets (1776, Panacea, Tortuga 2, Assassination Market…) were:

- filtered: non-HTML files, empty listings, user profiles and "no products found" pages are removed (file type detected with `libmagic`, encoding with `chardet`);
- categorised: per-market rules map each market's own product categories to the thesis taxonomy (for example *weed, pills, opioids… → Drugs*; *money, digital goods → Fraud*);
- cleaned and exported to a `title,content,category` CSV with a multi-threaded pass.

> The raw HTML and the resulting CSV are **not** in this repository (see [Ethics](#ethics-and-responsible-use)). The notebook expects them under `./examples/<market>/`.

---

## 3. Training

`trainer/notebooks/02_train_validate_predict.ipynb` was run on Google Colab (it mounts Google Drive to save checkpoints; change `save_dir` to run it locally).

| Setting         | Value                                                       |
|-----------------|-------------------------------------------------------------|
| Base model      | `bert-base-uncased` + `BertForSequenceClassification`       |
| Classes         | `Drugs`, `Fraud`, `Services`, CSAM-related (4 labels)       |
| Class filtering | Categories with fewer than 50 samples are dropped           |
| Balancing       | `Drugs` downsampled (17,145 → 264)                          |
| Split           | 85 / 15 stratified train/validation (602 samples in total)  |
| Max length      | 512 tokens (training); 128 tokens (inference in the scraper)|
| Optimiser       | AdamW, lr `1e-5`, eps `1e-8`, linear schedule, 5 epochs     |
| Batch size      | 3                                                           |

### Results (validation set, 91 samples)

| Epoch | Train loss | Val loss | Weighted F1 |
|-------|-----------:|---------:|------------:|
| 1     | 0.600      | 0.194    | 0.978       |
| 2     | 0.096      | 0.084    | 0.968       |
| 3     | 0.025      | 0.025    | 1.000       |
| 4     | 0.008      | 0.010    | 1.000       |
| 5     | 0.006      | 0.009    | 1.000       |

Per-class accuracy of the epoch-1 checkpoint (the one the scraper uses): Drugs 39/40 (97.5%), Fraud 15/16 (93.8%), Services 10/10, CSAM-related 25/25.

> The validation set is small and comes from a handful of markets, so these numbers are optimistic and probably do not reflect how well the model generalises to arbitrary hidden services.

### Using a trained model

Model checkpoints are about 440 MB each and are not stored in git. Put `finetuned_BERT_epoch_1.model` in `models/` (or point `DARKNET_MODEL_PATH` at it). See [`models/README.md`](models/README.md).

---

## Ethics and responsible use

This project was built for **academic research** into automated detection of illegal content, to support law-enforcement and threat-intelligence work.

- **No scraped content is distributed.** The raw HTML snapshots, the labelled dataset and the crawl logs are deliberately kept out of this repository, because they contain material from illegal marketplaces, including CSAM-related listings. Do not add them.
- Crawling hidden services can expose you to illegal material. Make sure your work is legal where you are and approved by your institution's ethics board **before** running the crawler.
- The crawler fetches text only. Do not change it to download images or media.
- If you come across child sexual abuse material, report it to your national hotline (see [INHOPE](https://www.inhope.org/)) or to law enforcement. Do not store or share it.

## License

Released under the **GNU General Public License v3.0**; see [LICENSE](LICENSE).
The vendored reStalker code in `scraper/DarkNetScraper/parsers/regex/` keeps its original MIT license.
