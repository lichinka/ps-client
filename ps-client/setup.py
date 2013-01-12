from esky import bdist_esky
from distutils.core import setup

setup(name = "PSClient",
         version = "0.1.2",
         description = "PS client v0.1.2",
         install_requires = ["Flask>=0.9"],
         scripts = ["daemon.py"],
         data_files = [("templates", ["templates/index.html"]), ("data", ["data/log.db"]), ("certs", ["certs/disp.crt", "certs/disp.key", "certs/sigen-ca.pem"])],
         options = {"bdist_esky":{"freezer_module": "bbfreeze", "includes": ["jinja2", "jinja2.ext", "log", "logging", "netifaces", "sqlite3"], "excludes": ["django"]}})
