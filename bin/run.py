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
                                                 "Used with Depression HCP Sequence 1/2017. Files are copied NOT moved.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('sourcedir', help="Path to DICOM source directory, where raw files are located")
    parser.add_argument('outputdir', help="Output directory")
    parser.add_argument('dcm2nii', help='dcm2niibatch program')
    parser.add_argument('-subj', dest='subj', help='SubjID/prefix', required=True)
    parser.add_argument('-dataset', dest='dataset', help='Project name', required=True)
    parser.add_argument('--tfmrifirst', help="Spin echo field maps for task fMRI were acquired prior to resting state"
                                             "fMRI.", required=False, action='store_true')

    args = parser.parse_args()

    try:
        # create list of directories to be converted
        lscmd = 'ls -d ' + args.sourcedir + '/* > ' + args.outputdir + '/dirs.txt'
        subprocess.call(lscmd, shell=True)

        # check paths
        if not os.path.exists(args.outputdir):
            raise IOError('Directory ' + args.outputdir + ' does not exist.')
        if os.path.exists(args.outputdir+'/' + args.subj + '_nii'):
            raise IOError('Directory '+args.outputdir+'/' + args.subj + '_nii' + ' exists. Please rename the directory or delete the directory')

        # create bids directory
        os.mkdir(args.outputdir+'/' + args.subj + '_nii')

        # convert DICOM to NIFTI
        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        makeconfigyml = scriptdir + '/' + 'makeconfigyml.sh'
        bashargs = 'bash ' + makeconfigyml + ' ' + args.outputdir + '/dirs.txt ' + args.outputdir+'/'+args.subj + '_nii' + ' > '  + args.outputdir + '/batchconfig.yml'
        subprocess.call(bashargs, shell=True)
        dcm2niiargs = args.dcm2nii + ' ' + args.outputdir + '/batchconfig.yml' + ' > ' + args.outputdir + '/batchconversion.log'
        subprocess.call(dcm2niiargs, shell=True)

        # run BIDS_organize.py
        if args.tfmrifirst:
            os.mkdir(args.outputdir + '/' + args.subj + '_bids')
            bids_cmd = 'python ' + scriptdir + '/bin/BIDS_organize.py ' + args.outputdir + '/' + args.subj + '_nii ' + args.outputdir + '/' + args.subj + '_bids ' + ' -dataset ' + args.dataset + ' -subjID ' + args.subj +  ' --tfmrifirst' + ' > ' + args.outputdir + '/rename.log'
            subprocess.call(bids_cmd, shell=True)
        else:
            os.mkdir(args.outputdir + '/' + args.subj + '_bids')
            bids_cmd = 'python '+scriptdir+'/bin/BIDS_organize.py '+ args.outputdir+'/'+args.subj+ '_nii ' + args.outputdir+'/'+args.subj+'_bids '+' -dataset '+args.dataset+' -subjID '+args.subj + ' > '  + args.outputdir + '/rename.log'
            subprocess.call(bids_cmd, shell=True)

        bidslogs = os.path.join(args.outputdir, "bids_conversion_logs")
        os.mkdir(bidslogs)
        shutil.move(os.path.join(args.outputdir, "dirs.txt"), os.path.join(bidslogs, "dirs.txt"))
        shutil.move(os.path.join(args.outputdir, "batchconfig.yml"), os.path.join(bidslogs, "batchconfig.yml"))
        shutil.move(os.path.join(args.outputdir, "batchconversion.log"),
                    os.path.join(bidslogs, "batchconversion.log"))
        shutil.move(os.path.join(args.outputdir, "rename.log"), os.path.join(bidslogs, "rename.log"))

    except:
        print traceback.print_exc(file=sys.stdout)