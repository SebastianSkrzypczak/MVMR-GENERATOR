import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "mvmr", "mvmr"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_settings_for_random_generation():
    settings = {"max_difference": 10}
    return settings
