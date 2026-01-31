# ==============================
# Stations & Lines
# ==============================
stations = [
    "Tanah Merah", "Expo", "Changi Airport", "Changi T5",
    "Sungei Bedok", "Tampines", "Bedok", "Kembangan",
    "Paya Lebar", "City Hall", "Orchard", "Bishan",
    "Bugis", "Gardens By The Bay", "HarbourFront",
    "Marina Bay", "Dhoby Ghaut", "Raffles Place"
]

lines = ["EWL_Airport", "TEL_Airport", "TEL_Extension", "CRL_T5"]

# =========================================
# Rule Explanations
# =========================================
RULE_EXPLANATIONS = {
    1: "Today Mode requires the EWL to operate the airport corridor.",
    2: "EWL cannot operate the airport corridor in Future Mode.",
    3: "TEL must operate the airport corridor in Future Mode.",
    4: "TEL Extension enables access to Changi Terminal 5.",
    5: "Using Changi Terminal 5 requires the TEL Extension to be active.",
    6: "Changi Terminal 5 cannot be used in Today Mode.",
    7: "A route cannot use the EWL airport corridor if it is unavailable.",
    8: "A route cannot use the TEL airport corridor if it is unavailable.",
    9: "TEL airport services are suspended during integration works.",
    10: "Closed Expo station cannot appear in a route.",
    11: "Closed Tanah Merah station cannot appear in a route.",
    12: "The airport corridor cannot be operated by both EWL and TEL.",
    13: "Routes passing through Expo must use the correct airport corridor for the mode.",
    14: "Routes passing through Changi Airport must use the TEL corridor in Future Mode.",
    15: "TEL airport operation during integration works is contradictory."
}

# =========================================
# Rule Checker
# =========================================
def check_rules(scenario):
    violated = []

    Today = scenario.get("Today", False)
    Future = scenario.get("Future", False)
    EWL_Airport = scenario.get("EWL_Airport", False)
    TEL_Airport = scenario.get("TEL_Airport", False)
    TEL_Extension = scenario.get("TEL_Extension", False)
    IntegrationWorks_AirportCorridor = scenario.get("IntegrationWorks_AirportCorridor", False)
    Closed_Expo = scenario.get("Closed_Expo", False)
    Closed_TanahMerah = scenario.get("Closed_TanahMerah", False)

    Uses_EWL_Airport = scenario.get("Uses_EWL_Airport", False)
    Uses_TEL_Airport = scenario.get("Uses_TEL_Airport", False)
    Uses_T5 = scenario.get("Uses_T5", False)
    Uses_Expo = scenario.get("Uses_Expo", False)
    Uses_TanahMerah = scenario.get("Uses_TanahMerah", False)
    Uses_ChangiAirport = scenario.get("Uses_ChangiAirport", False)

    rules = [
        (Today and not EWL_Airport, 1),
        (Future and EWL_Airport, 2),
        (Future and not TEL_Airport, 3),
        (TEL_Extension and not Uses_T5, 4),
        (Uses_T5 and not TEL_Extension, 5),
        (Uses_T5 and not Future, 6),
        (Uses_EWL_Airport and not EWL_Airport, 7),
        (Uses_TEL_Airport and not TEL_Airport, 8),
        (IntegrationWorks_AirportCorridor and TEL_Airport, 9),
        (Closed_Expo and Uses_Expo, 10),
        (Closed_TanahMerah and Uses_TanahMerah, 11),
        (TEL_Airport and EWL_Airport, 12),
        (Uses_Expo and not ((Today and Uses_EWL_Airport) or (Future and Uses_TEL_Airport)), 13),
        (Uses_ChangiAirport and Future and not Uses_TEL_Airport, 14),
        (TEL_Airport and IntegrationWorks_AirportCorridor, 15),
    ]

    for condition, rule in rules:
        if condition:
            violated.append(rule)

    # Scenario 6: If both Rule 9 and 15 violated → CONTRADICTORY
    if 9 in violated and 15 in violated:
        return "CONTRADICTORY", violated

    if not violated:
        return "VALID ROUTE", []
    else:
        return "INVALID ROUTE", violated

# =========================================
# Scenarios
# =========================================
scenarios = [
    {
        "title": "Scenario 1 – Valid Today Mode",
        "facts": {
            "Today": True,
            "EWL_Airport": True,
            "IntegrationWorks_AirportCorridor": False,
            "Uses_EWL_Airport": True,
            "Uses_Expo": True,
            "Uses_ChangiAirport": True
        }
    },
    {
        "title": "Scenario 2 – Invalid Today Mode using T5",
        "facts": {
            "Today": True,
            "Uses_T5": True,
            "TEL_Extension": False
        }
    },
    {
        "title": "Scenario 3 – Valid Future Mode (TEL + T5)",
        "facts": {
            "Future": True,
            "TEL_Airport": True,
            "TEL_Extension": True,
            "IntegrationWorks_AirportCorridor": False,
            "Uses_TEL_Airport": True,
            "Uses_T5": True,
            "Uses_ChangiAirport": True
        }
    },
    {
        "title": "Scenario 4 – Invalid Future Mode using EWL",
        "facts": {
            "Future": True,
            "EWL_Airport": False,
            "Uses_EWL_Airport": True,
            "Uses_ChangiAirport": True
        }
    },
    {
        "title": "Scenario 5 – Invalid due to Station Closure (Expo)",
        "facts": {
            "Future": True,
            "TEL_Airport": True,
            "Closed_Expo": True,
            "Uses_Expo": True,
            "Uses_TEL_Airport": True
        }
    },
    {
        "title": "Scenario 6 – Contradictory Advisory (Integration Works)",
        "facts": {
            "Future": True,
            "TEL_Airport": True,
            "IntegrationWorks_AirportCorridor": True
        }
    },
    {
        "title": "Scenario 7 – Invalid (TEL extension missing)",
        "facts": {
            "Future": True,
            "TEL_Airport": True,
            "TEL_Extension": False,
            "Uses_T5": True,
            "Uses_TEL_Airport": True
        }
    },
    {
        "title": "Scenario 8 – Invalid (Closed Tanah Merah)",
        "facts": {
            "Future": True,
            "TEL_Airport": True,
            "Closed_TanahMerah": True,
            "Uses_TanahMerah": True,
            "Uses_TEL_Airport": True
        }
    }
]

# =========================================
# Output
# =========================================
for s in scenarios:
    status, violations = check_rules(s["facts"])

    print("=" * 70)
    print(s["title"])
    print("-" * 70)
    print(f"Result: {status}")

    if violations:
        print("\nViolated Rules:")
        for r in violations:
            print(f"  • Rule {r}: {RULE_EXPLANATIONS[r]}")
    else:
        print("\nNo rules violated. Route is valid.")

    print()  # <-- blank line after each scenario

print("=" * 70)