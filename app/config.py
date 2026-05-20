import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_browser_sources(config: dict) -> list[dict]:
    return [s for s in config["sources"] if s["type"] == "browser"]


def get_api_sources(config: dict) -> list[dict]:
    return [s for s in config["sources"] if s["type"] == "api"]
