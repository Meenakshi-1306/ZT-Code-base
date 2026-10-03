import re


# ---------------------------------------------------------
# Risk levels
# ---------------------------------------------------------

def get_risk_level(score: int) -> str:

    if score >= 80:
        return "Critical"

    elif score >= 60:
        return "High"

    elif score >= 30:
        return "Medium"

    else:
        return "Low"


# ---------------------------------------------------------
# Detect scenario
# ---------------------------------------------------------

def detect_scenario(question: str):

    q = question.lower()

    access_keywords = [
        "access",
        "admin",
        "database",
        "db",
        "permission",
        "privilege",
        "login",
    ]

    if any(word in q for word in access_keywords):
        return "access_control"

    return "general"


# ---------------------------------------------------------
# Detect sensitive resources
# ---------------------------------------------------------

def detect_resource_sensitivity(question: str):

    q = question.lower()

    if any(
        word in q
        for word in [
            "admin db",
            "admin database",
            "production database",
            "production db",
            "root",
            "administrator",
            "privileged",
        ]
    ):
        return 10

    if any(
        word in q
        for word in [
            "database",
            "db",
            "server",
        ]
    ):
        return 8

    return 5


# ---------------------------------------------------------
# Detect privilege level
# ---------------------------------------------------------

def detect_privilege(question: str):

    q = question.lower()

    if any(
        word in q
        for word in [
            "admin",
            "administrator",
            "root",
            "privileged",
        ]
    ):
        return 10

    if any(
        word in q
        for word in [
            "manager",
            "operator",
        ]
    ):
        return 7

    return 5


# ---------------------------------------------------------
# Detect compliance sensitivity
# ---------------------------------------------------------

def detect_compliance_sensitivity(
    retrieved_documents,
):

    if not retrieved_documents:
        return 5

    standards = set()

    for document in retrieved_documents:

        metadata = document.get(
            "metadata",
            {},
        )

        standard = metadata.get(
            "standard",
            "",
        )

        if standard:
            standards.add(
                standard.lower()
            )

    # More compliance frameworks
    # involved = higher compliance sensitivity

    if len(standards) >= 4:
        return 10

    elif len(standards) >= 2:
        return 8

    elif len(standards) == 1:
        return 6

    return 5


# ---------------------------------------------------------
# Detect likelihood of misuse
# ---------------------------------------------------------

def detect_likelihood(question: str):

    q = question.lower()

    high_risk_words = [
        "unauthorized",
        "bypass",
        "hack",
        "exploit",
        "without permission",
        "bypass security",
    ]

    if any(
        word in q
        for word in high_risk_words
    ):
        return 10

    if any(
        word in q
        for word in [
            "admin",
            "root",
            "privileged",
        ]
    ):
        return 8

    return 5


# ---------------------------------------------------------
# Calculate score
# ---------------------------------------------------------

def calculate_risk_score(
    impact,
    likelihood,
    exposure,
    privilege,
    compliance,
):

    score = (

        0.30 * impact
        + 0.25 * likelihood
        + 0.20 * exposure
        + 0.15 * privilege
        + 0.10 * compliance

    )

    # Convert 1-10 to 0-100

    score = round(
        score * 10
    )

    return min(
        max(score, 0),
        100,
    )


# ---------------------------------------------------------
# Generate factors
# ---------------------------------------------------------

def generate_granted_factors(
    privilege,
    exposure,
    compliance,
):

    factors = []

    if privilege >= 8:
        factors.append(
            "High privilege level"
        )

    if exposure >= 8:
        factors.append(
            "Sensitive database or system"
        )

    factors.append(
        "Potential unauthorized access"
    )

    if compliance >= 8:
        factors.append(
            "High compliance exposure"
        )

    return factors


def generate_denied_factors():

    return [
        "Administrative task may be delayed",
        "Potential operational impact",
    ]


# ---------------------------------------------------------
# Compliance mapping
# ---------------------------------------------------------

def generate_compliance_mapping(
    retrieved_documents,
):

    compliance = []

    found = set()

    for document in retrieved_documents:

        metadata = document.get(
            "metadata",
            {},
        )

        standard = metadata.get(
            "standard",
            "",
        )

        if not standard:
            continue

        standard_lower = (
            standard.lower()
        )

        if standard_lower in found:
            continue

        found.add(
            standard_lower
        )

        if "iso" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "ISO/IEC 27001",

                    "area":
                        "Access Control",
                }
            )

        elif "nist" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "NIST",

                    "area":
                        "Identity and Access Management",
                }
            )

        elif "cis" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "CIS Controls",

                    "area":
                        "Account and Access Management",
                }
            )

        elif "pci" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "PCI DSS",

                    "area":
                        "Access Control",
                }
            )

        elif "gdpr" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "GDPR",

                    "area":
                        "Protection of Personal Data",
                }
            )

        elif "hipaa" in standard_lower:

            compliance.append(
                {
                    "standard":
                        "HIPAA",

                    "area":
                        "Privacy and Security Rule",
                }
            )

    return compliance


# ---------------------------------------------------------
# Generate answer
# ---------------------------------------------------------

def generate_answer(
    question,
    compliance,
    retrieved_documents=None,
):

    if retrieved_documents:

        evidence_lines = []

        for document in retrieved_documents[:2]:

            metadata = document.get(
                "metadata",
                {},
            )

            source = metadata.get(
                "source",
                "uploaded compliance document",
            )

            page = metadata.get(
                "page",
                "unknown",
            )

            text = " ".join(
                document.get(
                    "text",
                    "",
                ).split()
            )

            if text:

                evidence_lines.append(
                    f"{source}, page {page}: {text}"
                )

        if evidence_lines:

            frameworks = ", ".join(
                item["standard"]
                for item in compliance
                if item.get("standard")
            )

            framework_note = (
                f" The retrieved evidence maps to {frameworks}."
                if frameworks
                else ""
            )

            return (
                f"For the question '{question}', "
                "the indexed compliance evidence says: "
                + " ".join(evidence_lines)
                + framework_note
            )

    q = question.lower()

    if (
        "admin" in q
        and
        ("db" in q or "database" in q)
    ):

        return (
            "Access to the admin database may be restricted "
            "because administrative privileges should be "
            "limited to authorized users and granted according "
            "to least-privilege and access-control requirements."
        )

    if "access" in q:

        return (
            "Access may be restricted because the requested "
            "resource may require authorization, appropriate "
            "privileges, and compliance with access-control "
            "requirements."
        )

    return (
        "The requested action should be evaluated against "
        "the applicable security controls and authorization "
        "requirements."
    )


# ---------------------------------------------------------
# Generate recommendation
# ---------------------------------------------------------

def generate_recommendation(
    granted_score,
    denied_score,
):

    if granted_score > denied_score:

        return (
            "Keep access restricted unless the user has an "
            "approved administrative role. If access is "
            "required, use approved temporary privileged "
            "access with authorization and logging."
        )

    else:

        return (
            "Access may be provided if the request is "
            "authorized and appropriate controls are in place. "
            "Monitor and log the activity."
        )


# ---------------------------------------------------------
# Generate risk explanation
# ---------------------------------------------------------

def generate_risk_explanation(
    score,
    level,
    factors,
    evidence_count,
):

    """Explain the risk classification in analyst-readable language."""

    threshold = {
        "Critical": "80 or above",
        "High": "60 to 79",
        "Medium": "30 to 59",
        "Low": "below 30",
    }[level]

    factor_text = ", ".join(
        factors
    ).lower()

    evidence_text = (
        f" {evidence_count} retrieved compliance source(s) "
        "also informed the assessment."
        if evidence_count
        else
        " No compliance source was retrieved, "
        "so this is a signal-only assessment."
    )

    return (
        f"This request is classified as {level} risk "
        f"with a score of {score}/100 "
        f"because the configured {level.lower()} band "
        f"is {threshold}. "
        f"The main contributing signals are "
        f"{factor_text}."
        f"{evidence_text}"
    )


# ---------------------------------------------------------
# Main risk assessment function
# ---------------------------------------------------------

def assess_risk(
    question,
    retrieved_documents,
):

    scenario = detect_scenario(
        question
    )

    # -----------------------------
    # Determine risk factors
    # -----------------------------

    sensitivity = (
        detect_resource_sensitivity(
            question
        )
    )

    privilege = (
        detect_privilege(
            question
        )
    )

    likelihood = (
        detect_likelihood(
            question
        )
    )

    compliance = (
        detect_compliance_sensitivity(
            retrieved_documents
        )
    )

    # -----------------------------
    # Access granted
    #
    # Sensitive resource → high impact
    # Admin privilege → high privilege
    # Compliance controls → high compliance risk
    # -----------------------------

    impact_granted = sensitivity

    exposure_granted = sensitivity

    granted_score = (
        calculate_risk_score(
            impact=impact_granted,
            likelihood=likelihood,
            exposure=exposure_granted,
            privilege=privilege,
            compliance=compliance,
        )
    )

    # -----------------------------
    # Access denied
    # -----------------------------

    # Denying access normally reduces
    # security risk but can create
    # operational impact.

    impact_denied = 4

    likelihood_denied = 2

    exposure_denied = 2

    privilege_denied = 2

    compliance_denied = 2

    denied_score = (
        calculate_risk_score(
            impact=impact_denied,
            likelihood=likelihood_denied,
            exposure=exposure_denied,
            privilege=privilege_denied,
            compliance=compliance_denied,
        )
    )

    # -----------------------------
    # Compliance
    # -----------------------------

    compliance_mapping = (
        generate_compliance_mapping(
            retrieved_documents
        )
    )

    # -----------------------------
    # Answer
    # -----------------------------

    answer = generate_answer(
        question,
        compliance_mapping,
        retrieved_documents,
    )

    # -----------------------------
    # Factors
    # -----------------------------

    granted_factors = (
        generate_granted_factors(
            privilege,
            sensitivity,
            compliance,
        )
    )

    denied_factors = (
        generate_denied_factors()
    )

    # -----------------------------
    # Recommendation
    # -----------------------------

    recommendation = (
        generate_recommendation(
            granted_score,
            denied_score,
        )
    )

    granted_level = (
        get_risk_level(
            granted_score
        )
    )

    denied_level = (
        get_risk_level(
            denied_score
        )
    )

    # -----------------------------
    # Final response
    # -----------------------------

    return {

        "question":
            question,

        "answer":
            answer,

        "compliance":
            compliance_mapping,

        "risk_assessment": {

            "access_granted": {

                "score":
                    granted_score,

                "level":
                    granted_level,

                "factors":
                    granted_factors,
            },

            "access_denied": {

                "score":
                    denied_score,

                "level":
                    denied_level,

                "factors":
                    denied_factors,
            },
        },

        "recommendation":
            recommendation,

        "risk_explanation": {

            "access_granted":
                generate_risk_explanation(
                    granted_score,
                    granted_level,
                    granted_factors,
                    len(
                        retrieved_documents
                    ),
                ),

            "access_denied":
                generate_risk_explanation(
                    denied_score,
                    denied_level,
                    denied_factors,
                    len(
                        retrieved_documents
                    ),
                ),
        },
    }