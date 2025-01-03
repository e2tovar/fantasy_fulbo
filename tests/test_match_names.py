from services import fuzzy_match_names

def test_fuzzy_match_names():
    # Mock Excel names
    excel_names = ['Roman (goat)', 'Andres Freitas', 'Andrés Ruiz', 'Eddy']

    # Mock database mapping
    db_names = {
        "Román Díaz": 1,
        "Andrés Freitas": 5,
        "Andrés Ruiz": 7,
        "Eddy": 21
    }

    # Call the fuzzy matching function
    matched_names, unmatched_names = fuzzy_match_names(excel_names, db_names)

    # Assertions
    assert matched_names == {
        'Andres Freitas': 5,
        'Andrés Ruiz': 7,
        'Eddy': 21
    }, "Matched names are incorrect"

    assert unmatched_names == ['Roman (goat)'], "Unmatched names are incorrect"
