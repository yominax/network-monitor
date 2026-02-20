"""
Gestion de la configuration des campagnes de tests réseau.

La configuration est décrite dans un fichier YAML, par exemple :

```yaml
interval_seconds: 5
targets:
  - name: gateway
    host: 192.168.0.1
    icmp: true
    tcp_ports: [22, 80]
    http_urls: ["http://192.168.0.1/"]
```
"""

from dataclasses import dataclass, field
from typing import List, Optional

import yaml


@dataclass
class Target:
    """Description d'une cible réseau à tester."""

    name: str
    host: str
    icmp: bool = True
    tcp_ports: List[int] = field(default_factory=list)
    http_urls: List[str] = field(default_factory=list)


@dataclass
class MonitorConfig:
    """Configuration globale d'une campagne de tests."""

    interval_seconds: int = 5
    targets: List[Target] = field(default_factory=list)


def load_config(path: str) -> MonitorConfig:
    """Charge la configuration YAML depuis ``path`` et retourne un ``MonitorConfig``."""

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    interval = int(raw.get("interval_seconds", 5))
    targets_cfg = raw.get("targets", [])

    targets: List[Target] = []
    for t in targets_cfg:
        targets.append(
            Target(
                name=t["name"],
                host=t["host"],
                icmp=bool(t.get("icmp", True)),
                tcp_ports=list(t.get("tcp_ports", [])),
                http_urls=list(t.get("http_urls", [])),
            )
        )

    return MonitorConfig(interval_seconds=interval, targets=targets)
