# tun this script from project root
#pip install unittest-xml-reporting
#pip install coverage
#python3 -m xmlrunner discover . -s test -v -o build/test-results
#sudo chmod 777 /usr/lib/python3/dist-packages/coverage
python3-coverage run -m xmlrunner discover . -s test -v -o build/test-results