from setuptools import setup, find_packages

setup(
    name="rlviz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "click",
        "python-multipart",
        "h5py",
        "imageio",
        "numpy",
    ],
    include_package_data=True,
    package_data={
        "rlviz": ["static/**/*"],
    },
    entry_points={
        "console_scripts": [
            "rlviz=rlviz.cli:run"
        ]
    },
)

