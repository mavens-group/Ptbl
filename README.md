# Ptbl

A GTK4 desktop periodic table. Select an element to browse its physical data,
use the search field to jump to a symbol or name, and open **Tools** for the
legacy utilities modernized for GTK4.

## Run

```bash
python3 ptbl.py
```

## Install

Install directly from a local checkout or a Git URL:

```bash
python3 -m pip install .
# or: python3 -m pip install git+https://github.com/YOUR-ACCOUNT/Ptbl.git
```

This installs the `ptbl` launcher, the data files, a GNOME desktop entry, and
the application icon beneath the selected Python environment's prefix. GTK4
and PyGObject remain system dependencies; on Fedora install `gtk4` and
`python3-gobject`, and on Debian/Ubuntu install `gir1.2-gtk-4.0` and
`python3-gi`.

Requirements: Python 3 with PyGObject and GTK 4 (`python3-gi` and `gtk4` on
most Linux distributions). The full legacy property exports are bundled in
`data/exported/`. Core atomic and thermal properties are overlaid from the
bundled PubChem periodic-table snapshot (`data/pubchem-periodic-table.json`),
retrieved through [PubChem PUG-REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest).
Specialist crystal, electrical, and nuclear values remain legacy data pending
individual source review.
