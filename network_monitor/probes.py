"""
Implémentation de sondes réseau simples :
- ICMP (ping)
- TCP connect
- HTTP GET

Les fonctions renvoient des métriques sous forme de dict Python pour
faciliter l'export vers Prometheus.
"""

import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, Optional
import urllib3

import requests

# Désactive les warnings SSL pour les tests (pas pour la production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class ProbeResult:
    """Résultat d'une sonde réseau unique."""

    success: bool
    latency_ms: Optional[float]
    error: Optional[str] = None


def icmp_ping(host: str, timeout: float = 1.0) -> ProbeResult:
    """Effectue un ping ICMP vers ``host`` en utilisant la commande système ``ping``."""

    # Sous Linux, -c pour le nombre de paquets, -W pour le timeout (en secondes)
    cmd = ["ping", "-c", "1", "-W", str(int(timeout)), host]
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        success = proc.returncode == 0
        error = None if success else proc.stderr.strip()
        return ProbeResult(
            success=success,
            latency_ms=elapsed_ms,
            error=error
        )
    except Exception as exc:  # pragma: no cover - cas d'erreur système
        return ProbeResult(success=False, latency_ms=None, error=str(exc))


def tcp_connect(host: str, port: int, timeout: float = 1.0) -> ProbeResult:
    """Tente d'établir une connexion TCP vers (host, port)."""

    start = time.perf_counter()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ProbeResult(success=True, latency_ms=elapsed_ms)
    except Exception as exc:
        return ProbeResult(success=False, latency_ms=None, error=str(exc))
    finally:
        s.close()


def http_get(url: str, timeout: float = 2.0) -> ProbeResult:
    """Envoie une requête HTTP GET vers ``url`` et mesure le temps de réponse."""

    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=timeout, verify=False)
        elapsed_ms = (time.perf_counter() - start) * 1000
        success = 200 <= resp.status_code < 400
        error_msg = None if success else f"HTTP {resp.status_code}"
        return ProbeResult(
            success=success,
            latency_ms=elapsed_ms,
            error=error_msg,
        )
    except requests.exceptions.SSLError:
        # Erreur SSL : message court pour éviter de polluer les métriques
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ProbeResult(
            success=False,
            latency_ms=elapsed_ms,
            error="SSL error"
        )
    except Exception as exc:
        # Limiter la taille des messages d'erreur pour Prometheus
        error_msg = str(exc)[:100] if len(str(exc)) > 100 else str(exc)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ProbeResult(
            success=False,
            latency_ms=elapsed_ms,
            error=error_msg
        )


def result_to_labels(result: ProbeResult) -> Dict[str, str]:
    """Convertit un ``ProbeResult`` en labels textuels pour les métriques."""

    return {
        "status": "up" if result.success else "down",
        "error": result.error or "",
    }
