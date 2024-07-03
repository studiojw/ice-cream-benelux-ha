"""String utilities for ice_cream_benelux."""


def snake_to_pascal_case(s):
    """Convert snake case to pascal case."""
    return s.replace("_", " ").title().replace(" ", "")
