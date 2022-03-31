from setuptools import setup

setup(name='pyrplib',
      version='0.1',
      description='RPLIB Python Library',
      url='https://github.com/IGARDS/RPLib',
      author='Paul Anderson, Brandon Tat, Charlie Ward',
      author_email='pauleanderson',
      license='MIT',
      install_requires=[
          'dash',
          'matplotlib'
      ],
      packages=['pyrplib'],
      zip_safe=False)
