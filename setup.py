from setuptools import setup, find_packages

setup(
    name="rlviz",  # The name of your package
    version="0.1.0",           # Version of your package
    author="Joel Woodfield",
    author_email="joelwoodfield@gmail.com",
    description="Visualizer for RL",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/joel-woodfield/rl_visualizer",  # Link to your GitHub repository
    packages=find_packages(),  # Automatically find all packages in your project
    install_requires=[         # List of dependencies (if any)
        'torch',
        'tqdm',
        'imageio',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose the appropriate license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',   # Specify the Python versions you support
)
