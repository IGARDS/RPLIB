from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = open(f"{this_directory}/README.md").read()

setup(name='pyrplib',
      version='0.1.2',
      description='Ranking Python Library',
      url='https://github.com/IGARDS/ranking_toolbox',
      author='Paul Anderson, Amy Langville, Kathryn Pedings-Behling, Brandon Tat,  Charlie Ward',
      author_email='pauleanderson@gmail.com',
      license='MIT',
      install_requires=[
          'pyrankability',
          'joblib',
          'dash_bootstrap_components',
          'requests',
          'dash',
      ],
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      zip_safe=False)

