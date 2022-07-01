# RPLIB

This repo contains the RPLib data, package, and web server.

## Browse data (recommended)
Visit the RPLIB browser at https://birg.dev/rplib/. 

## View RPLIB Card (recommended)
You may view individual cards using the [RPLIB browser](https://birg.dev/rplib/) or for a more customizable experience, use our sample Jupyter notebook that has been tested with Google's Colab: [Click to launch on Colab](https://colab.research.google.com/github/IGARDS/structured_artificial/blob/main/notebooks/RPLIB_Card.ipynb).

## Contribute a dataset (recommended)
We encourage the community to extend this repository with additional data. The recommended procedure for doing so begins with filling out this form: [Click to launch add dataset form](https://docs.google.com/forms/d/e/1FAIpQLSenO1WO_LlzNQ1ak4IPyOjBKkuixZU93umLgeI2kJbFxwzcZQ/viewform).

## Generate artificial data (recommended)
We have also developed a sample notebook for those researchers interested in generating their own artificial data in a compatable format for RPLIB. [Click to launch on Colab](https://colab.research.google.com/github/IGARDS/structured_artificial/blob/main/notebooks/structured_artificial.ipynb). 

## Install instructions
### Prerequisites
graphviz headers must be installed:
```bash
apt-get install -y libgraphviz-dev
```
### Recommended package installation
```bash
pip install pyrplib
```

### Post package installation: Gurobi License
The webserver does not require Gurobi to launch, but to use the full functionality of RPLIB, the Gurobi optimizer must be installed with a valid license. Gurobi provides free academic licenses and more information on obtaining and installing your license can be found here: https://support.gurobi.com/hc/en-us/articles/360040541251. 

### Verify installation
```python
import pyrplib
```

## Development notes
### Launch a version of RPLIB browser locally
### Production
```bash
cd pyrplib
USER=$(id -u) docker-compose up -d --build production
```

### Staging
```bash
cd pyrplib
git checkout staging
USER=$(id -u) docker-compose up -d --build staging
```

### Development environments
cd pyrplib
git checkout <branch>
USER=$(id -u) docker-compose up --build <branch>

### Running tests
```bash
cd pyrplib
python3 -m venv ../env
source ../env/bin/activate
cd tests
pytest card_tests.py
```

## Authors
Paul Anderson, Ph.D.<br>
Brandon Tat<br>
Charlie Ward<br>
Department of Computer Science and Software Engineering<br>
California Polytechnic State University<br>

Kathryn Pedings-Behling<br>
Amy Langville, Ph.D.<br>
Department of Mathematics<br>
College of Charleston<br>

## Acknowledgements
We would like to thank the entire IGARDS team for their invaluable insight and encouragement.