#!/bin/bash

#
# Start the Selenium server
#
#-firefoxProfileTemplate /home/luka/.mozilla/firefox/firefox_testing_profile \
#
java -jar $(pwd)/../lib/python2.7/site-packages/SeleniumLibrary/lib/selenium-server.jar \
     -port 4444 \
     -singleWindow \
     -trustAllSSLCertificates \
     -userExtensions $(pwd)/../lib/python2.7/site-packages/SeleniumLibrary/lib/user-extensions.js > $(pwd)/tests/selenium_server.log &

#
# Give the Selenium server some time to warm up
#
sleep 1

#
# Run the tests for PS-Client
#
../bin/pybot --pythonpath .:./tests --outputdir ./tests tests/test_daemon.txt
