## Network Monitor - Automatisation de tests & supervision réseau

**Objectif** : automatiser des **campagnes de tests de performances réseau** (latence / disponibilité) et les **superviser en temps réel** pour mesurer la robustesse d'une infrastructure réseau.

- **Python** (`network_monitor/`) : sondes ICMP, TCP, HTTP orchestrées par un runner.
- **Métriques Prometheus** : endpoint `/metrics` sur le port `8000`.
- **Supervision** : Prometheus + Grafana (via `docker-compose`) avec un dashboard préconfiguré.
- **Documentation** : génération automatique avec **Doxygen** à partir des commentaires du code.
- **CI/CD** : pipeline **GitHub Actions** (lint, tests, génération de doc).

---

### Comment lancer le projet (WSL / Linux)

**1. Pré-requis système**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip doxygen graphviz \
  docker.io docker-compose-plugin
```

Optionnel mais recommandé pour Docker :

```bash
sudo usermod -aG docker $USER

```

**2. Installer les dépendances Python**

Depuis la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Lancer les sondes réseau + endpoint Prometheus**

```bash
source .venv/bin/activate       
python -m network_monitor.runner \
  --config targets.yaml \
  --interval 5
```

- Les cibles de test sont décrites dans `targets.yaml`.
- Les métriques sont exposées sur `http://localhost:8000/metrics`.
- Les snapshots JSON sont stockés dans `results/`.

**4. Démarrer Prometheus + Grafana**

Dans un autre terminal (toujours à la racine du projet) :

```bash
docker compose up
```

- Prometheus écoute sur `http://localhost:9090` et scrape `http://host.docker.internal:8000/metrics`.
- Grafana écoute sur `http://localhost:3000` (login `admin` / `admin`).
- Un dashboard **Network Monitor - Latence & Disponibilité** est automatiquement importé.

**5. Générer la documentation technique (Doxygen)**

```bash
doxygen Doxyfile
```

La doc HTML est générée dans `docs/html/index.html` 
