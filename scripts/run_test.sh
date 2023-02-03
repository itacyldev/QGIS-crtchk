# tun this script from project root
#python3 -m unittest discover . -s test -v
pip install unittest-xml-reporting
python3 -m xmlrunner discover . -s test -v -o build/test-results
