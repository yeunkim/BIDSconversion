#!/usr/bin/python

import inspect, os
from os.path import dirname, abspath
import sys
import argparse
from argparse import RawTextHelpFormatter
from shutil import copyfile
import fnmatch
from glob import glob
import traceback


def createPath(odir):
    if not os.path.exists(odir):
        os.makedirs(odir)

def rename(idir, pattern, titlePattern):
    try:
        for pathAndFilename in glob(os.path.join(idir, pattern)):
            names = (os.path.basename(pathAndFilename)).split('.')
            ext = '.'.join(names[1:])
            print names[0]
            if os.path.exists(os.path.join(idir, titlePattern+'.{0}'.format(ext))):
                exists = True
                while exists:
                    idx = titlePattern.find('run') + 5
                    run = str(int(titlePattern[idx]) + 1)
                    s = list(titlePattern)
                    s[idx] = run
                    titlePattern = "".join(s)
                    if not os.path.exists(os.path.join(idir, titlePattern + '.{0}'.format(ext))):
                        exists = False
            os.rename(pathAndFilename,os.path.join(idir, titlePattern+'.{0}'.format(ext)))
    except:
        sys.stdout('Cannot find files with pattern {0} in {1}, skipping...'.format(pattern, idir))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Renames and reorganizes files to be BIDS and BIDS-App compatible. \n"
                                                 "Used with UCLA HCP Sequence 10/2016. Files are copied NOT moved.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('input_dir', help="Path to input directory, where converted files are located")
    parser.add_argument('output_dir', help="Path to output directory, where renamed and reorganized files will be placed")
    parser.add_argument('-dataset', dest='dataset', help="Datast name", required=True)
    parser.add_argument('-subjID', dest='subjID', help="subject ID", required=True)

    args = parser.parse_args()

    try:

        if not os.path.exists(args.input_dir):
            raise IOError('Directory ' + args.input_dir + ' does not exist.')
        if not os.path.exists(args.output_dir):
            raise IOError('Directory ' + args.output_dir + ' does not exist.')

        idir=glob(args.input_dir)[0]
        odir= glob(args.output_dir)[0]+'/'+args.dataset

        subdir= odir+'/'+'sub-'+args.subjID

        for folder in os.listdir(idir):
            if "T1W" in folder:
                newpath=subdir+'/'+ 'anat'
                createPath(newpath)
                src=idir+'/'+folder+'/'
                files=glob(src+'/T1W_MPR_20*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "T2W" in folder:
                newpath = subdir + '/' + 'anat'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/T2W*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "RFMRI" in folder:
                newpath = subdir + '/' + 'func'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/RFMRI*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "TFMRI" in folder:
                newpath = subdir + '/' + 'func'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/TFMRI*')
                for file in files:
                    copyfile(glob(file)[0], newpath+'/'+os.path.split(file)[1])

            elif "FIELDMAP" in folder:
                newpath = subdir + '/' + 'fmap'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/*FIELDMAP*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "DWI" in folder:
                newpath = subdir + '/' + 'dwi'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/DWI*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            else:
                continue

        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

        for folder in os.listdir(subdir):
            if folder == "anat":
                fnpath = glob(subdir+'/'+folder)[0]

                fn = 'sub-'+args.subjID+'_T1w'
                rename(fnpath, r'T1W*', fn)

                fn = 'sub-' + args.subjID + '_inplaneT2'
                rename(fnpath, r'T2W*', fn)
            if folder == "func":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_task-rest_run-01_sbref'
                rename(fnpath, r'*REST_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_run-02_sbref'
                rename(fnpath, r'*REST_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_run-01_bold'
                rename(fnpath, r'*REST_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_run-02_bold'
                rename(fnpath, r'*REST_PA*', fn)

                if os.path.exists(glob(fnpath+'/*rest*')[0]):
                    json = glob(scriptdir + '/json/*rest*')[0]
                    copyfile(json, odir + '/' + os.path.basename(json))


                fn = 'sub-' + args.subjID + '_task-emotionregulation_run-01_sbref'
                rename(fnpath, r'*EMOTION_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-emotionregulation_run-02_sbref'
                rename(fnpath, r'*EMOTION_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-emotionregulation_run-01_bold'
                rename(fnpath, r'*EMOTION_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-emotionregulation_run-02_bold'
                rename(fnpath, r'*EMOTION_PA*', fn)

                if os.path.exists(glob(fnpath + '/*emotion*')[0]):
                    tsv = glob(scriptdir + '/tsv/*emotion*')
                    copyfile(tsv[0], fnpath + '/sub-' + args.subjID + '_'+ os.path.basename(tsv[0]))
                    copyfile(tsv[1], fnpath + '/sub-' + args.subjID + '_'+ os.path.basename(tsv[1]))
                    json = glob(scriptdir + '/json/*emotion*')[0]
                    copyfile(json, odir+'/'+os.path.basename(json))
            if folder == "fmap":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_dir-AP_epi'
                rename(fnpath, r'*FIELDMAP_AP*', fn)

                fn = 'sub-' + args.subjID + '_dir-PA_epi'
                rename(fnpath, r'*FIELDMAP_PA*', fn)
            if folder == "dwi":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_sbref'
                rename(fnpath, r'DWI*AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-02_sbref'
                rename(fnpath, r'DWI*PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_dwi'
                rename(fnpath, r'DWI*_AP*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-02_dwi'
                rename(fnpath, r'DWI*_PA*', fn)


    except:
        print traceback.print_exc(file=sys.stdout)