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
import re
import json

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def natsort(text):
    return(int(text[text.rfind('_') + 1 : ]))

def createPath(odir):
    if not os.path.exists(odir):
        os.makedirs(odir)

def rename(idir, pattern, titlePattern):
    if glob(os.path.join(idir, pattern)):
        files = glob(os.path.join(idir, pattern))
        files.sort(key=natural_keys)
        for pathAndFilename in files:
            if "dwi" in idir:
                names = (os.path.basename(pathAndFilename)).split('.')

                ext = '.'.join(names[1:])
                parts = (os.path.basename(pathAndFilename)).split('_')
                direction = next(x for x in parts if "DIR" in x)
                newname = titlePattern.split('-')
                tmp=direction.lower() + newname[2]
                newname[2] = tmp
                titlePattern_dir = '-'.join(newname)

                if os.path.exists(os.path.join(idir, titlePattern_dir + '.{0}'.format(ext))):
                    exists = True
                    while exists:
                        idx = titlePattern_dir.find('run') + 5
                        run = str(int(titlePattern_dir[idx]) + 1)
                        s = list(titlePattern_dir)
                        s[idx] = run
                        titlePattern_dir = "".join(s)
                        if not os.path.exists(os.path.join(idir, titlePattern_dir + '.{0}'.format(ext))):
                            exists = False
                print os.path.basename(pathAndFilename), " --> ", (titlePattern_dir + '.{0}'.format(ext))
                os.rename(pathAndFilename, os.path.join(idir, titlePattern_dir + '.{0}'.format(ext)))
            else:
                names = (os.path.basename(pathAndFilename)).split('.')
                ext = '.'.join(names[1:])

                if os.path.exists(os.path.join(idir, titlePattern + '.{0}'.format(ext))):
                    exists = True
                    while exists:
                        idx = titlePattern.find('run') + 5
                        run = str(int(titlePattern[idx]) + 1)
                        s = list(titlePattern)
                        s[idx] = run
                        titlePattern = "".join(s)
                        if not os.path.exists(os.path.join(idir, titlePattern + '.{0}'.format(ext))):
                            exists = False
                print os.path.basename(pathAndFilename), " --> ",(titlePattern + '.{0}'.format(ext))
                os.rename(pathAndFilename, os.path.join(idir, titlePattern + '.{0}'.format(ext)))

    else:
        print 'Cannot find files with pattern {0}, skipping...'.format(pattern)

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
            if "T1W" in folder and "RMS" in folder:
                newpath=subdir+'/'+ 'anat'
                createPath(newpath)
                src=idir+'/'+folder+'/'

                files=glob(src+'/T1W*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "T2W" in folder and "VNAV" in folder:
                newpath = subdir + '/' + 'anat'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/T2W*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "RFMRI" in folder and "PHYSIOLOG" not in folder:
                newpath = subdir + '/' + 'func'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/RFMRI*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "TFMRI" in folder and "PHYSIOLOG" not in folder:
                newpath = subdir + '/' + 'func'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/TFMRI*')
                for file in files:
                    copyfile(glob(file)[0], newpath+'/'+os.path.split(file)[1])

            elif "FIELDMAP" in folder and "ASL" not in folder:
                newpath = subdir + '/' + 'fmap'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/*FIELDMAP*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            elif "DMRI" in folder and "PHYSIOLOG" not in folder:
                newpath = subdir + '/' + 'dwi'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/DMRI*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            else:
                continue

        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

        for folder in os.listdir(subdir):
            # try:
            #     if folder == "anat":
            #         # if len(glob(subdir + '/' + folder + '/*T1w*')) > 1:
            #
            #
            # 
            #         fnpath = glob(subdir+'/'+folder)[0]
            #
            #         fn = 'sub-'+args.subjID+'_T1w'
            #         rename(fnpath, r'T1W*', fn)
            #
            #         fn = 'sub-' + args.subjID + '_inplaneT2'
            #         rename(fnpath, r'T2W*', fn)
            #
            #         T2s = glob(subdir + '/' + folder + '/')
            #         for t in T2s:
            #             fn = 'sub-' + args.subjID + '_T2w.'
            #             ext = '.'.join(os.path.split(t)[1].split('.')[1:])
            #             copyfile(glob(t)[0], os.path.split(t)[0] + '/' + fn + ext)
            #
            # except ValueError:
            #     sys.stdout.write('Please make sure there is only one T1 or T2 image.')
            if folder == "func":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_task-rest_acq-AP_run-01_sbref'
                rename(fnpath, r'*REST_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_acq-PA_run-01_sbref'
                rename(fnpath, r'*REST_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_acq-AP_run-01_bold'
                rename(fnpath, r'*REST_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-rest_acq-PA_run-01_bold'
                rename(fnpath, r'*REST_PA*', fn)

                if glob(fnpath+'/*rest*'):
                    for i in range(0,2):
                        json = glob(scriptdir + '/json/*rest*')[i]
                        copyfile(json, odir + '/' + os.path.basename(json))

                fn = 'sub-' + args.subjID + '_task-EMOTION_acq-AP_run-01_sbref'
                rename(fnpath, r'*EMOTION_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-EMOTION_acq-PA_run-01_sbref'
                rename(fnpath, r'*EMOTION_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-EMOTION_acq-AP_run-01_bold'
                rename(fnpath, r'*EMOTION_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-EMOTION_acq-PA_run-01_bold'
                rename(fnpath, r'*EMOTION_PA*', fn)

                if glob(fnpath + '/*EMOTION*'):
                    tsv = glob(scriptdir + '/tsv/*EMOTION*')
                    copyfile(tsv[0], fnpath + '/sub-' + args.subjID + '_'+ os.path.basename(tsv[0]))
                    copyfile(tsv[1], fnpath + '/sub-' + args.subjID + '_'+ os.path.basename(tsv[1]))
                    for i in range(0,2):
                        json = glob(scriptdir + '/json/*EMOTION*')[i]
                        copyfile(json, odir+'/'+os.path.basename(json))

                fn = 'sub-' + args.subjID + '_task-carit_acq-AP_run-01_sbref'
                rename(fnpath, r'*CARIT_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-carit_acq-PA_run-01_sbref'
                rename(fnpath, r'*CARIT_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-carit_acq-AP_run-01_bold'
                rename(fnpath, r'*CARIT_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-carit_acq-PA_run-01_bold'
                rename(fnpath, r'*CARIT_PA*', fn)

                if glob(fnpath + '/*carit*'):
                    for i in range(0, 1):
                        json = glob(scriptdir + '/json/*carit*')[0]
                        copyfile(json, odir + '/' + os.path.basename(json))
                    try:
                        tsv = glob(scriptdir + '/tsv/*carit*')
                        copyfile(tsv[0], fnpath + '/sub-' + args.subjID + '_' + os.path.basename(tsv[0]))
                        copyfile(tsv[1], fnpath + '/sub-' + args.subjID + '_' + os.path.basename(tsv[1]))
                    except:
                        sys.stdout.write('tsv files for CARIT task fMRI not added yet.\n')

                fn = 'sub-' + args.subjID + '_task-facematching_acq-AP_run-01_sbref'
                rename(fnpath, r'*FACEMATCHING_AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-facematching_acq-PA_run-01_sbref'
                rename(fnpath, r'*FACEMATCHING_PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_task-facematching_acq-AP_run-01_bold'
                rename(fnpath, r'*FACEMATCHING_AP*', fn)

                fn = 'sub-' + args.subjID + '_task-facematching_acq-PA_run-01_bold'
                rename(fnpath, r'*FACEMATCHING_PA*', fn)

                if glob(fnpath + '/*face*'):
                    for i in range(0, 1):
                        json = glob(scriptdir + '/json/*face*')[0]
                        copyfile(json, odir + '/' + os.path.basename(json))
                    try:
                        tsv = glob(scriptdir + '/tsv/*face*')
                        copyfile(tsv[0], fnpath + '/sub-' + args.subjID + '_' + os.path.basename(tsv[0]))
                        copyfile(tsv[1], fnpath + '/sub-' + args.subjID + '_' + os.path.basename(tsv[1]))
                    except:
                        sys.stdout.write('tsv files for FACEMATCHING task fMRI not added yet.\n')


            if folder == "fmap":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_dir-AP_run-01_epi'
                rename(fnpath, r'*FIELDMAP_AP*', fn)

                fn = 'sub-' + args.subjID + '_dir-PA_run-01_epi'
                rename(fnpath, r'*FIELDMAP_PA*', fn)

                # edit spin echo field map JSON files
                spinecho = True
                SPElist = glob(fnpath + '/*json')

                funclist = glob(subdir + '/func/*rest*bold*nii*' )
                basenames = [ 'func/'+ os.path.basename(x) for x in funclist ]

                a_dict = {'Intended For' : basenames, 'TotalReadoutTime' : 0.060320907}

                for i in range(0,2):
                    with open(SPElist[i]) as f:
                        data =json.load(f)
                    data.update(a_dict)
                    with open(SPElist[i], 'w') as f:
                        json.dump(data, f)

                carit = glob(subdir + '/func/*carit*bold*nii*')
                face = glob(subdir + '/func/*face*bold*nii*')
                tasklist = carit + face
                taskbasenames = ['func/'+ os.path.basename(x) for x in tasklist ]
                a_dict = {'Intended For' : taskbasenames, 'TotalReadoutTime' : 0.060320907}

                for i in range(2,4):
                    with open(SPElist[i]) as f:
                        data =json.load(f)
                    data.update(a_dict)
                    with open(SPElist[i], 'w') as f:
                        json.dump(data, f)

            if folder == "dwi":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_sbref'
                rename(fnpath, r'DMRI*AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-01_sbref'
                rename(fnpath, r'DMRI*PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_dwi'
                rename(fnpath, r'DMRI*_AP*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-01_dwi'
                rename(fnpath, r'DMRI*_PA*', fn)


    except:
        print traceback.print_exc(file=sys.stdout)