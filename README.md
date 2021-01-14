# Setup

* Working in `virtualenv`:
    * Python v3.7.x+ is required.
    * Setup virtual environment:
        * `python3 -m venv .venv && source .venv/bin/activate`
    * Install components:
        * `pip install -r requirements_test.txt`

* Deactivate virtualenv:
    * `deactivate`


___

# Typical Running of Script

* Make sure virtualenv is active in the terminal:
    * `source .venv/bin/activate`
* Run:
    * `./robomars.py -h`
    * `./robomars.py <input_file>`

* E.g. some samples:
    * `./robomars.py  tests/testfiles/sample_input`
    * `./robomars.py  tests/testfiles/sample_input_noblanklines`

* E.g. run all samples, good and bad:
    * `./.runallsamples`


___

# Testing

* Using **pytest**:
    * `PYTHONPATH=. pytest`
    * `PYTHONPATH=. pytest --junit-xml=testresults.xml --cov-report=html --cov-branch --cov=src`


___
