from setuptools import setup

setup(name='pyrplib',
      version='0.1',
      description='RPLIB Python Library',
      url='https://github.com/IGARDS/RPLIB',
      author='Paul Anderson, Brandon Tat, Charlie Ward',
      author_email='pauleanderson',
      license='MIT',
      install_requires=[
          'pytest',
          'dash',
          'matplotlib',
          'nx_altair',
          'pygraphviz',
          'dash_bootstrap_components',
          'requests',
          'pyrankability',
          'joblib'
      ],
      packages=['pyrplib'],
      zip_safe=False)


from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = open(f"{this_directory}/README.md").read()

setup(name='pyrplib',
      version='0.1.1',
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
      packages=['pyrplib'],
      zip_safe=False)

