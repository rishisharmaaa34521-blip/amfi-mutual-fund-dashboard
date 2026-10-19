"""Fetch and parse AMFI monthly Excel reports; fail closed on changed layouts."""
from __future__ import annotations
import re
from pathlib import Path
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "https://www.amfiindia.com/research-information/amfi-monthly"
RAW = ROOT / "data" / "raw"

def report_links(session: requests.Session) -> list[tuple[str, str]]:
    response = session.get(ARCHIVE, timeout=45)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    found = {}
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if "excel" not in label:
            continue
        url = urljoin(ARCHIVE, a["href"])
        # AMFI archive groups reports by fiscal year; report filename convention contains month/year.
        context = ""
        node = a
        for _ in range(5):
            if node.parent is None: break
            node = node.parent
            context = " ".join(node.stripped_strings)
            if re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b", context, re.I): break
        m = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b", context, re.I)
        if not m:
            # Most AMFI file names are am<month><year>repo with the month spelled out in title.
            m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})", a.get("title", ""), re.I)
        if m:
            date = pd.Timestamp(f"{m.group(2)}-{m.group(1)}-01")
            found[date.strftime("%Y-%m")] = url
    return sorted(found.items())

def _number(value):
    if pd.isna(value): return None
    s = str(value).replace(",", "").replace("₹", "").strip()
    if s in {"", "-", "—", "nan", "None"}: return None
    s = re.sub(r"[^0-9.()\-]", "", s)
    if s.startswith("(") and s.endswith(")"): s = "-" + s[1:-1]
    try: return float(s)
    except ValueError: return None

def parse_workbook(path: Path, month: str) -> dict:
    book = pd.ExcelFile(path)
    frame = None
    for sheet in book.sheet_names:
        candidate = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
        if candidate.astype(str).apply(lambda c: c.str.contains("mobiliz|mobilis", case=False, regex=True)).any().any():
            frame = candidate; break
    if frame is None: raise ValueError(f"No funds-mobilized header found in {path.name}")
    header_row = None; cols = {}
    for i in range(min(30, len(frame))):
        texts = [str(x).lower().replace("\n", " ") for x in frame.iloc[i].tolist()]
        joined = " | ".join(texts)
        if ("mobiliz" in joined or "mobilis" in joined) and ("repurchase" in joined or "redemption" in joined):
            header_row = i
            for j, text in enumerate(texts):
                if "mobiliz" in text or "mobilis" in text: cols["inflow"] = j
                if "repurchase" in text or "redemption" in text: cols["outflow"] = j
                if "net inflow" in text or "net flow" in text: cols["net_flow"] = j
                if ("net assets under management as on" in text or re.search(r"\baum as on\b", text)) and "segregated" not in text:
                    cols["aum"] = j
            break
    if header_row is None or not {"inflow", "outflow", "aum"}.issubset(cols):
        raise ValueError(f"Expected AMFI report columns not recognized in {path.name}")
    subtotal = None
    for _, row in frame.iterrows():
        labels = [re.sub(r"\s+", " ", str(x)).strip().lower() for x in row.tolist() if not pd.isna(x)]
        if any(re.search(r"sub\s*total\s*[-–]?\s*ii\b", x) for x in labels):
            subtotal = row
            break
    if subtotal is None: raise ValueError(f"Open-ended equity subtotal (II) not found in {path.name}")
    total = {k: _number(subtotal.iloc[j]) for k, j in cols.items()}
    if any(total.get(k) is None for k in ("inflow", "outflow", "aum")):
        raise ValueError(f"Equity subtotal has missing target/AUM values in {path.name}")
    net = total.get("net_flow")
    if net is not None and abs(net - (total["inflow"] - total["outflow"])) > 1.0:
        raise ValueError(f"Published equity subtotal net flow does not reconcile for {month}")
    return {"month": month, "equity_inflow": total["inflow"], "equity_outflow": total["outflow"],
            "net_flow": total["inflow"] - total["outflow"], "equity_aum": total["aum"], "source_file": path.name}

def collect(start="2019-04", end=None):
    RAW.mkdir(parents=True, exist_ok=True)
    session = requests.Session(); session.headers["User-Agent"] = "AcademicResearch/1.0 (AMFI monthly public reports)"
    links = report_links(session)
    if end is None: end = pd.Timestamp.today().strftime("%Y-%m")
    selected = [(m, u) for m, u in links if start <= m <= end]
    if not selected: raise RuntimeError("No AMFI Excel reports found in requested range; inspect the official archive or update parser.")
    output=[]; errors=[]
    for month, url in selected:
        suffix = ".xls" if url.lower().split("?",1)[0].endswith(".xls") else ".xlsx"
        path = RAW / f"amfi_{month}{suffix}"
        try:
            if not path.exists():
                r=session.get(url, timeout=60); r.raise_for_status()
                if not r.content[:2] or len(r.content) < 1000: raise ValueError("Download is empty or not a workbook")
                path.write_bytes(r.content)
            output.append(parse_workbook(path, month))
        except Exception as exc:
            errors.append(f"{month}: {exc}")
    if errors: (ROOT / "outputs" / "tables").mkdir(parents=True, exist_ok=True); (ROOT / "outputs" / "tables" / "collection_errors.txt").write_text("\n".join(errors), encoding="utf-8")
    if len(output) < 60: raise RuntimeError(f"Only {len(output)} valid monthly reports; at least 60 required. See outputs/tables/collection_errors.txt")
    df=pd.DataFrame(output).sort_values("month").drop_duplicates("month", keep="last")
    df.to_csv(ROOT / "data" / "processed" / "monthly_flows.csv", index=False)
    return df
