"""Fill lines to have equal number of delimited fields."""


def fill_lines(
    lines: list[str],
    sep: str = "\t",
    fill: str = "NA",
) -> list[str]:
    """Pad delimited lines so all have equal field count.

    Parameters
    ----------
    lines : list of str
        Input lines.
    sep : str
        Field separator.
    fill : str
        Value to use for padding.

    Returns
    -------
    list of str
        Lines with equal number of fields.
    """
    if not lines:
        return []
    split = [line.split(sep) for line in lines]
    max_fields = max(len(fields) for fields in split)
    result = []
    for fields in split:
        while len(fields) < max_fields:
            fields.append(fill)
        result.append(sep.join(fields))
    return result
