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
sys.path.append('..')
from bidsconversion import readFileNameDICOM

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def natsort(text):
    return(int(text[text.rfind('_') + 1 : ]))

def createPath(odir):
    if not os.path.exists(odir):
        os.makedirs(odir)

def renameFunc(idir, titlePattern_dir, ext, pathAndFilename):
    renamed = []
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
    return [os.path.basename(pathAndFilename) ,titlePattern_dir + '.{0}'.format(ext) ]

def rename(idir, pattern, titlePattern):
    renamed = {}
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
                renames = renameFunc(idir, titlePattern_dir, ext, pathAndFilename)
                renamed[renames[0]] = renames[1]
            else:
                names = (os.path.basename(pathAndFilename)).split('.')
                ext = '.'.join(names[1:])
                renames = renameFunc(idir, titlePattern, ext, pathAndFilename)
                renamed[renames[0]] = renames[1]
    else:
        print 'Cannot find files with pattern {0}, skipping...'.format(pattern)
    return renamed

def anat(subdir):
    return os.path.join(subdir, 'anat')
def dwi(subdir):
    return os.path.join(subdir, 'dwi')
def func(subdir):
    return os.path.join(subdir, 'func')
def fmap(subdir):
    return os.path.join(subdir, 'fmap')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Renames and reorganizes files to be BIDS and BIDS-App compatible. \n"
                                                 "Used with Depression Connectome Project 1/2017. Files are copied NOT moved.",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('input_dir', help="Path to input directory, where converted files are located")
    parser.add_argument('output_dir', help="Path to output directory, where renamed and reorganized files will be placed")
    parser.add_argument('-dataset', dest='dataset', help="Datast name", required=True)
    parser.add_argument('-subjID', dest='subjID', help="subject ID", required=True)
    parser.add_argument('--tfmrifirst', help="Spin echo field map for task fMRI was acquired before the SPE field map"
                                             "for the resting state fMRIs", required= False, action='store_true')
    args = parser.parse_args()

    imageTypes = ['T1W',
                  'T2W',
                  'RFMRI',
                  'TFMRI',
                  'SPINECHOFIELDMAP',
                  'DMRI',
                  'DWI']
    try:

        if not os.path.exists(args.input_dir):
            raise IOError('Directory ' + args.input_dir + ' does not exist.')
        if not os.path.exists(args.output_dir):
            raise IOError('Directory ' + args.output_dir + ' does not exist.')

        idir= glob(args.input_dir)[0]
        odir= os.path.join(glob(args.output_dir)[0], args.dataset)
        subdir= os.path.join(odir,'sub-'+args.subjID)

        try:
            funcFmapPair = readFileNameDICOM.readFileName(idir)
        except:
            print("No functional data found.")

        imageOptions = { "T1W" : anat(subdir),
                         "T2W" : anat(subdir),
                         "RFMRI" : func(subdir),
                         "TFMRI" : func(subdir),
                         "SPINECHOFIELDMAP" : fmap(subdir),
                         "DMRI" : dwi(subdir),
                         "DWI" : dwi(subdir)}

        for folder in os.listdir(idir):
            for imageType in imageTypes:
                    if imageType in folder:
                        newpath = imageOptions[imageType]
                        createPath(newpath)
                        src = os.path.join(idir, folder)
                        files = glob(src + '/' + imageType + '*')
                        for file in files:
                            copyfile(glob(file)[0], os.path.join(newpath, os.path.split(file)[1]))
                    else:
                        continue

        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

        dirs = os.listdir(subdir)
        # dirs.sort(reverse=True)
        for folder in dirs:
            try:
                if folder == "anat":
                    for t in [ 'T1W', 'T2W']:
                        basenames = [os.path.basename(x).split(".")[0] for x in
                                     glob(os.path.join(subdir, folder, '{0}*nii*'.format(t)))]
                        basenames.sort(key=natsort)
                        tImage = basenames[-1]
                        fnpath = glob(subdir + '/' + folder)[0]
                        if t in 'T1W':
                            fn = 'sub-{0}_T1w'.format(args.subjID)
                            renamed = rename(fnpath, '*{0}*'.format(tImage), fn)
                        if t in 'T2W':
                            fn = 'sub-{0}_inplaneT2'.format(args.subjID)
                            renamed = rename(fnpath, '*{0}*'.format(tImage), fn)
                            fn2 = 'sub-{0}_T2w'.format(args.subjID)
                            T2s = glob(os.path.join(subdir, folder, '{0}*'.format(fn)))
                            for t2 in T2s:
                                ext = '.'.join(os.path.split(t2)[1].split('.')[1:])
                                copyfile(glob(t2)[0], os.path.join(subdir, folder, '{0}.{1}'.format(fn2,ext)))
                        for f in basenames[0:len(basenames) - 1]:
                            [os.remove(x) for x in glob(os.path.join(subdir, folder, '*{0}*'.format(f)))]

            except ValueError:
                sys.stdout.write('Please make sure there is only one T1 or T2 image.')

            if folder == "func":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-{0}_task-rest_acq-AP_run-01_sbref'.format(args.subjID)
                FUNCrenamed = rename(fnpath, r'*REST_AP_SBREF*', fn)

                fn = 'sub-{0}_task-rest_acq-PA_run-01_sbref'.format(args.subjID)
                FUNCrenamed.update(rename(fnpath, r'*REST_PA_SBREF*', fn))

                fn = 'sub-{0}_task-rest_acq-AP_run-01_bold'.format(args.subjID)
                FUNCrenamed.update(rename(fnpath, r'*REST_AP*', fn))

                fn = 'sub-{0}_task-rest_acq-PA_run-01_bold'.format(args.subjID)
                FUNCrenamed.update(rename(fnpath, r'*REST_PA*', fn))

                if glob(fnpath+'/*rest*'):
                    rsTRfilename = glob(os.path.join(subdir, folder, '*rest*json'))[0]
                    with open(rsTRfilename, "r") as f:
                        rsData = json.load(f)
                    rsTR = rsData["RepetitionTime"]
                    for i in range(0,2):
                        jsonfn = glob(scriptdir + '/json/*rest*')[i]
                        copyfile(jsonfn, odir + '/' + os.path.basename(jsonfn))
                        with open(os.path.join(odir, os.path.basename(jsonfn)), "r") as f:
                            rsDataTmp = json.load(f)
                            rsDataTmp["RepetitionTime"] = rsTR
                        with open(os.path.join(odir, os.path.basename(jsonfn)), "w") as f:
                            f.write(json.dumps(rsDataTmp))

                taskfiles = glob(fnpath + '/*TFMRI*')
                if taskfiles:
                    tasknames = []
                    for taskfile in taskfiles:
                        tasknames.append(os.path.basename(taskfile).split('_')[1])

                    for taskname in set(tasknames):
                        fn = 'sub-{0}_task-{1}_acq-AP_run-01_sbref'.format(args.subjID, taskname.lower())
                        FUNCrenamed.update(rename(fnpath, r'*{0}_AP_SBREF*'.format(taskname), fn))

                        fn = 'sub-{0}_task-{1}_acq-PA_run-01_sbref'.format(args.subjID, taskname.lower())
                        FUNCrenamed.update(rename(fnpath, r'*{0}_PA_SBREF*'.format(taskname), fn))

                        fn = 'sub-{0}_task-{1}_acq-AP_run-01_bold'.format(args.subjID, taskname.lower())
                        FUNCrenamed.update(rename(fnpath, r'*{0}_AP*'.format(taskname), fn))

                        fn = 'sub-{0}_task-{1}_acq-PA_run-01_bold'.format(args.subjID, taskname.lower())
                        FUNCrenamed.update(rename(fnpath, r'*{0}_PA*'.format(taskname), fn))

                        TRfilename = glob(os.path.join(subdir, folder, '*{0}*json'.format(taskname.lower())))[0]
                        with open(TRfilename, "r") as f:
                            Data = json.load(f)
                        TR = Data["RepetitionTime"]

                        for i in range(0, 2):
                            jsonfn = glob(scriptdir + '/json/*TASKNAME*')[i]
                            copyfile(jsonfn, os.path.join(odir, os.path.basename(jsonfn).replace('TASKNAME', taskname.lower())))
                            jsonfn = jsonfn.replace('TASKNAME', taskname.lower())
                            with open(os.path.join(odir, os.path.basename(jsonfn)), "r") as f:
                                DataTmp = json.load(f)
                                DataTmp["RepetitionTime"] = TR
                                DataTmp["TaskName"] = taskname.lower()
                            with open(os.path.join(odir, os.path.basename(jsonfn)), "w") as f:
                                f.write(json.dumps(DataTmp))

            if folder == "fmap":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_dir-AP_run-01_epi'
                FMAPrenamed = rename(fnpath, r'*FIELDMAP_AP*', fn)

                fn = 'sub-' + args.subjID + '_dir-PA_run-01_epi'
                FMAPrenamed.update(rename(fnpath, r'*FIELDMAP_PA*', fn))

                # edit spin echo field map JSON files
                spinecho = True
                SPElist = glob(fnpath + '/*json')
                SPElist.sort()

                funclist = glob(subdir + '/func/*rest*bold*nii*')
                tasklist = []
                try:
                    if tasknames:
                        for taskname in set(tasknames):
                            tasklist= tasklist + glob(subdir+'/func/*{0}*bold*nii*'.format(taskname.lower()))

                except:
                    sys.stdout.write('No TFMRI detected.')

                speJSONonly = { k:v for k,v in FMAPrenamed.iteritems() if 'json' in k}

                for speOrig, speRenamed in speJSONonly.iteritems():
                    if any(key for key, value in funcFmapPair.flippairdict.iteritems() if speOrig.split('.')[0] in key):
                        funcrenames =[]
                        for func in funcFmapPair.flippairdict[speOrig.split('.')[0]]:
                            funcrenames.append([value for key, value in FUNCrenamed.iteritems() if func in key and 'nii' in key])
                        funcrenames = [ x[0] for x in funcrenames if 'bold' in x[0]]
                        a_dict = {'IntendedFor': funcrenames , 'TotalReadoutTime': 0.060320907 }
                        with open(os.path.join(fnpath, speRenamed)) as f:
                            data = json.load(f)
                        data.update(a_dict)
                        with open(os.path.join(fnpath, speRenamed), 'w') as f:
                            json.dump(data, f)

            if folder == "dwi":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_sbref'
                rename(fnpath, r'DMRI*AP_SBREF*', fn)
                rename(fnpath, r'DWI*AP_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-01_sbref'
                rename(fnpath, r'DMRI*PA_SBREF*', fn)
                rename(fnpath, r'DWI*PA_SBREF*', fn)

                fn = 'sub-' + args.subjID + '_acq-AP_run-01_dwi'
                rename(fnpath, r'DMRI*_AP*', fn)
                rename(fnpath, r'DWI*_AP*', fn)

                fn = 'sub-' + args.subjID + '_acq-PA_run-01_dwi'
                rename(fnpath, r'DMRI*_PA*', fn)
                rename(fnpath, r'DWI*_PA*', fn)


    except:
        print traceback.print_exc(file=sys.stdout)