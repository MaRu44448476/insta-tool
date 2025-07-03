from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="instagram-trend-tool",
    version="1.0.0",
    author="Instagram Trend Tool",
    description="Instagram trend analysis tool for hashtag-based post collection and ranking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "instaloader==4.11",
        "pandas==2.2.2",
        "python-dateutil==2.9.0",
        "click==8.1.7",
        "python-dotenv==1.0.1",
        "slack-sdk==3.27.1",
        "pyyaml==6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "insta-trend=insta_trend_tool.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)