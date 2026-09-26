#!/usr/bin/env python3
"""GTK4 & Libadwaita Periodic Table with Material You / GNOME HIG styling."""

from __future__ import annotations

import json
import math
import re
import site
import sys
import sysconfig
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango

APP_ID = "org.rudra.Ptbl"


def find_data_root():
  """Find data when run from source or installed with pip."""
  candidates = (
      Path(__file__).with_name("data"),
      Path(sysconfig.get_path("data")) / "share" / "ptbl" / "data",
      Path(site.USER_BASE) / "share" / "ptbl" / "data",
  )
  for candidate in candidates:
    if candidate.is_dir():
      return candidate
  raise FileNotFoundError("Ptbl data files were not installed")


DATA_ROOT = find_data_root()
DATA_DIR = DATA_ROOT / "exported"
PUBCHEM_PATH = DATA_ROOT / "pubchem-periodic-table.json"

# (atomic number, symbol, name, grid column, grid row, category)
ELEMENTS = [
    (1, "H", "Hydrogen", 1, 1, "nonmetal"),
    (2, "He", "Helium", 18, 1, "noble"),
    (3, "Li", "Lithium", 1, 2, "alkali"),
    (4, "Be", "Beryllium", 2, 2, "alkaline"),
    (5, "B", "Boron", 13, 2, "metalloid"),
    (6, "C", "Carbon", 14, 2, "nonmetal"),
    (7, "N", "Nitrogen", 15, 2, "nonmetal"),
    (8, "O", "Oxygen", 16, 2, "nonmetal"),
    (9, "F", "Fluorine", 17, 2, "halogen"),
    (10, "Ne", "Neon", 18, 2, "noble"),
    (11, "Na", "Sodium", 1, 3, "alkali"),
    (12, "Mg", "Magnesium", 2, 3, "alkaline"),
    (13, "Al", "Aluminium", 13, 3, "post"),
    (14, "Si", "Silicon", 14, 3, "metalloid"),
    (15, "P", "Phosphorus", 15, 3, "nonmetal"),
    (16, "S", "Sulfur", 16, 3, "nonmetal"),
    (17, "Cl", "Chlorine", 17, 3, "halogen"),
    (18, "Ar", "Argon", 18, 3, "noble"),
    (19, "K", "Potassium", 1, 4, "alkali"),
    (20, "Ca", "Calcium", 2, 4, "alkaline"),
    *[(n, s, name, n - 18, 4, "transition")
      for n, s, name in [(21, "Sc", "Scandium"), (22, "Ti", "Titanium"),
                         (23, "V", "Vanadium"), (24, "Cr", "Chromium"),
                         (25, "Mn", "Manganese"), (26, "Fe", "Iron"),
                         (27, "Co", "Cobalt"), (28, "Ni", "Nickel"),
                         (29, "Cu", "Copper"), (30, "Zn", "Zinc")]],
    (31, "Ga", "Gallium", 13, 4, "post"),
    (32, "Ge", "Germanium", 14, 4, "metalloid"),
    (33, "As", "Arsenic", 15, 4, "metalloid"),
    (34, "Se", "Selenium", 16, 4, "nonmetal"),
    (35, "Br", "Bromine", 17, 4, "halogen"),
    (36, "Kr", "Krypton", 18, 4, "noble"),
    (37, "Rb", "Rubidium", 1, 5, "alkali"),
    (38, "Sr", "Strontium", 2, 5, "alkaline"),
    *[(n, s, name, n - 36, 5, "transition")
      for n, s, name in [(39, "Y", "Yttrium"), (40, "Zr", "Zirconium"),
                         (41, "Nb", "Niobium"), (42, "Mo", "Molybdenum"),
                         (43, "Tc", "Technetium"), (44, "Ru", "Ruthenium"),
                         (45, "Rh", "Rhodium"), (46, "Pd", "Palladium"),
                         (47, "Ag", "Silver"), (48, "Cd", "Cadmium")]],
    (49, "In", "Indium", 13, 5, "post"),
    (50, "Sn", "Tin", 14, 5, "post"),
    (51, "Sb", "Antimony", 15, 5, "metalloid"),
    (52, "Te", "Tellurium", 16, 5, "metalloid"),
    (53, "I", "Iodine", 17, 5, "halogen"),
    (54, "Xe", "Xenon", 18, 5, "noble"),
    (55, "Cs", "Caesium", 1, 6, "alkali"),
    (56, "Ba", "Barium", 2, 6, "alkaline"),
    (57, "La", "Lanthanum", 3, 6, "lanthanide"),
    *[(n, s, name, n - 68, 6, "transition") for n, s, name in
      [(72, "Hf", "Hafnium"), (73, "Ta", "Tantalum"), (74, "W", "Tungsten"),
       (75, "Re", "Rhenium"), (76, "Os", "Osmium"), (77, "Ir", "Iridium"),
       (78, "Pt", "Platinum"), (79, "Au", "Gold"), (80, "Hg", "Mercury")]],
    (81, "Tl", "Thallium", 13, 6, "post"),
    (82, "Pb", "Lead", 14, 6, "post"),
    (83, "Bi", "Bismuth", 15, 6, "post"),
    (84, "Po", "Polonium", 16, 6, "metalloid"),
    (85, "At", "Astatine", 17, 6, "halogen"),
    (86, "Rn", "Radon", 18, 6, "noble"),
    (87, "Fr", "Francium", 1, 7, "alkali"),
    (88, "Ra", "Radium", 2, 7, "alkaline"),
    (89, "Ac", "Actinium", 3, 7, "actinide"),
    *[(n, s, name, n - 100, 7, "transition")
      for n, s, name in [(104, "Rf", "Rutherfordium"), (105, "Db", "Dubnium"),
                         (106, "Sg", "Seaborgium"), (107, "Bh", "Bohrium"),
                         (108, "Hs", "Hassium"), (109, "Mt", "Meitnerium"),
                         (110, "Ds", "Darmstadtium"),
                         (111, "Rg", "Roentgenium"), (112, "Cn", "Copernicium")]],
    (113, "Nh", "Nihonium", 13, 7, "post"),
    (114, "Fl", "Flerovium", 14, 7, "post"),
    (115, "Mc", "Moscovium", 15, 7, "post"),
    (116, "Lv", "Livermorium", 16, 7, "post"),
    (117, "Ts", "Tennessine", 17, 7, "halogen"),
    (118, "Og", "Oganesson", 18, 7, "noble"),
    *[(n, s, name, n - 54, 9, "lanthanide")
      for n, s, name in [(58, "Ce", "Cerium"), (59, "Pr", "Praseodymium"),
                         (60, "Nd", "Neodymium"), (61, "Pm", "Promethium"),
                         (62, "Sm", "Samarium"), (63, "Eu", "Europium"),
                         (64, "Gd", "Gadolinium"), (65, "Tb", "Terbium"),
                         (66, "Dy", "Dysprosium"), (67, "Ho", "Holmium"),
                         (68, "Er", "Erbium"), (69, "Tm", "Thulium"),
                         (70, "Yb", "Ytterbium"), (71, "Lu", "Lutetium")]],
    *[(n, s, name, n - 86, 10, "actinide")
      for n, s, name in [(90, "Th", "Thorium"), (91, "Pa", "Protactinium"),
                         (92, "U", "Uranium"), (93, "Np", "Neptunium"),
                         (94, "Pu", "Plutonium"), (95, "Am", "Americium"),
                         (96, "Cm", "Curium"), (97, "Bk", "Berkelium"),
                         (98, "Cf", "Californium"), (99, "Es", "Einsteinium"),
                         (100, "Fm", "Fermium"), (101, "Md", "Mendelevium"),
                         (102, "No", "Nobelium"), (103, "Lr", "Lawrencium")]],
]

TABS = {
    "Overview": [
        "Symbol", "Atomic number", "Atomic mass (u)", "Oxidation states",
        "Electronegativity", "Electron affinity (kJ/mol)"
    ],
    "Thermal": [
        "Phase", "Melting point", "Boiling point", "Critical pressure",
        "Critical temperature", "Heat of fusion", "Heat of vaporization",
        "Specific heat", "Adiabatic index", "Neel point", "Curie point"
    ],
    "Crystal": [
        "Atomic radius (Å)", "Covalent radius (Å)", "van der Waals radius (Å)",
        "Crystal structure", "Lattice parameter a (Å)",
        "Lattice parameter b (Å)", "Lattice parameter c (Å)", "Space group",
        "Space group number"
    ],
    "Electronic": [
        "Electron configuration", "Magnetic type", "Mass susceptibility",
        "Molar susceptibility"
    ],
    "Electrical": [
        "Electrical type", "Conductivity", "Resistivity",
        "Superconducting point"
    ],
    "Nuclear": [
        "Half life", "Mean life", "Decay mode", "Quantum numbers",
        "Cross section", "Neutron mass absorption"
    ],
}

CATEGORY_NAMES = {
    "alkali": "Alkali metals",
    "alkaline": "Alkaline earth metals",
    "transition": "Transition metals",
    "post": "Post-transition metals",
    "metalloid": "Metalloids",
    "nonmetal": "Other nonmetals",
    "halogen": "Halogens",
    "noble": "Noble gases",
    "lanthanide": "Lanthanides",
    "actinide": "Actinides",
}

CATEGORY_SHORT = {
    "alkali": "Alkali",
    "alkaline": "Alkaline Earth",
    "transition": "Transition",
    "post": "Post-Transition",
    "metalloid": "Metalloid",
    "nonmetal": "Nonmetal",
    "halogen": "Halogen",
    "noble": "Noble Gas",
    "lanthanide": "Lanthanide",
    "actinide": "Actinide",
}


def load_exported_data():
  """Load legacy specialist data and overlay current PubChem core properties."""
  raw = {
      table: json.loads((DATA_DIR / f"{table}.json").read_text())
      for table in TABS
  }
  current_names = {row["Properties"]: row["Name"] for row in raw["Overview"]}
  data = {}
  for table, rows in raw.items():
    selected = {}
    for row in rows:
      number = int(row["Properties"])
      if number not in selected or row["Name"] == current_names.get(
          row["Properties"]):
        selected[number] = row
    data[table] = selected
  refresh_core_properties(data)
  return data


def superscript_configuration(value):
  superscripts = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
  return re.sub(
      r"([spdfg])(\d+)",
      lambda match: match.group(1) + match.group(2).translate(superscripts),
      value)


def refresh_core_properties(data):
  """Overlay fields supplied by PubChem's documented periodic-table feed."""
  table = json.loads(PUBCHEM_PATH.read_text())["Table"]
  columns = table["Columns"]["Column"]
  for row in table["Row"]:
    source = dict(zip(columns, row["Cell"]))
    number = int(source["AtomicNumber"])
    overview = data["Overview"][number]
    overview["Weight"] = source["AtomicMass"]
    if source["OxidationStates"]:
      overview["Val"] = source["OxidationStates"]
    if source["Electronegativity"]:
      overview["Eneg"] = source["Electronegativity"]
    if source["ElectronAffinity"]:
      overview["Eaff"] = f"{float(source['ElectronAffinity']) * 96.485:.3f}"

    electronic = data["Electronic"][number]
    if source["ElectronConfiguration"]:
      electronic["Econf"] = superscript_configuration(
          source["ElectronConfiguration"])

    thermal = data["Thermal"][number]
    if source["StandardState"]:
      thermal["Phase"] = source["StandardState"]
    if source["MeltingPoint"]:
      thermal["AbM"] = f"{source['MeltingPoint']} K"
    if source["BoilingPoint"]:
      thermal["AbB"] = f"{source['BoilingPoint']} K"


CSS = """
/* Modern GNOME HIG & Material You Tonal Theme */

button.element-card {
  min-width: 44px;
  min-height: 48px;
  margin: 1px;
  border-radius: 6px;
  padding: 2px 3px;
  border: none;
  box-shadow: none;
  transition: background 150ms ease-out;
  color: #1b1b1f;
}

button.element-card:active {
  filter: brightness(0.92);
}

.element-card:focus-visible {
  outline: 2px solid @accent_color;
  outline-offset: 2px;
}

.symbol {
  font-size: 13.5pt;
  font-weight: 750;
  letter-spacing: -0.3px;
}

.number {
  font-size: 8.5pt;
  font-weight: 600;
}

/* Solid category fills; dark text keeps contrast >= 5.8:1 on every one. */
.hero-card.alkali, button.element-card.alkali { background: #F0876A; background-image: none; color: #1b1b1f; }
button.element-card.alkali:hover { background: #F5A88F; }
.hero-card.alkaline, button.element-card.alkaline { background: #F2B84B; background-image: none; color: #1b1b1f; }
button.element-card.alkaline:hover { background: #F7CB76; }
.hero-card.transition, button.element-card.transition { background: #6FCB8A; background-image: none; color: #1b1b1f; }
button.element-card.transition:hover { background: #93DAA8; }
.hero-card.post, button.element-card.post { background: #5BB0EA; background-image: none; color: #1b1b1f; }
button.element-card.post:hover { background: #82C4F0; }
.hero-card.metalloid, button.element-card.metalloid { background: #4FCFC0; background-image: none; color: #1b1b1f; }
button.element-card.metalloid:hover { background: #7CDCD0; }
.hero-card.nonmetal, button.element-card.nonmetal { background: #B49AF0; background-image: none; color: #1b1b1f; }
button.element-card.nonmetal:hover { background: #C8B5F5; }
.hero-card.halogen, button.element-card.halogen { background: #EE7FB6; background-image: none; color: #1b1b1f; }
button.element-card.halogen:hover { background: #F4A3CB; }
.hero-card.noble, button.element-card.noble { background: #7F9BF0; background-image: none; color: #1b1b1f; }
button.element-card.noble:hover { background: #A0B6F5; }
.hero-card.lanthanide, button.element-card.lanthanide { background: #E8996A; background-image: none; color: #1b1b1f; }
button.element-card.lanthanide:hover { background: #EFB392; }
.hero-card.actinide, button.element-card.actinide { background: #E5737F; background-image: none; color: #1b1b1f; }
button.element-card.actinide:hover { background: #EC959E; }

.hero-card {
  border-radius: 16px;
  padding: 16px 20px;
  border: 1px solid alpha(currentColor, 0.12);
  margin-bottom: 8px;
}
.hero-symbol {
  font-size: 32pt;
  font-weight: 850;
  letter-spacing: -1px;
}
.hero-title {
  font-size: 16pt;
  font-weight: 700;
}
.hero-number {
  font-size: 11pt;
  font-weight: 600;
  opacity: 0.72;
}


.property-value {
  font-feature-settings: 'tnum';
  font-weight: 500;
}
.dim-label {
  opacity: 0.62;
}
.badge-label {
  font-size: 9pt;
  font-weight: 600;
  border-radius: 8px;
  padding: 3px 8px;
  background: alpha(currentColor, 0.08);
}
"""


class PeriodicTable(Adw.Application):

  def __init__(self):
    super().__init__(application_id=APP_ID,
                     flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
    self.elements = {
        number: (symbol, name, category)
        for number, symbol, name, _col, _row, category in ELEMENTS
    }
    self.data = load_exported_data()

  def do_startup(self):
    Adw.Application.do_startup(self)
    provider = Gtk.CssProvider()
    provider.load_from_string(CSS)
    display = Gdk.Display.get_default()
    if display:
      Gtk.StyleContext.add_provider_for_display(
          display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    for name, callback in (("about", self.show_about),
                           ("vegard", self.show_vegard)):
      action = Gio.SimpleAction.new(name, None)
      action.connect("activate", callback)
      self.add_action(action)

    for key in ("atomic-radius", "covalent-radius", "vdw-radius",
                "electron-affinity"):
      action = Gio.SimpleAction.new(key, None)
      action.connect("activate", self.show_trend, key)
      self.add_action(action)

    quit_action = Gio.SimpleAction.new("quit", None)
    quit_action.connect("activate", lambda *_: self.quit())
    self.add_action(quit_action)

  def do_activate(self):
    win = self.props.active_window
    if not win:
      win = MainWindow(self)
    win.present()

  def show_about(self, *_):
    parent = self.props.active_window
    about = Adw.AboutDialog(
        application_name="Ptbl",
        application_icon=APP_ID,
        developer_name="Rudra Banerjee",
        version="2.0.0",
        comments="A modern GTK4 and Libadwaita periodic table.",
        website="https://github.com/rudrab/PeriodicTable",
        issue_url="https://github.com/rudrab/PeriodicTable/issues",
        license_type=Gtk.License.GPL_3_0,
        developers=["Rudra Banerjee"],
    )
    about.present(parent)

  def show_vegard(self, *_):
    VegardWindow(self).present()

  def show_trend(self, _action, _parameter, key):
    TrendWindow(self, key).present()


class MainWindow(Adw.ApplicationWindow):

  def __init__(self, app):
    super().__init__(application=app,
                     title="Periodic Table",
                     default_width=920,
                     default_height=600)

    toolbar_view = Adw.ToolbarView()
    self.set_content(toolbar_view)

    header = Adw.HeaderBar()
    title_widget = Adw.WindowTitle(title="Periodic Table", subtitle="Ptbl")
    header.set_title_widget(title_widget)
    toolbar_view.add_top_bar(header)

    self.search = Gtk.SearchEntry(placeholder_text="Find element by symbol or name…")
    self.search.set_width_chars(22)
    self.search.connect("search-changed", self.filter_elements)
    self.search.connect("activate", self.open_first_match)
    header.pack_start(self.search)

    menu = Gio.Menu()
    tools = Gio.Menu()
    tools.append("Vegard’s law", "app.vegard")
    tools.append("Atomic radius trend", "app.atomic-radius")
    tools.append("Covalent radius trend", "app.covalent-radius")
    tools.append("van der Waals radius trend", "app.vdw-radius")
    tools.append("Electron affinity trend", "app.electron-affinity")
    menu.append_submenu("Tools & Trends", tools)
    menu.append("About Ptbl", "app.about")
    menu.append("Quit", "app.quit")

    menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic",
                                 menu_model=menu)
    menu_button.set_tooltip_text("Main menu")
    header.pack_end(menu_button)

    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                    spacing=4,
                    margin_top=6,
                    margin_bottom=6,
                    margin_start=8,
                    margin_end=8)

    scroller = Gtk.ScrolledWindow(vexpand=True,
                                  hexpand=True,
                                  propagate_natural_width=True,
                                  propagate_natural_height=True,
                                  hscrollbar_policy=Gtk.PolicyType.NEVER,
                                  vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
    outer.append(scroller)

    content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                          spacing=4,
                          halign=Gtk.Align.FILL,
                          valign=Gtk.Align.FILL,
                          hexpand=True,
                          vexpand=True,
                          margin_top=2,
                          margin_bottom=2)
    scroller.set_child(content_box)

    self.grid = Gtk.Grid(column_spacing=2,
                         row_spacing=2,
                         column_homogeneous=True,
                         row_homogeneous=True,
                         halign=Gtk.Align.FILL,
                         valign=Gtk.Align.FILL,
                         hexpand=True,
                         vexpand=True)
    content_box.append(self.grid)

    self.cards = []
    for number, symbol, name, col, row, category in ELEMENTS:
      card = self.element_card(number, symbol, name, category)
      self.grid.attach(card, col - 1, row - 1, 1, 1)
      self.cards.append((card, symbol, name, category))

    lanth_label = Gtk.Label(label="57–71  Lanthanides", xalign=1)
    lanth_label.add_css_class("badge-label")
    lanth_label.add_css_class("dim-label")
    self.grid.attach(lanth_label, 0, 8, 3, 1)

    act_label = Gtk.Label(label="89–103  Actinides", xalign=1)
    act_label.add_css_class("badge-label")
    act_label.add_css_class("dim-label")
    self.grid.attach(act_label, 0, 9, 3, 1)

    toolbar_view.set_content(outer)

  def element_card(self, number, symbol, name, category):
    card = Gtk.Button(hexpand=True, vexpand=True)
    card.add_css_class("element-card")
    card.update_property([Gtk.AccessibleProperty.LABEL], [f"{name}, atomic number {number}"])
    card.add_css_class(category)
    card.set_tooltip_text(f"{name} ({number})\nCategory: {CATEGORY_NAMES[category]}")
    card.set_cursor_from_name("pointer")

    card.connect("clicked", lambda *_: self.open_element(number))

    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    num = Gtk.Label(label=str(number), xalign=0)
    num.add_css_class("number")
    inner.append(num)

    sym = Gtk.Label(label=symbol, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, vexpand=True)
    sym.add_css_class("symbol")
    inner.append(sym)
    card.set_child(inner)

    return card

  def open_element(self, number):
    ElementWindow(self.get_application(), number, parent=self).present()

  def open_first_match(self, _entry):
    for card, _symbol, _name, _category in self.cards:
      if card.get_visible():
        card.emit("clicked")
        return

  def filter_elements(self, _entry):
    query = self.search.get_text().strip().casefold()
    for card, symbol, name, _category in self.cards:
      matches = not query or (query in symbol.casefold() or query in name.casefold())
      card.set_visible(matches)


class ElementWindow(Adw.Window):

  def __init__(self, app, number, parent=None):
    symbol, fallback_name, category = app.elements[number]
    overview = app.data["Overview"].get(number, {})
    name = overview.get("Name", fallback_name)
    weight = overview.get("Weight", "—")

    super().__init__(application=app,
                     title=f"{name} ({symbol})",
                     default_width=640,
                     default_height=600,
                     transient_for=parent)

    toolbar_view = Adw.ToolbarView()
    self.set_content(toolbar_view)

    header = Adw.HeaderBar()
    title_widget = Adw.WindowTitle(title=f"{name} ({symbol})",
                                   subtitle=f"Atomic No. {number} • {CATEGORY_NAMES[category]}")
    header.set_title_widget(title_widget)
    toolbar_view.add_top_bar(header)

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                       spacing=12,
                       margin_top=14,
                       margin_bottom=14,
                       margin_start=16,
                       margin_end=16)

    # Hero card with M3 tonal container styling
    hero = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                   spacing=16)
    hero.add_css_class("hero-card")
    hero.add_css_class(category)

    sym_label = Gtk.Label(label=symbol)
    sym_label.add_css_class("hero-symbol")
    hero.append(sym_label)

    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                       valign=Gtk.Align.CENTER,
                       spacing=3,
                       hexpand=True)
    title_lbl = Gtk.Label(label=name, xalign=0)
    title_lbl.add_css_class("hero-title")
    info_box.append(title_lbl)

    sub_lbl = Gtk.Label(
        label=f"Atomic mass: {weight} u  •  Atomic number: {number}",
        xalign=0)
    sub_lbl.add_css_class("hero-number")
    info_box.append(sub_lbl)
    hero.append(info_box)

    badge = Gtk.Label(label=CATEGORY_NAMES[category], valign=Gtk.Align.CENTER)
    badge.add_css_class("badge-label")
    hero.append(badge)

    main_box.append(hero)

    # ViewStack and ViewSwitcher
    stack = Adw.ViewStack(vexpand=True)
    switcher = Adw.ViewSwitcher(stack=stack, halign=Gtk.Align.CENTER)
    main_box.append(switcher)
    main_box.append(stack)

    icons = {
        "Overview": "view-list-bullet-symbolic",
        "Thermal": "weather-clear-symbolic",
        "Crystal": "system-run-symbolic",
        "Electronic": "network-wired-symbolic",
        "Electrical": "battery-symbolic",
        "Nuclear": "emblem-synchronizing-symbolic",
    }

    for table, labels in TABS.items():
      row_data = app.data[table].get(number, {})
      values = list(row_data.values())[2:]
      page = self.build_properties_page(labels, values)
      icon = icons.get(table, "document-properties-symbolic")
      stack.add_titled_with_icon(page, table, table, icon)

    toolbar_view.set_content(main_box)

  @staticmethod
  def build_properties_page(labels, values):
    page = Adw.PreferencesPage()
    group = Adw.PreferencesGroup()
    page.add(group)

    for label, value in zip(labels, values):
      val_str = str(value) if value not in (None, "", "N/A") else "—"
      row = Adw.ActionRow(title=label)
      val_label = Gtk.Label(label=val_str,
                            valign=Gtk.Align.CENTER,
                            halign=Gtk.Align.END,
                            selectable=True,
                            wrap=True,
                            wrap_mode=Pango.WrapMode.WORD_CHAR,
                            max_width_chars=36)
      val_label.add_css_class("property-value")
      if val_str == "—":
        val_label.add_css_class("dim-label")
      else:
        val_label.add_css_class("accent")
      row.add_suffix(val_label)
      group.add(row)

    return page


class VegardWindow(Adw.Window):

  def __init__(self, app):
    super().__init__(application=app,
                     title="Vegard’s Law",
                     default_width=560,
                     default_height=460)
    self.app = app

    toolbar_view = Adw.ToolbarView()
    self.set_content(toolbar_view)

    header = Adw.HeaderBar()
    header.set_title_widget(Adw.WindowTitle(title="Vegard’s Law", subtitle="Alloy parameter estimation"))
    toolbar_view.add_top_bar(header)

    clamp = Adw.Clamp(maximum_size=520, margin_top=16, margin_bottom=16, margin_start=16, margin_end=16)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    clamp.set_child(box)

    pref_group = Adw.PreferencesGroup(
        title="Composition",
        description="Estimate composition-weighted lattice parameters and atomic weight using element percentages totaling 100% (e.g. Cu50Zn50).")
    box.append(pref_group)

    entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    self.entry = Gtk.Entry(text="Cu50Zn50", hexpand=True)
    self.entry.connect("activate", self.calculate)
    calc_btn = Gtk.Button(label="Calculate")
    calc_btn.add_css_class("suggested-action")
    calc_btn.connect("clicked", self.calculate)
    entry_box.append(self.entry)
    entry_box.append(calc_btn)
    pref_group.add(entry_box)

    self.result_group = Adw.PreferencesGroup(title="Estimated Properties")
    box.append(self.result_group)

    self.row_weight = Adw.ActionRow(title="Atomic weight")
    self.lbl_weight = Gtk.Label(label="—", selectable=True)
    self.lbl_weight.add_css_class("property-value")
    self.row_weight.add_suffix(self.lbl_weight)
    self.result_group.add(self.row_weight)

    self.row_latpar = Adw.ActionRow(title="Lattice parameters")
    self.lbl_latpar = Gtk.Label(label="—", selectable=True)
    self.lbl_latpar.add_css_class("property-value")
    self.row_latpar.add_suffix(self.lbl_latpar)
    self.result_group.add(self.row_latpar)

    self.row_vol = Adw.ActionRow(title="Estimated cell volume")
    self.lbl_vol = Gtk.Label(label="—", selectable=True)
    self.lbl_vol.add_css_class("property-value")
    self.row_vol.add_suffix(self.lbl_vol)
    self.result_group.add(self.row_vol)

    self.status_label = Gtk.Label(label="", wrap=True, xalign=0)
    self.status_label.add_css_class("dim-label")
    box.append(self.status_label)

    toolbar_view.set_content(clamp)
    self.calculate()

  def calculate(self, *_):
    formula = self.entry.get_text().strip()
    parts = re.findall(r"([A-Z][a-z]?)(\d+(?:\.\d+)?)", formula)
    if not parts or sum(float(pct) for _, pct in parts) != 100:
      self.status_label.set_label(
          "Please enter valid element symbols with percentages totaling 100 (e.g. Cu50Zn50, Fe70Ni30).")
      self.lbl_weight.set_label("—")
      self.lbl_latpar.set_label("—")
      self.lbl_vol.set_label("—")
      return

    totals = [0.0, 0.0, 0.0]
    weight = 0.0
    for symbol, percentage in parts:
      number = next((n for n, row in self.app.data["Overview"].items()
                     if row["Symbol"] == symbol), None)
      row = self.app.data["Crystal"].get(number) if number else None
      if not row:
        self.status_label.set_label(f"Element '{symbol}' not found in database.")
        return
      fraction = float(percentage) / 100
      try:
        weight += float(self.app.data["Overview"][number]["Weight"]) * fraction
        for i, field in enumerate(("latpar1", "latpar2", "latpar3")):
          totals[i] += float(row[field]) * fraction
      except (TypeError, ValueError):
        self.status_label.set_label(f"Lattice data for '{symbol}' is incomplete for calculation.")
        return

    volume = math.prod(totals)
    self.status_label.set_label(f"Calculation complete for {formula}.")
    self.lbl_weight.set_label(f"{weight:.4f} u")
    self.lbl_latpar.set_label(f"a = {totals[0]:.4f} Å,  b = {totals[1]:.4f} Å,  c = {totals[2]:.4f} Å")
    self.lbl_vol.set_label(f"{volume:.4f} Å³")


class TrendWindow(Adw.Window):
  METRICS = {
      "atomic-radius": ("Crystal", "Atomrad", "Atomic radius", "Å"),
      "covalent-radius": ("Crystal", "covrad", "Covalent radius", "Å"),
      "vdw-radius": ("Crystal", "vandrad", "van der Waals radius", "Å"),
      "electron-affinity": ("Overview", "Eaff", "Electron affinity", "kJ/mol")
  }

  def __init__(self, app, key):
    table, field, title, unit = self.METRICS[key]
    super().__init__(application=app,
                     title=f"{title} Trend",
                     default_width=820,
                     default_height=540)
    self.app = app
    self.current_key = key
    self.title, self.unit = title, unit

    toolbar_view = Adw.ToolbarView()
    self.set_content(toolbar_view)

    header = Adw.HeaderBar()
    self.title_widget = Adw.WindowTitle(title=f"{title} Trend", subtitle=f"Unit: {unit}")
    header.set_title_widget(self.title_widget)
    toolbar_view.add_top_bar(header)

    # Metric dropdown switcher in header
    dropdown_model = Gtk.StringList.new([
        "Atomic radius",
        "Covalent radius",
        "van der Waals radius",
        "Electron affinity",
    ])
    dropdown_keys = ["atomic-radius", "covalent-radius", "vdw-radius", "electron-affinity"]
    self.dropdown = Gtk.DropDown.new(dropdown_model, None)
    self.dropdown.set_selected(dropdown_keys.index(key))
    self.dropdown.connect("notify::selected", self.on_dropdown_changed)
    header.pack_end(self.dropdown)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                  spacing=8,
                  margin_top=14,
                  margin_bottom=14,
                  margin_start=18,
                  margin_end=18)

    self.hover_badge = Gtk.Label(
        label="Hover or move over data points to inspect elements", xalign=0)
    self.hover_badge.add_css_class("badge-label")
    self.hover_badge.add_css_class("dim-label")

    self.chart = Gtk.DrawingArea(vexpand=True, hexpand=True)
    self.chart.set_draw_func(self.draw_chart)

    motion = Gtk.EventControllerMotion()
    motion.connect("motion", self.on_chart_motion)
    motion.connect("leave", self.on_chart_leave)
    self.chart.add_controller(motion)

    box.append(self.chart)
    box.append(self.hover_badge)
    toolbar_view.set_content(box)

    self.load_points(key)

  def on_dropdown_changed(self, dropdown, _pspec):
    dropdown_keys = ["atomic-radius", "covalent-radius", "vdw-radius", "electron-affinity"]
    selected_idx = dropdown.get_selected()
    new_key = dropdown_keys[selected_idx]
    self.load_points(new_key)
    self.chart.queue_draw()

  def load_points(self, key):
    table, field, title, unit = self.METRICS[key]
    self.title, self.unit = title, unit
    self.title_widget.set_title(f"{title} Trend")
    self.title_widget.set_subtitle(f"Unit: {unit}")
    self.points = []
    for number, row in self.app.data[table].items():
      try:
        self.points.append((float(number), float(row[field]), row["Name"]))
      except (TypeError, ValueError):
        pass

  def chart_bounds(self, width, height):
    return 78, 24, width - 24, height - 52

  def chart_scale(self, width, height):
    if not self.points:
      return 0, 1, lambda n, v: (0, 0)
    maximum = max(p[1] for p in self.points)
    minimum = min(p[1] for p in self.points)
    span = maximum - minimum or max(abs(maximum), 1)
    lower = minimum - span * .08
    upper = maximum + span * .08
    left, top, right, bottom = self.chart_bounds(width, height)

    def point(number, value):
      x = left + (number - 1) / 117 * (right - left)
      y = bottom - (value - lower) / (upper - lower) * (bottom - top)
      return x, y

    return lower, upper, point

  @staticmethod
  def format_tick(value):
    if abs(value) >= 100:
      return f"{value:.0f}"
    if abs(value) >= 10:
      return f"{value:.1f}"
    return f"{value:.2f}"

  @staticmethod
  def set_theme_color(cr, rgba, alpha=1.0):
    cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha * alpha)

  def draw_chart(self, area, cr, width, height):
    if not self.points:
      return
    foreground = area.get_style_context().get_color()
    left, top, right, bottom = self.chart_bounds(width, height)
    lower, upper, point = self.chart_scale(width, height)
    cr.set_font_size(10.5)

    # Y grid and labels
    for tick in range(6):
      value = lower + (upper - lower) * tick / 5
      y = bottom - (bottom - top) * tick / 5
      self.set_theme_color(cr, foreground, .14)
      cr.set_dash([3.0, 3.0], 0)
      cr.move_to(left, y)
      cr.line_to(right, y)
      cr.stroke()
      cr.set_dash([], 0)
      self.set_theme_color(cr, foreground, .72)
      text = self.format_tick(value)
      cr.move_to(left - 8 - cr.text_extents(text).width, y + 4)
      cr.show_text(text)

    # X grid and labels
    for number in (1, 20, 40, 60, 80, 100, 118):
      x, _ = point(number, lower)
      self.set_theme_color(cr, foreground, .10)
      cr.set_dash([3.0, 3.0], 0)
      cr.move_to(x, top)
      cr.line_to(x, bottom)
      cr.stroke()
      cr.set_dash([], 0)
      self.set_theme_color(cr, foreground, .72)
      text = str(number)
      cr.move_to(x - cr.text_extents(text).width / 2, bottom + 18)
      cr.show_text(text)

    # Axes
    self.set_theme_color(cr, foreground, .80)
    cr.set_line_width(1)
    cr.move_to(left, top)
    cr.line_to(left, bottom)
    cr.line_to(right, bottom)
    cr.stroke()
    cr.set_font_size(11)

    y_title = f"{self.title} ({self.unit})"
    cr.save()
    cr.translate(16, (top + bottom) / 2)
    cr.rotate(-math.pi / 2)
    cr.move_to(-cr.text_extents(y_title).width / 2, 0)
    cr.show_text(y_title)
    cr.restore()

    x_title = "Atomic number"
    cr.move_to((left + right - cr.text_extents(x_title).width) / 2, height - 8)
    cr.show_text(x_title)

    # Smooth Material/Adwaita Accent Trend Line
    cr.set_source_rgba(0.25, 0.65, 0.95, 0.9)
    cr.set_line_width(2.5)
    for i, (number, value, _name) in enumerate(self.points):
      x, y = point(number, value)
      if i == 0:
        cr.move_to(x, y)
      else:
        cr.line_to(x, y)
    cr.stroke()

    # Data points
    cr.set_source_rgba(0.40, 0.78, 1.0, 1.0)
    for number, value, _name in self.points:
      x, y = point(number, value)
      cr.arc(x, y, 3.5, 0, math.tau)
      cr.fill()

  def on_chart_motion(self, _controller, x, y):
    width, height = self.chart.get_width(), self.chart.get_height()
    if width <= 0 or height <= 0 or not self.points:
      return
    _lower, _upper, point = self.chart_scale(width, height)
    number, value, name = min(self.points,
                              key=lambda item:
                              (point(item[0], item[1])[0] - x)**2 +
                              (point(item[0], item[1])[1] - y)**2)
    px, py = point(number, value)
    if (px - x)**2 + (py - y)**2 <= 20**2:
      self.hover_badge.set_label(
          f"● {name} ({int(number)})  —  {self.title}: {value:g} {self.unit}")
      self.hover_badge.remove_css_class("dim-label")
    else:
      self.hover_badge.set_label("Hover or move over data points to inspect elements")
      self.hover_badge.add_css_class("dim-label")

  def on_chart_leave(self, _controller):
    self.hover_badge.set_label("Hover or move over data points to inspect elements")
    self.hover_badge.add_css_class("dim-label")


def main():
  return PeriodicTable().run(sys.argv)


if __name__ == "__main__":
  raise SystemExit(main())
