from setuptools import setup, find_packages

setup(
    name="iran-insurance-management",
    version="1.0.0",
    author="Hasnabadi 37751",
    description="Iran Insurance Installment Management Software",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.9",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "reportlab>=4.0.0",
        "jdatetime>=4.1.0",
        "arabic-reshaper>=3.0.0",
        "python-bidi>=0.4.2",
    ],
    entry_points={
        "console_scripts": [
            "iran-insurance=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
