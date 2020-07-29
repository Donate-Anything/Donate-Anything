from typing import Dict, List, Tuple
from urllib import parse

from django import template


register = template.Library()


@register.filter
def paginate(val, num_pages) -> List[Tuple[str, int]]:
    """Takes all current queries and page number
    and paginates with the same query parameters
    besides page number.

    Similar to how Google does it: 5 left, 4 to
    the right.
    :arg val: current url
    :arg num_pages: number of pages
    :return list of url paths for next pagination list.
    """
    # First grab the query parameters
    query: Dict[str, List[str]] = parse.parse_qs(
        parse.urlsplit(val).query, keep_blank_values=False
    )
    other_queries: str = parse.urlencode({"q": query.get("q")}, True)
    try:
        page = int(query["page"][0])
    except (TypeError, ValueError, KeyError):
        # Assume page 1
        return [(f"?page={i}&{other_queries}", i) for i in range(1, num_pages + 1)]
    # Deciding which pages to show
    if page <= 5 or num_pages <= 10:
        # Show first 10 if first 5 (e.g. 1-5/10) or if there're only 10
        return [
            (f"?page={i + 1}&{other_queries}", i + 1)
            for i in range(10 if num_pages > 10 else num_pages)
        ]

    # Pages start on 1
    start = page - 5
    # potential_end = page + 4
    if page + 4 > num_pages:
        # Show last 10 if within the last 5
        return [
            (f"?page={i + 1}&{other_queries}", i + 1)
            for i in range(num_pages - 9, num_pages)
        ]
    # Show 10 since still in middle
    return [(f"?page={i + 1}&{other_queries}", i + 1) for i in range(start, start + 10)]


@register.filter
def get_all_but_page(val):
    """
    :param val: full url
    :return: string of query parameters without page
    """
    query = parse.parse_qs(parse.urlsplit(val).query, keep_blank_values=False)
    other_queries: str = parse.urlencode({"q": query["q"]}, True)
    return f"?{other_queries}"
