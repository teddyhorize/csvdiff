# csvdiff

A fast CLI tool to compare and highlight structural differences between CSV files.

---

## Installation

```bash
pip install csvdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff.git
cd csvdiff && pip install .
```

---

## Usage

```bash
csvdiff file1.csv file2.csv
```

**Example output:**

```
~ Row 3: "price" changed from "9.99" → "12.49"
+ Row 7: new row added [id=104, name="Widget D", price="5.00"]
- Row 9: row removed [id=106, name="Widget F", price="3.50"]

Summary: 1 modified, 1 added, 1 removed
```

**Options:**

| Flag | Description |
|------|-------------|
| `--key <col>` | Column to use as row identifier |
| `--ignore <col>` | Ignore a column during comparison |
| `--output <file>` | Write results to a file |
| `--format json` | Output results as JSON |

```bash
# Compare using "id" as the unique key, ignore "updated_at"
csvdiff file1.csv file2.csv --key id --ignore updated_at
```

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).