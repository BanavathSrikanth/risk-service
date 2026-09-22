from pathlib import Path
from typing import Any

import yaml


def load_rules(rules_path: str) -> dict[str, Any]:
    path = Path(rules_path)
    if not path.exists():
        service_rules = Path(__file__).parents[2] / "domain" / "rules" / "v1"
        path = service_rules / path.name
        if not path.exists() and path.suffix == ".yaml":
            path = path.with_suffix(".yaml.txt")
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
