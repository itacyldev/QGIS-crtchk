# tun this script from project root
#python3 -m unittest discover . -s test -v
pip install unittest-xml-reporting
pip install coverage

coverage run --data-file=build/coverage-reports/.coverage -m xmlrunner discover . -s test -v -o build/test-results