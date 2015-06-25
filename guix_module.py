#!/usr/bin/env python2.7

#=======================================================================
# Author(s): Ben Woodcroft
#
# Copyright 2015
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================

import argparse
import subprocess
import logging
import re
import os

class GuixInfo:
    def __init__(self, guix_package_name):
        cmd = "guix package --show=%s" % guix_package_name
        logging.info("Running cmd: %s" % cmd)
        output = subprocess.check_output(cmd, shell=True)
        
        if output=='':
            raise Exception("Unfortunately it appears there is no '%s' package in guix" % guix_package_name)
        
        infos = {}
        r = re.compile("(.+?): (.*)")
        last_key = None
        for l in output.split("\n"):
            if len(l) == 0: continue
            if l[0] == '+':
                if not last_key:
                    raise Exception("info started with a + ?!!?!: %s" % l)
                infos[last_key] += ' '
                infos[last_key]+= l[1:]
            else:
                o = r.search(l)
                if o:
                    last_key = o.groups(0)[0].strip()
                    value = o.groups(0)[1].strip()
                    infos[last_key] = value
                else:
                    raise Exception("Badly parsed info line: %s" % l)
                
        # these throw errors if they don't exist, so don't need to check
        self.name = infos['name']
        self.version = infos['version']
        self.synopsis = infos['synopsis']
        self.description = infos['description']
        
class SearchPaths:
    def __init__(self, guix_profile_path):
        cmd = "guix package -p '%s' --search-paths" % guix_profile_path
        logging.info("Running cmd: %s" % cmd)
        output = subprocess.check_output(cmd, shell=True)
        
        self.search_paths = {}
        r = re.compile("export (.+?)=(.+)")
        for l in output.split("\n"):
            if len(l) == 0: continue
            o = r.search(l)
            if o:
                last_key = o.groups(0)[0].strip()
                value = o.groups(0)[1].strip()
                self.search_paths[last_key] = value
            else:
                raise Exception("Badly parsed --search-paths line: %s" % l)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-i','--install', metavar='package_name', help='package to be installed', required=True)
    parser.add_argument('--guix_package_name', metavar='name', help='the name of the package in guix (default: the one specified with --install)')
    parser.add_argument('-t','--test_directory', metavar='path', help='run guix, but output to this directory for testing (default: unused)')
    parser.add_argument('--sw_directory', metavar='path', help='path to base directory of where to install the guix profile', default='/srv/sw')
    parser.add_argument('--module_directory', metavar='path', help='path to base directory of where to install the module file', default='/srv/modulefiles')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    guix_package_name = args.install
    if args.guix_package_name:
        guix_package_name = args.guix_package_name
    
    # make sure that the guix package exists, and gather info on it at the same time
    # using guix package --show=guix_package_name
    guix_info = GuixInfo(guix_package_name)
    
    # create or make sure that the directory exists on the server
    # use package_name/version
    if args.test_directory:
        sw_folder = os.path.join(args.test_directory, 'sw', args.install, guix_info.version)
        modulefile_folder = os.path.join(args.test_directory, args.install)
    else:
        sw_folder = os.path.join(args.sw_directory, args.install, guix_info.version)
        modulefile_folder = os.path.join(args.module_directory, args.install)
    guix_profile_path = os.path.join(sw_folder, 'guix_package')
    module_file = os.path.join(modulefile_folder, guix_info.version)
    
    # ensure 'guix_profile' doesn't exist as a folder in that directory
    # ensure that the modulefile does not already exist
    if os.path.exists(sw_folder):
        raise Exception("A folder already exists at %s" % sw_folder)
    if not os.path.isdir(sw_folder):
        os.makedirs(sw_folder)
    if os.path.exists(module_file):
        raise Exception("A modulefile already exists at %s" % module_file)
    if not os.path.isdir(modulefile_folder):
        os.makedirs(modulefile_folder)
    
    # run guix package -i to do the actual installation to the profile
    cmd = "guix package -p '%s' -i %s" % (guix_profile_path, guix_package_name)
    logging.info("Running cmd: %s" % cmd)
    subprocess.check_call(cmd, shell=True)
    print "Do not worry about above notices that 'The following environment variable definitions may be needed'"
    
    # run guix package --search-paths to get the paths
    paths = SearchPaths(guix_profile_path)
    
    # write info and etc to the module file,
    with open(module_file,'w') as mfile:
        mfile.write("#%Module######################################################################\n")
        mfile.write("#\n")
        mfile.write("#        %s modulefile\n" % args.install)
        mfile.write("#        generated from guix package %s/%s\n" % 
                    (guix_info.name, guix_info.version))
        mfile.write("#\n")
        mfile.write("proc ModulesHelp { } {\n")
        mfile.write("    puts stderr \"%s\"\n" % guix_info.synopsis)
        mfile.write("}\n")
        mfile.write("\n")
        for env_name, env_value in paths.search_paths.iteritems():
            mfile.write("prepend-path %s %s\n" % (env_name, env_value))
            
    logging.info("Installation and modulefile creation appears to have completed without any problems.")
                    
        
