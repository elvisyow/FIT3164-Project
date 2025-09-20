from datetime import datetime
from typing import Optional

def parse_date(s: str) -> Optional[datetime]:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):  # your CSV uses 5/01/2004
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None
