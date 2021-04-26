from setuptools import setup, find_packages

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="heidegger_index",
    version="1.0",
    description="Heidegger index",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "hi-add=index:add_to_index"
        ]
    }
)
