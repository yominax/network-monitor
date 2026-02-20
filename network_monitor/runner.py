"""
Boucle principale de Network Monitor.

Lit une configuration YAML, exécute périodiquement des sondes réseau sur
les cibles définies et expose les résultats sous forme de métriques
Prometheus via un petit serveur HTTP.
"""

import argparse
import json
import threading
import time
from pathlib import Path
from typing import Dict

from prometheus_client import Gauge, start_http_server

from .config import MonitorConfig, load_config
from .probes import (
    http_get,
    icmp_ping,
    result_to_labels,
    tcp_connect
)


ICMP_LATENCY = Gauge(
    "network_icmp_latency_ms",
    "Latence ICMP mesurée vers une cible",
    ["target", "host", "status", "error"]
)
TCP_LATENCY = Gauge(
    "network_tcp_connect_latency_ms",
    "Temps d'établissement TCP",
    ["target", "host", "port", "status", "error"]
)
HTTP_LATENCY = Gauge(
    "network_http_latency_ms",
    "Latence HTTP GET",
    ["target", "url", "status", "error"]
)


def run_once(config: MonitorConfig, results_dir: Path) -> None:
    """Exécute une campagne de tests et met à jour les métriques."""

    snapshot: Dict[str, Dict] = {"timestamp": time.time(), "targets": []}

    for target in config.targets:
        tgt_data = {
            "name": target.name,
            "host": target.host,
            "probes": []
        }

        if target.icmp:
            res = icmp_ping(target.host)
            labels = {
                "target": target.name,
                "host": target.host,
                **result_to_labels(res)
            }
            ICMP_LATENCY.labels(**labels).set(res.latency_ms or 0.0)
            tgt_data["probes"].append({
                "type": "icmp",
                "result": res.__dict__
            })

        for port in target.tcp_ports:
            res = tcp_connect(target.host, port)
            labels = {
                "target": target.name,
                "host": target.host,
                "port": str(port),
                **result_to_labels(res)
            }
            TCP_LATENCY.labels(**labels).set(res.latency_ms or 0.0)
            tgt_data["probes"].append({
                "type": "tcp",
                "port": port,
                "result": res.__dict__
            })

        for url in target.http_urls:
            res = http_get(url)
            labels = {
                "target": target.name,
                "url": url,
                **result_to_labels(res)
            }
            HTTP_LATENCY.labels(**labels).set(res.latency_ms or 0.0)
            tgt_data["probes"].append({
                "type": "http",
                "url": url,
                "result": res.__dict__
            })

        snapshot["targets"].append(tgt_data)

    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    out_file = results_dir / f"snapshot_{timestamp}.json"
    content = json.dumps(snapshot, indent=2)
    out_file.write_text(content, encoding="utf-8")


def loop(
    config: MonitorConfig,
    results_dir: Path,
    stop_event: threading.Event
) -> None:
    """Boucle infinie de tests, s'arrêtant lorsque stop_event est posé."""

    while not stop_event.is_set():
        run_once(config, results_dir)
        stop_event.wait(config.interval_seconds)


def parse_args() -> argparse.Namespace:
    desc = "Network Monitor - sondes réseau avec export Prometheus."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Chemin vers le fichier YAML de configuration."
    )
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=None,
        help=(
            "Intervalle entre deux campagnes (secondes). "
            "Écrase la valeur du YAML si fourni."
        ),
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Répertoire où stocker les snapshots JSON.",
    )
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=8000,
        help="Port HTTP pour exposer les métriques Prometheus.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    if args.interval is not None:
        cfg.interval_seconds = args.interval

    results_dir = Path(args.results_dir)

    # Démarre le serveur Prometheus
    start_http_server(args.metrics_port)

    stop_event = threading.Event()

    try:
        loop(cfg, results_dir, stop_event)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    main()
