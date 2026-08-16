import os
import importlib.util


# =================================
# AKHIM AI WEB SEARCH TEST
# =================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

WEB_SEARCH_FILE = os.path.join(
    BASE_DIR,
    "web_search.py"
)


print("================================")
print("       AKHIM AI WEB TEST")
print("================================")
print()


# =================================
# CHECK FILE
# =================================

print(
    "Checking:",
    WEB_SEARCH_FILE
)


if not os.path.isfile(
    WEB_SEARCH_FILE
):

    print()
    print(
        "ERROR: web_search.py not found!"
    )

    raise SystemExit


# =================================
# LOAD web_search.py
# =================================

try:

    spec = importlib.util.spec_from_file_location(
        "web_search",
        WEB_SEARCH_FILE
    )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    WebSearch = module.WebSearch


except Exception as e:

    print()
    print(
        "ERROR loading WebSearch:"
    )

    print(e)

    raise SystemExit


# =================================
# CREATE SEARCH ENGINE
# =================================

search_engine = WebSearch()


# =================================
# GET QUESTION
# =================================

print()

query = input(
    "Search: "
).strip()


if not query:

    print(
        "No search query."
    )

    raise SystemExit


print()
print(
    "Searching..."
)
print()


# =================================
# SEARCH
# =================================

try:

    results = search_engine.search(
        query,
        max_results=5
    )


except Exception as e:

    print()
    print(
        "Search failed:"
    )

    print(e)

    raise SystemExit


# =================================
# RESULTS
# =================================

if not results:

    print(
        "No results found."
    )

    raise SystemExit


print(
    "Found",
    len(results),
    "results."
)

print()


for i, result in enumerate(
    results,
    start=1
):

    print(
        f"[{i}]",
        result.get(
            "title",
            "No title"
        )
    )


    print(
        "URL:",
        result.get(
            "url",
            ""
        )
    )


    source = result.get(
        "source",
        ""
    )

    if source:

        print(
            "Source:",
            source
        )


    date = result.get(
        "date",
        ""
    )

    if date:

        print(
            "Date:",
            date
        )


    snippet = result.get(
        "snippet",
        ""
    )

    if snippet:

        print(
            "Snippet:",
            snippet
        )


    print(
        "-" * 50
    )


print()
print(
    "Search test finished."
)