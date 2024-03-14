import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "admin")
    user, db_name = "mvmr", "mvmr"
    encoding = "unicode"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}?client_encoding={encoding}"


def get_settings_for_random_generation():
    settings = {"max_difference": 10}
    return settings
