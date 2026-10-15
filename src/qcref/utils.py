import numbers
from dataclasses import fields, is_dataclass
from typing import Optional


def to_table(objects, headers: Optional[list[str]] = None):
    """Convert a list of dataclass objects into a nicely formatted table."""
    if not objects:
        print("No data to display.")
        return
    first = objects[0]
    if isinstance(first, dict):
        headers = headers or list(first.keys())
        rows = [[obj.get(h, "") for h in headers] for obj in objects]
    elif is_dataclass(first):
        headers = headers or [f.name for f in fields(first)]
        rows = [[getattr(obj, h) for h in headers] for obj in objects]
    else:
        headers = headers or list(vars(first).keys())
        rows = [[getattr(obj, h) for h in headers] for obj in objects]
    print(_tabulate(rows, headers=headers))


def _tabulate(
    rows: list[list[str]], headers: Optional[list[str]] = None, num_format: str = ".5g"
) -> str:
    """Format a list of rows into a table. Replacement for tabulate package."""
    table = []
    if headers is None:
        headers = [f"Column {i + 1}" for i in range(len(rows[0]))]

    # 1) Build a parallel matrix of *display* strings, forcing any Value to plain float
    text_rows = []
    for row in rows:
        txt_row = []
        for cell in row:
            if cell is None:
                txt = ""
            elif isinstance(cell, numbers.Real):
                txt = format(float(cell), num_format)
            else:
                txt = str(cell)
            txt_row.append(txt)
        text_rows.append(txt_row)

    # 2) Compute column widths from headers + text_rows
    cols = list(zip([str(h) for h in headers], *text_rows))
    widths = [max(len(item) for item in col) for col in cols]
    sep = "  "  # two spaces between columns

    # 4) Print header and separator
    header_line = sep.join(h.ljust(w) for h, w in zip(headers, widths))
    table.append(header_line)
    table.append(sep.join("-" * w for w in widths))

    # 5) Create each data row, right-aligning numbers, left-aligning text
    for raw_row, txt_row in zip(rows, text_rows):
        line = sep.join(
            txt.rjust(widths[i])
            if isinstance(raw_row[i], numbers.Real)
            else txt.ljust(widths[i])
            for i, txt in enumerate(txt_row)
        )
        table.append(line)
    return "\n".join(table)
