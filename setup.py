from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="airops",
    version="0.1.0",
    author="Muhammet Ayan",
    author_email="muhammet.ayan@hotmail.com",
    description="A Python library to enhance the efficiency and flexibility of Apache Airflow operators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/airops",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "apache-airflow",
    ],
)
