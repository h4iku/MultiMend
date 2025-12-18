export CFLAGS="-Wno-error=array-bounds"
python setup.py build_ext --inplace -j 0
pip uninstall -y fastparquet
pip install fastparquet==0.4.0