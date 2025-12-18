pip install cython
pip install numpy
export CFLAGS="-Wno-error=array-bounds"
python setup.py build_ext --inplace --force
