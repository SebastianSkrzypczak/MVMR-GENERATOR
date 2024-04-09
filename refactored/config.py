import os


def get_postgres_uri():

    return os.environ.get("DB_URL")


def get_settings_for_random_generation():
    settings = {"max_difference": 10}
    return settings
