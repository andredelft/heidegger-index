from setuptools import setup, find_packages

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="heidegger_index",
    version="1.0",
    description="Heidegger index",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "add-ref=index:ar_click",
            "format-refs=index:fr_click",
        ]
    },
)
