#!/usr/bin/python

import inspect, os, shutil
import argparse
import traceback
import sys
import subprocess
from argparse import RawTextHelpFormatter
from os.path import dirname, abspath

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Wrapper script to convert and organize files/folders. \n"
                                                 "Used with Depression HCP Sequence 1/2017. Files are copied NOT moved."
                                                 "Does not support session naming at this point in time.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('sourcedir', help="Path to DICOM source directory, where raw files are located")
    parser.add_argument('outputdir', help="Output directory")
    parser.add_argument('-dcm2nii', help='dcm2niibatch program. Argument not needed if run with Docker.',
                        required=False, default='/dcm2niix/build/bin/dcm2niibatch')
    parser.add_argument('-subj', dest='subj', help='subject ID or prefix', required=True)
    parser.add_argument('-dataset', dest='dataset', help='Project name', required=False)

    args = parser.parse_args()

    try:
        # create list of directories to be converted
        lscmd = 'ls -d ' + args.sourcedir + '/* > ' + args.outputdir + '/dirs.txt'
        subprocess.call(lscmd, shell=True)

        niftiDir = args.subj + '_nii'
        # check paths
        if not os.path.exists(args.outputdir):
            raise IOError('Directory ' + args.outputdir + ' does not exist.')
        if os.path.exists(args.outputdir+ os.sep + niftiDir):
            raise IOError('Directory '+args.outputdir+ os.sep + niftiDir + ' exists. Please rename the directory or delete the directory')

        # create bids directory
        os.mkdir(args.outputdir+ os.sep + niftiDir)

        # convert DICOM to NIFTI
        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        makeconfigyml = scriptdir + os.sep + 'makeconfigyml.sh'
        bashargs = 'bash ' + makeconfigyml + ' ' + \
                   args.outputdir + '/dirs.txt ' + \
                   args.outputdir+ os.sep + niftiDir + \
                   ' > '  + args.outputdir + '/batchconfig.yml'
        subprocess.call(bashargs, shell=True)

        dcm2niiargs = args.dcm2nii + ' ' + \
                      args.outputdir + '/batchconfig.yml' + ' > ' + \
                      args.outputdir + '/batchconversion.log'
        subprocess.call(dcm2niiargs, shell=True)

        # run BIDS_organize.py
        bidsDataset = args.subj + '_bids'
        os.mkdir(args.outputdir + os.sep + bidsDataset)
        if args.dataset:
            dataset = ' -dataset {0}'.format(args.dataset)
        else:
            dataset = ' '
        bids_cmd = 'python ' + scriptdir + '/bin/BIDS_organize.py ' + \
                   args.outputdir + os.sep + niftiDir + ' ' + \
                   args.outputdir + os.sep + bidsDataset + ' ' + \
                   dataset + ' -subjID ' + args.subj + ' > ' + \
                   args.outputdir + '/rename.log'
        subprocess.call(bids_cmd, shell=True)

        bidslogs = os.path.join(args.outputdir, "bids_conversion_logs")
        os.mkdir(bidslogs)

        #move logs files
        shutil.move(os.path.join(args.outputdir, "dirs.txt"), os.path.join(bidslogs, "dirs.txt"))
        shutil.move(os.path.join(args.outputdir, "batchconfig.yml"), os.path.join(bidslogs, "batchconfig.yml"))
        shutil.move(os.path.join(args.outputdir, "batchconversion.log"),
                    os.path.join(bidslogs, "batchconversion.log"))
        shutil.move(os.path.join(args.outputdir, "rename.log"), os.path.join(bidslogs, "rename.log"))

    except:
        print traceback.print_exc(file=sys.stdout)