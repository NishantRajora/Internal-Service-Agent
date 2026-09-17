# retriever.py

import json
import os
import re


# ============================================================
# CONFIGURATION
# ============================================================

POLICY_FILE = "policies.json"


# ============================================================
# LOAD POLICIES
# ============================================================

def load_policies():
    """
    Load Veridian Corp policies from policies.json.
    """

    if not os.path.exists(POLICY_FILE):
        raise FileNotFoundError(
            f"{POLICY_FILE} was not found."
        )

    with open(
        POLICY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        policies = json.load(file)

    return policies


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Convert text to lowercase and remove unnecessary
    punctuation.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# KEYWORD MAP
# ============================================================

POLICY_KEYWORDS = {

    "KB-01": [
        "password",
        "forgot password",
        "reset password",
        "locked out",
        "account locked",
        "failed password",
        "login",
        "log in"
    ],

    "KB-02": [
        "vpn",
        "vpn access",
        "vpn credentials",
        "credentials expired",
        "remote access",
        "contractor vpn"
    ],

    "KB-03": [
        "laptop replacement",
        "replace laptop",
        "new laptop",
        "laptop replacement request",
        "replacement"
    ],

    "KB-04": [
        "software",
        "install software",
        "software installation",
        "application",
        "app installation",
        "browser extension",
        "extension",
        "non catalog",
        "not in catalog"
    ],

    "KB-05": [
        "printer",
        "printing",
        "paper jam",
        "print queue",
        "spooler"
    ],

    "KB-06": [
        "mailbox",
        "mailbox full",
        "email quota",
        "mailbox quota",
        "storage",
        "cannot send email",
        "cant send email",
        "can't send email"
    ],

    "KB-07": [
        "guest wifi",
        "guest wi fi",
        "guest wi-fi",
        "visitor wifi",
        "visitor wi-fi",
        "guest internet"
    ],

    "KB-08": [
        "expense",
        "expense software",
        "expense tool",
        "expense management",
        "expense login",
        "expense account"
    ],

    "KB-09": [
        "phishing",
        "phishing email",
        "malware",
        "unauthorized access",
        "suspicious email",
        "security incident",
        "security issue"
    ],

    "KB-10": [
        "work from home",
        "working from home",
        "home office",
        "home equipment",
        "office equipment",
        "monitor",
        "chair"
    ],

    "ASSET-POLICY": [
        "4 year",
        "four year",
        "refresh cycle",
        "hardware refresh",
        "early replacement",
        "finance sign off",
        "finance approval"
    ]
}


# ============================================================
# CATEGORY → POLICY MAP
# ============================================================

CATEGORY_POLICY_MAP = {

    "Security Incident": "KB-09",

    "Account Access": "KB-01",

    "VPN Access": "KB-02",

    "Contractor VPN": "KB-02",

    "Laptop / Hardware": "KB-03",

    "Software Installation": "KB-04",

    "Printer": "KB-05",

    "Email / Mailbox": "KB-06",

    "Guest Wi-Fi": "KB-07",

    "Expense Software": "KB-08",

    "Home Office Equipment": "KB-10",

    "Admin / Server Access": None,

    "Unknown": None
}


# ============================================================
# KEYWORD SCORING
# ============================================================

def calculate_keyword_score(
    request,
    policy_id,
    policy
):
    """
    Calculate how strongly the request matches a policy.

    A simple keyword scoring approach is sufficient for the
    small supplied Veridian knowledge base.
    """

    text = normalize_text(request)

    keywords = POLICY_KEYWORDS.get(
        policy_id,
        []
    )

    score = 0

    matched_keywords = []

    for keyword in keywords:

        normalized_keyword = normalize_text(
            keyword
        )

        # Exact phrase match
        if normalized_keyword in text:

            # Longer phrases get more weight
            words = normalized_keyword.split()

            weight = len(words) * 2

            score += weight

            matched_keywords.append(
                keyword
            )

    # --------------------------------------------------------
    # Also check policy title and description
    # --------------------------------------------------------

    policy_text = normalize_text(
        f"""
        {policy.get('title', '')}
        {policy.get('description', '')}
        """
    )

    request_words = set(
        text.split()
    )

    policy_words = set(
        policy_text.split()
    )

    common_words = request_words.intersection(
        policy_words
    )

    # Small additional score for overlapping words
    score += min(
        len(common_words),
        5
    )

    return score, matched_keywords


# ============================================================
# FIND POLICY BY ID
# ============================================================

def get_policy_by_id(policy_id):
    """
    Retrieve a specific policy using its ID.
    """

    policies = load_policies()

    for policy in policies:

        if policy.get("id") == policy_id:

            return policy

    return None


# ============================================================
# MAIN RETRIEVER
# ============================================================

def find_relevant_policy(
    category=None,
    request=""
):
    """
    Find the most relevant policy.

    Retrieval strategy:

    1. Use category mapping when available.
    2. Otherwise use keyword matching.
    3. Return None when confidence is too low.

    This prevents the system from inventing a policy.
    """

    policies = load_policies()

    # --------------------------------------------------------
    # STEP 1 — Category-based retrieval
    # --------------------------------------------------------

    if category:

        mapped_policy_id = CATEGORY_POLICY_MAP.get(
            category
        )

        if mapped_policy_id:

            policy = get_policy_by_id(
                mapped_policy_id
            )

            if policy:

                return policy

    # --------------------------------------------------------
    # STEP 2 — Keyword-based retrieval
    # --------------------------------------------------------

    best_policy = None
    best_score = 0
    best_matches = []

    for policy in policies:

        policy_id = policy.get(
            "id"
        )

        score, matches = calculate_keyword_score(
            request,
            policy_id,
            policy
        )

        if score > best_score:

            best_score = score
            best_policy = policy
            best_matches = matches

    # --------------------------------------------------------
    # STEP 3 — Confidence threshold
    # --------------------------------------------------------

    if best_score < 2:

        return None

    # Attach retrieval metadata
    best_policy = best_policy.copy()

    best_policy["_retrieval_score"] = best_score

    best_policy["_matched_keywords"] = best_matches

    return best_policy


# ============================================================
# SEARCH ALL POLICIES
# ============================================================

def search_policies(query, top_k=5):
    """
    Return the top matching policies.

    Useful for debugging or displaying retrieval results.
    """

    policies = load_policies()

    scored_policies = []

    for policy in policies:

        score, matches = calculate_keyword_score(
            query,
            policy.get("id"),
            policy
        )

        scored_policies.append(
            {
                "policy": policy,
                "score": score,
                "matches": matches
            }
        )

    # Sort highest score first
    scored_policies.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return scored_policies[:top_k]


# ============================================================
# DEBUG FUNCTION
# ============================================================

def debug_retrieval(query, category=None):
    """
    Print retrieval results for testing.
    """

    print("\n================================")
    print("VERIDIAN POLICY RETRIEVAL")
    print("================================")

    print(
        f"\nQuery: {query}"
    )

    print(
        f"Category: {category}"
    )

    policy = find_relevant_policy(
        category=category,
        request=query
    )

    if policy:

        print(
            f"\nBest Policy:"
        )

        print(
            f"ID: {policy.get('id')}"
        )

        print(
            f"Title: {policy.get('title')}"
        )

        print(
            f"Score: "
            f"{policy.get('_retrieval_score', 'N/A')}"
        )

        print(
            f"Matched Keywords: "
            f"{policy.get('_matched_keywords', [])}"
        )

        print(
            f"\nDescription:"
        )

        print(
            policy.get(
                "description",
                ""
            )
        )

    else:

        print(
            "\nNo sufficiently relevant policy found."
        )


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    test_cases = [

        (
            "My password is not working and "
            "I am locked out of my account.",
            "Account Access"
        ),

        (
            "My VPN credentials have expired.",
            "VPN Access"
        ),

        (
            "Can my guest get Wi-Fi tomorrow?",
            "Guest Wi-Fi"
        ),

        (
            "I received a phishing email.",
            "Security Incident"
        ),

        (
            "My printer has a paper jam.",
            "Printer"
        ),

        (
            "My mailbox is full.",
            "Email / Mailbox"
        ),

        (
            "I need a monitor for working from home.",
            "Home Office Equipment"
        )
    ]

    for query, category in test_cases:

        debug_retrieval(
            query=query,
            category=category
        )