import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="backtrader-oandav20",
    version="0.1.0",
    description="Integrate Oanda-V20 API into backtrader",
    long_description=long_description,
    license='GNU General Public License Version 3',
    url="https://github.com/ftomassetti/backtrader-oandav20",
    packages=setuptools.find_packages(),
    install_requires=[
        'backtrader>=1.9',
        'pyyaml',
        'v20'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6'
)