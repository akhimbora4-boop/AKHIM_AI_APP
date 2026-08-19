import os
import sys
import time
import traceback
import argparse
import importlib.util
from urllib.parse import urlparse


# ============================================================
# AKHIM AI
# ADVANCED WEB SEARCH TESTER
# ============================================================

VERSION = "2.0"


# ============================================================
# COLORS
# ============================================================

class Colors:

    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


def color(text, colour):
    return f"{colour}{text}{Colors.RESET}"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

WEB_SEARCH_FILE = os.path.join(
    BASE_DIR,
    "web_search.py"
)


# ============================================================
# ARGUMENTS
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description="AKHIM AI WebSearch diagnostic tester"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=None,
        help="Search query"
    )

    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=5,
        help="Maximum number of results"
    )

    parser.add_argument(
        "--traceback",
        action="store_true",
        help="Show full traceback on errors"
    )

    return parser.parse_args()


# ============================================================
# HEADER
# ============================================================

def print_header():

    print()
    print("=" * 60)
    print(
        color(
            "              AKHIM AI WEB SEARCH TEST",
            Colors.CYAN + Colors.BOLD
        )
    )
    print(
        color(
            f"                    Version {VERSION}",
            Colors.WHITE
        )
    )
    print("=" * 60)
    print()


# ============================================================
# CHECK FILE
# ============================================================

def check_web_search_file():

    print(
        color(
            "[1] Checking web_search.py",
            Colors.BLUE
        )
    )

    print(
        "    Path:",
        WEB_SEARCH_FILE
    )

    if not os.path.isfile(
        WEB_SEARCH_FILE
    ):

        print(
            color(
                "    ERROR: web_search.py not found!",
                Colors.RED
            )
        )

        return False

    print(
        color(
            "    OK: web_search.py found.",
            Colors.GREEN
        )
    )

    return True


# ============================================================
# LOAD MODULE
# ============================================================

def load_web_search_module():

    print()

    print(
        color(
            "[2] Loading WebSearch module",
            Colors.BLUE
        )
    )

    try:

        spec = importlib.util.spec_from_file_location(
            "akhim_ai_web_search",
            WEB_SEARCH_FILE
        )

        if spec is None:

            raise ImportError(
                "Could not create module specification."
            )

        if spec.loader is None:

            raise ImportError(
                "Module loader is unavailable."
            )

        module = importlib.util.module_from_spec(
            spec
        )

        spec.loader.exec_module(
            module
        )

        print(
            color(
                "    OK: web_search.py loaded.",
                Colors.GREEN
            )
        )

        return module

    except Exception as error:

        print(
            color(
                "    ERROR: Failed to load web_search.py",
                Colors.RED
            )
        )

        print(
            "    Reason:",
            error
        )

        return None


# ============================================================
# VALIDATE CLASS
# ============================================================

def validate_web_search_class(module):

    print()

    print(
        color(
            "[3] Validating WebSearch class",
            Colors.BLUE
        )
    )

    if not hasattr(
        module,
        "WebSearch"
    ):

        print(
            color(
                "    ERROR: WebSearch class not found.",
                Colors.RED
            )
        )

        return None

    WebSearch = module.WebSearch

    if not callable(
        WebSearch
    ):

        print(
            color(
                "    ERROR: WebSearch is not callable.",
                Colors.RED
            )
        )

        return None

    print(
        color(
            "    OK: WebSearch class found.",
            Colors.GREEN
        )
    )

    return WebSearch


# ============================================================
# CREATE SEARCH ENGINE
# ============================================================

def create_search_engine(WebSearch):

    print()

    print(
        color(
            "[4] Creating search engine",
            Colors.BLUE
        )
    )

    try:

        search_engine = WebSearch()

        print(
            color(
                "    OK: WebSearch instance created.",
                Colors.GREEN
            )
        )

        return search_engine

    except Exception as error:

        print(
            color(
                "    ERROR: Could not create WebSearch.",
                Colors.RED
            )
        )

        print(
            "    Reason:",
            error
        )

        return None


# ============================================================
# VALIDATE SEARCH METHOD
# ============================================================

def validate_search_method(search_engine):

    print()

    print(
        color(
            "[5] Validating search() method",
            Colors.BLUE
        )
    )

    search_method = getattr(
        search_engine,
        "search",
        None
    )

    if not callable(
        search_method
    ):

        print(
            color(
                "    ERROR: search() method not found.",
                Colors.RED
            )
        )

        return False

    print(
        color(
            "    OK: search() method available.",
            Colors.GREEN
        )
    )

    return True


# ============================================================
# GET QUERY
# ============================================================

def get_query(args):

    print()

    if args.query is not None:

        query = args.query.strip()

    else:

        try:

            query = input(
                "Search: "
            ).strip()

        except KeyboardInterrupt:

            print()
            print(
                color(
                    "Search cancelled.",
                    Colors.YELLOW
                )
            )

            return None

    if not query:

        print(
            color(
                "ERROR: Empty search query.",
                Colors.RED
            )
        )

        return None

    return query


# ============================================================
# VALIDATE MAX RESULTS
# ============================================================

def validate_max_results(value):

    if value < 1:

        print(
            color(
                "ERROR: max-results must be >= 1.",
                Colors.RED
            )
        )

        return False

    if value > 100:

        print(
            color(
                "WARNING: max-results > 100.",
                Colors.YELLOW
            )
        )

    return True


# ============================================================
# URL VALIDATION
# ============================================================

def is_valid_url(url):

    if not isinstance(
        url,
        str
    ):

        return False

    url = url.strip()

    if not url:

        return False

    try:

        parsed = urlparse(
            url
        )

        return bool(
            parsed.scheme
            and parsed.netloc
        )

    except Exception:

        return False


# ============================================================
# NORMALIZE VALUE
# ============================================================

def safe_text(value):

    if value is None:

        return ""

    try:

        return str(value).strip()

    except Exception:

        return ""


# ============================================================
# VALIDATE RESULT
# ============================================================

def validate_result(result, index):

    problems = []

    if not isinstance(
        result,
        dict
    ):

        problems.append(
            "Result is not a dictionary."
        )

        return problems

    title = safe_text(
        result.get("title")
    )

    url = safe_text(
        result.get("url")
    )

    snippet = safe_text(
        result.get("snippet")
    )

    source = safe_text(
        result.get("source")
    )

    date = safe_text(
        result.get("date")
    )

    if not title:

        problems.append(
            "Missing title."
        )

    if not url:

        problems.append(
            "Missing URL."
        )

    elif not is_valid_url(url):

        problems.append(
            "Invalid URL."
        )

    if not snippet:

        problems.append(
            "Missing snippet."
        )

    if not source:

        problems.append(
            "Missing source."
        )

    # Date is optional.
    # We do not mark it as a hard failure.

    return problems


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def find_duplicates(results):

    seen = set()
    duplicates = []

    for index, result in enumerate(
        results,
        start=1
    ):

        if not isinstance(
            result,
            dict
        ):

            continue

        url = safe_text(
            result.get("url")
        )

        if not url:

            continue

        normalized = url.rstrip(
            "/"
        ).lower()

        if normalized in seen:

            duplicates.append(
                index
            )

        else:

            seen.add(
                normalized
            )

    return duplicates


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(index, result):

    print(
        color(
            f"[{index}]",
            Colors.CYAN + Colors.BOLD
        ),
        safe_text(
            result.get(
                "title",
                "No title"
            )
        )
    )

    print(
        "    URL:",
        safe_text(
            result.get("url")
        )
    )

    source = safe_text(
        result.get("source")
    )

    if source:

        print(
            "    Source:",
            source
        )

    date = safe_text(
        result.get("date")
    )

    if date:

        print(
            "    Date:",
            date
        )

    snippet = safe_text(
        result.get("snippet")
    )

    if snippet:

        print(
            "    Snippet:",
            snippet
        )

    print(
        "-" * 60
    )


# ============================================================
# RUN SEARCH
# ============================================================

def run_search(
    search_engine,
    query,
    max_results
):

    print()

    print(
        color(
            "[6] Running web search",
            Colors.BLUE
        )
    )

    print(
        "    Query:",
        query
    )

    print(
        "    Max results:",
        max_results
    )

    print()

    start_time = time.perf_counter()

    try:

        results = search_engine.search(
            query,
            max_results=max_results
        )

    except TypeError as error:

        print(
            color(
                "    ERROR: search() signature mismatch.",
                Colors.RED
            )
        )

        print(
            "    Reason:",
            error
        )

        print()
        print(
            "    Your WebSearch.search() may not support:"
        )

        print(
            "    max_results=..."
        )

        return None, None

    except Exception as error:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            color(
                "    SEARCH FAILED",
                Colors.RED
            )
        )

        print(
            "    Error:",
            error
        )

        print(
            "    Time:",
            f"{elapsed:.3f}s"
        )

        return None, elapsed

    elapsed = (
        time.perf_counter()
        - start_time
    )

    return results, elapsed


# ============================================================
# ANALYZE RESULTS
# ============================================================

def analyze_results(results):

    print()

    print(
        color(
            "[7] Analyzing results",
            Colors.BLUE
        )
    )

    if results is None:

        print(
            color(
                "    No result object returned.",
                Colors.RED
            )
        )

        return False

    if not isinstance(
        results,
        (list, tuple)
    ):

        print(
            color(
                "    ERROR: search() must return list/tuple.",
                Colors.RED
            )
        )

        print(
            "    Returned:",
            type(results).__name__
        )

        return False

    if not results:

        print(
            color(
                "    WARNING: No search results.",
                Colors.YELLOW
            )
        )

        return False

    print(
        color(
            f"    Found {len(results)} result(s).",
            Colors.GREEN
        )
    )

    problems_count = 0

    for index, result in enumerate(
        results,
        start=1
    ):

        problems = validate_result(
            result,
            index
        )

        if problems:

            problems_count += len(
                problems
            )

            print(
                color(
                    f"    Result {index}:",
                    Colors.YELLOW
                )
            )

            for problem in problems:

                print(
                    "      -",
                    problem
                )

    duplicates = find_duplicates(
        results
    )

    if duplicates:

        print(
            color(
                "    Duplicate URLs:",
                Colors.YELLOW
            ),
            duplicates
        )

    else:

        print(
            color(
                "    Duplicate URLs: none",
                Colors.GREEN
            )
        )

    if problems_count == 0:

        print(
            color(
                "    Result validation: PASSED",
                Colors.GREEN
            )
        )

    else:

        print(
            color(
                f"    Result validation: {problems_count} issue(s)",
                Colors.YELLOW
            )
        )

    return True


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    print()

    print(
        color(
            "[8] Search results",
            Colors.BLUE
        )
    )

    print()

    for index, result in enumerate(
        results,
        start=1
    ):

        if isinstance(
            result,
            dict
        ):

            print_result(
                index,
                result
            )

        else:

            print(
                color(
                    f"[{index}] Invalid result:",
                    Colors.RED
                ),
                repr(result)
            )

            print(
                "-" * 60
            )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    results,
    elapsed
):

    print()

    print("=" * 60)

    print(
        color(
            "                    TEST SUMMARY",
            Colors.CYAN + Colors.BOLD
        )
    )

    print("=" * 60)

    if results is None:

        print(
            "Status:",
            color(
                "FAILED",
                Colors.RED
            )
        )

        return False

    if not isinstance(
        results,
        (list, tuple)
    ):

        print(
            "Status:",
            color(
                "FAILED",
                Colors.RED
            )
        )

        return False

    if not results:

        print(
            "Status:",
            color(
                "NO RESULTS",
                Colors.YELLOW
            )
        )

        return False

    valid = 0
    invalid = 0

    for result in results:

        if not isinstance(
            result,
            dict
        ):

            invalid += 1
            continue

        problems = validate_result(
            result,
            0
        )

        if problems:

            invalid += 1

        else:

            valid += 1

    duplicates = find_duplicates(
        results
    )

    print(
        "Total results:",
        len(results)
    )

    print(
        "Valid results:",
        valid
    )

    print(
        "Invalid results:",
        invalid
    )

    print(
        "Duplicate URLs:",
        len(duplicates)
    )

    if elapsed is not None:

        print(
            "Search time:",
            f"{elapsed:.3f} seconds"
        )

    print()

    if valid > 0:

        print(
            "Status:",
            color(
                "SEARCH TEST PASSED",
                Colors.GREEN + Colors.BOLD
            )
        )

        return True

    print(
        "Status:",
        color(
            "SEARCH TEST FAILED",
            Colors.RED + Colors.BOLD
        )
    )

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_arguments()

    print_header()

    # --------------------------------------------------------
    # Validate max results
    # --------------------------------------------------------

    if not validate_max_results(
        args.max_results
    ):

        return 1

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not check_web_search_file():

        return 1

    # --------------------------------------------------------
    # Load module
    # --------------------------------------------------------

    module = load_web_search_module()

    if module is None:

        if args.traceback:

            traceback.print_exc()

        return 1

    # --------------------------------------------------------
    # Validate class
    # --------------------------------------------------------

    WebSearch = validate_web_search_class(
        module
    )

    if WebSearch is None:

        return 1

    # --------------------------------------------------------
    # Create search engine
    # --------------------------------------------------------

    search_engine = create_search_engine(
        WebSearch
    )

    if search_engine is None:

        return 1

    # ---------------