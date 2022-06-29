from setuptools import setup

setup(name='pyrplib',
      version='0.1',
      description='RPLIB Python Library',
      url='https://github.com/IGARDS/RPLIB',
      author='Paul Anderson, Brandon Tat, Charlie Ward',
      author_email='pauleanderson',
      license='MIT',
      install_requires=[
          'dash',
          'matplotlib',
          'nx_altair',
          'pygraphviz',
          'dash_bootstrap_components'
      ],
      packages=['pyrplib'],
      zip_safe=False)
