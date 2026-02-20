"""Setup script for Network Monitor."""

from setuptools import find_packages, setup

setup(
    name="network-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "prometheus-client>=0.21.0",
        "pyyaml>=6.0.2",
        "requests>=2.32.3",
    ],
    python_requires=">=3.10",
)
