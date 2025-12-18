pip install git+https://github.com/encode/requests-async.git@0.5.0
python setup.py build
python setup.py install
pip3 install -e .[dev]
pip3 install -e .
pip3 install -e .[test]