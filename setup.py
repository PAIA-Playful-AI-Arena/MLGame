import sys

import setuptools

# readme.md = github readme.md, 這裡可接受markdown寫法
# 如果沒有的話，需要自己打出介紹此專案的檔案，再讓程式知道
sys.path.append(r".")
import mlgame.version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlgame",  #
    version=mlgame.version.version,
    author="PAIA",
    author_email="service@paia-tech.com",
    description="A machine learning game framework based on Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PAIA-Playful-AI-Arena/MLGame",
    packages=setuptools.find_packages(
        exclude=["tests"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    include_package_data=True,
    keywords=["AI", "machine learning", 'game', 'framework'],

    install_requires=[
        "pygame==2.0.1",
        'pandas==1.4.1',
        "pydantic==1.9.0",
        "websockets==10.2"
    ]

)
