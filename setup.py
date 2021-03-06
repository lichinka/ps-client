#!/usr/bin/env python
# -*- coding: utf8 -*-

#
# Setup installation script for PS-Client
#
import os
import sys
try:
    from setuptools import setup, Extension, Command
except ImportError:
    from distutils.core import setup, Extension, Command


def get_version ( ):
    VERSION = os.path.abspath (os.path.join (os.path.dirname (__file__),
                               'VERSION'))
    with open (VERSION, 'r') as f:
        for line in f:
            ret = line.split ('\n')[0]
            assert ret.count ('.') == 2, ret
            for num in ret.split ('.'):
                assert num.isdigit ( ), ret
            return ret
        else:
            raise ValueError ("Couldn't find version string")
    f.close ( )


def get_description ( ):
    README = os.path.abspath (os.path.join (os.path.dirname (__file__),
                              'README'))
    with open (README, 'r') as f:
        return f.read ( )
    f.close ( )


def get_requirements ( ):
    """
    Returns a setup-friendly tuple for the 'install_requires' field,
    generated with the contents of 'file_name'.-
    """
    import platform
    REQUIRE = os.path.abspath (os.path.join (os.path.dirname (__file__),
                              'requirements_%s.txt' % platform.system ( )))
    with open (REQUIRE, 'r') as f:
        ret_value = []
        for pkg in f:
            pkg = pkg.strip ( )
            if len (pkg) > 0 and pkg[0] != '#':
                ret_value.append (pkg)
        return ret_value
    f.close ( )


class PyTest (Command):
    """
    Implements the command:

        $> python setup.py test

    using the 'runtests.py' script, generated by PyTest.-
    """
    user_options = []
    def initialize_options (self):
        pass

    def finalize_options (self):
        pass

    def run (self):
        import subprocess
        errno = subprocess.call ([sys.executable,
                                 'runtests.py',
                                 'ps-client'])
        raise SystemExit (errno)

#
# Windows
#
if sys.platform.startswith("win32"):

    def get_winver():
        major, minor = sys.getwindowsversion()[0:2]
        return '0x0%s' % ((major * 100) + minor)

    extensions = [Extension('_psutil_mswindows',
                            sources=['psutil/_psutil_mswindows.c',
                                     'psutil/_psutil_common.c',
                                     'psutil/arch/mswindows/process_info.c',
                                     'psutil/arch/mswindows/process_handles.c',
                                     'psutil/arch/mswindows/security.c'],
                            define_macros=[('_WIN32_WINNT', get_winver()),
                                           ('_AVAIL_WINVER_', get_winver())],
                            libraries=["psapi", "kernel32", "advapi32",
                                       "shell32", "netapi32", "iphlpapi",
                                       "wtsapi32"],
                            #extra_compile_args=["/Z7"],
                            #extra_link_args=["/DEBUG"]
                            )]
#
# Linux
#
elif sys.platform.startswith("linux"):
    extensions = [Extension ('_psutil_linux',
                             sources=['psutil/_psutil_linux.c'])]
else:
    sys.exit ('ERROR: platform %s is not supported' % sys.platform)


def main ( ):
    setup_args = dict (
        name='PSClient',
        version=get_version ( ),
        description='Client module of the PowerServer system',
        long_description=get_description ( ),
        install_requires=get_requirements ( ),
        dependency_links=["git+git://github.com/lichinka/dbus-python.git#egg=dbus-python-10.1.1"],
        scripts = ['ps-client/daemon.py'],
        packages=['ps-client'],
        cmdclass = {'test': PyTest},
        keywords=['PowerServer', 'client'],
        author='Bostjan Kaluza, Dejan Petelin, Lucas Benedicic',
        author_email='powerserver@gmail.com',
        maintainer='PowerServer Team',
        maintainer_email='powerserver <at> gmail <dot> com',
        url='http://ps.ijs.si/',
        platforms='Platform Independent',
        license='License :: OSI Approved :: BSD License',
        classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Environment :: Console',
              'Operating System :: Microsoft',
              'Operating System :: Microsoft :: Windows :: Windows NT/2000',
              'Operating System :: POSIX',
              'Operating System :: POSIX :: Linux',
              'Operating System :: OS Independent',
              'Programming Language :: C',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Topic :: System :: Monitoring',
              'Topic :: System :: Hardware',
              'Topic :: System :: Networking',
              'Topic :: System :: Systems Administration',
              'Topic :: Utilities',
              'Intended Audience :: Developers',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: BSD License',
              ],
        )
    setup (**setup_args)


if __name__ == '__main__':
    main ( )
