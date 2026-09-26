from pathlib import Path

from setuptools import setup


ROOT = Path(__file__).parent

setup(
    name="ptbl",
    version="2.0.0",
    description="A GTK4 periodic table",
    long_description=(ROOT / "README.md").read_text(),
    long_description_content_type="text/markdown",
    license="GPL-3.0-or-later",
    python_requires=">=3.10",
    py_modules=["ptbl"],
    entry_points={"console_scripts": ["ptbl=ptbl:main"]},
    data_files=[
        ("share/ptbl/data", [
            "data/elements.db",
            "data/pubchem-periodic-table.json",
        ]),
        ("share/ptbl/data/exported",
         [str(path) for path in sorted((ROOT / "data/exported").glob("*.json"))]),
        ("share/applications", ["data/org.rudra.Ptbl.desktop"]),
        ("share/icons/hicolor/scalable/apps",
         ["data/icons/hicolor/scalable/apps/org.rudra.Ptbl.svg"]),
    ],
    classifiers=[
        "Environment :: X11 Applications :: GTK",
        "Programming Language :: Python :: 3",
        "Topic :: Education :: Chemistry",
    ],
)
