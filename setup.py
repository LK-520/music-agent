from setuptools import find_packages, setup


setup(
    name="music-agent",
    version="0.1.0",
    description="Local background music agent for Hermes/OpenClaw.",
    packages=find_packages(include=["musicctl*", "musicd*", "shared*"]),
    entry_points={
        "console_scripts": [
            "musicctl=musicctl.cli:main",
        ]
    },
)
