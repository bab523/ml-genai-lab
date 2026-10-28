import sqlite3, os, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---- SQLite database ----
if os.path.exists("data/clients.db"):
    os.remove("data/clients.db")
con = sqlite3.connect("data/clients.db")
con.executescript("""
CREATE TABLE clients(client_id INTEGER PRIMARY KEY, name TEXT, risk_profile TEXT, tax_bracket REAL);
CREATE TABLE holdings(client_id INTEGER, asset_class TEXT, sector TEXT, balance REAL);
""")
con.executemany("INSERT INTO clients VALUES(?,?,?,?)", [
    (1, "Customer X", "aggressive", 0.32),
    (2, "Customer Y", "conservative", 0.24),
    (3, "Customer Z", "moderate", 0.35),
])
con.executemany("INSERT INTO holdings VALUES(?,?,?,?)", [
    (1, "equities", "technology", 420000), (1, "equities", "energy", 150000),
    (1, "bonds", "government", 80000), (1, "cash", "cash", 50000),
    (2, "bonds", "government", 300000), (2, "equities", "healthcare", 90000), (2, "cash", "cash", 60000),
    (3, "equities", "financials", 200000), (3, "real_estate", "reits", 120000), (3, "bonds", "corporate", 100000),
])
con.commit(); con.close()
print("created data/clients.db")

# ---- Market outlook PDFs (fictional) ----
REPORTS = {
 "q3_market_outlook.pdf": """Q3 Market Outlook (fictional lab document)
Technology: We are cautious on technology equities. Valuations are stretched and we expect a 12 percent correction in the sector over the quarter.
Energy: Energy equities are expected to gain 8 percent as supply stays tight.
Government bonds: Yields are expected to fall, so government bonds should return about 3 percent.
Corporate bonds: Credit spreads may widen, and we expect a flat return of 0 percent.
Healthcare: Healthcare is defensive and we forecast a 5 percent gain.
Financials: Banks face margin pressure and we forecast a 2 percent decline.
Real estate: REITs should return 4 percent as rate-cut hopes build.
Cash: Cash yields 4 percent annualised, about 1 percent for the quarter.""",
 "tax_notes.pdf": """Tax Notes (fictional lab document)
Capital gains realised on equities are taxed at the client's marginal tax bracket in this model.
Interest on bonds and cash is taxed at the client's marginal tax bracket.
Losses can be harvested and offset against gains, so projected tax risk is calculated on projected gains only.""",
}
for name, text in REPORTS.items():
    c = canvas.Canvas(f"data/reports/{name}", pagesize=A4); c.setFont("Helvetica", 11); y = 800
    for line in text.split("\n"):
        for piece in (textwrap.wrap(line, 95) or [""]):
            c.drawString(50, y, piece); y -= 16
    c.save()
    print("created data/reports/" + name)
