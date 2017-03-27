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
                                                 "Used with Depression Connectome Project 1/2017. Files are copied NOT moved.",
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
            # if "T1W" in folder and "RMS" in folder:
            if "T1W" in folder and "SETTER" not in folder:
                newpath=subdir+'/'+ 'anat'
                createPath(newpath)
                src=idir+'/'+folder+'/'

                files=glob(src+'/T1W*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            # elif "T2W" in folder and "VNAV" in folder:
            elif "T2W" in folder and "SETTER" not in folder:
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

            elif "DWI" in folder and "PHYSIOLOG" not in folder:
                newpath = subdir + '/' + 'dwi'
                createPath(newpath)
                src = idir + '/' + folder + '/'
                files = glob(src + '/DWI*')
                for file in files:
                    copyfile(glob(file)[0], newpath + '/' + os.path.split(file)[1])

            else:
                continue

        scriptdir = dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

        dirs = os.listdir(subdir)
        dirs.sort(reverse=True)
        for folder in dirs:
            try:
                if folder == "anat":
                    # if len(glob(subdir + '/' + folder + '/*T1W*nii*')) > 1:
                    basenames = [os.path.basename(x).split(".")[0] for x in glob(subdir + '/' + folder + '/*T1W*nii*')]
                    basenames.sort(key=natsort)
                    T1fn = basenames[-1]
                    # if len(glob(subdir + '/' + folder + '/*T2W*nii*')) > 1:
                    basenames = [os.path.basename(x).split(".")[0] for x in glob(subdir + '/' + folder + '/*T2W*nii*')]
                    basenames.sort(key=natsort)
                    T2fn = basenames[-1]

                    fnpath = glob(subdir+'/'+folder)[0]

                    fn = 'sub-'+args.subjID+'_T1w'
                    rename(fnpath, '*'+T1fn+'*', fn)

                    fn = 'sub-' + args.subjID + '_inplaneT2'
                    rename(fnpath, '*'+T2fn+'*', fn)

                    [os.remove(x) for x in glob(subdir + '/' + folder + '/*T1W*')]
                    [os.remove(x) for x in glob(subdir + '/' + folder + '/*T2W*')]

                    T2s = glob(subdir + '/' + folder + '/*inplane*')
                    for t in T2s:
                        fn = 'sub-' + args.subjID + '_T2w.'
                        ext = '.'.join(os.path.split(t)[1].split('.')[1:])
                        copyfile(glob(t)[0], os.path.split(t)[0] + '/' + fn + ext)

            except ValueError:
                sys.stdout.write('Please make sure there is only one T1 or T2 image.')
            if folder == "func":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-{0}_task-rest_acq-AP_run-01_sbref'.format(args.subjID)
                rename(fnpath, r'*REST_AP_SBREF*', fn)

                fn = 'sub-{0}_task-rest_acq-PA_run-01_sbref'.format(args.subjID)
                rename(fnpath, r'*REST_PA_SBREF*', fn)

                fn = 'sub-{0}_task-rest_acq-AP_run-01_bold'.format(args.subjID)
                rename(fnpath, r'*REST_AP*', fn)

                fn = 'sub-{0}_task-rest_acq-PA_run-01_bold'.format(args.subjID)
                rename(fnpath, r'*REST_PA*', fn)

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
                        fn = 'sub-{0}_task-{1}_acq-AP_run-01_sbref'.format(args.subjID, taskname)
                        rename(fnpath, r'*{0}_AP_SBREF*'.format(taskname), fn)

                        fn = 'sub-{0}_task-{1}_acq-PA_run-01_sbref'.format(args.subjID, taskname)
                        rename(fnpath, r'*{0}_PA_SBREF*'.format(taskname), fn)

                        fn = 'sub-{0}_task-{1}_acq-AP_run-01_bold'.format(args.subjID, taskname)
                        rename(fnpath, r'*{0}_AP*'.format(taskname), fn)

                        fn = 'sub-{0}_task-{1}_acq-PA_run-01_bold'.format(args.subjID, taskname)
                        rename(fnpath, r'*{0}_PA*'.format(taskname), fn)

                        TRfilename = glob(os.path.join(subdir, folder, '*{0}*json'.format(taskname)))[0]
                        with open(TRfilename, "r") as f:
                            Data = json.load(f)
                        TR = Data["RepetitionTime"]
                        try:
                            tsv = glob(scriptdir + '/tsv/*{0}*'.format(taskname))
                            copyfile(tsv[0], os.path.join(fnpath, '/sub-{0}_{1}'.format(args.subjID, os.path.basename(tsv[0]))))
                            copyfile(tsv[1], os.path.join(fnpath, '/sub-{0}_{1}'.format(args.subjID, os.path.basename(tsv[1]))))
                        except:
                            sys.stdout.write('tsv files for {0} task fMRI not added yet.\n'.format(taskname))
                        for i in range(0, 2):
                            jsonfn = glob(scriptdir + '/json/*TASKNAME*')[i]
                            copyfile(jsonfn, os.path.join(odir, os.path.basename(jsonfn).replace('TASKNAME', taskname)))
                            jsonfn = jsonfn.replace('TASKNAME', taskname)
                            with open(os.path.join(odir, os.path.basename(jsonfn)), "r") as f:
                                DataTmp = json.load(f)
                                DataTmp["RepetitionTime"] = TR
                                DataTmp["TaskName"] = taskname
                            with open(os.path.join(odir, os.path.basename(jsonfn)), "w") as f:
                                f.write(json.dumps(DataTmp))

            if folder == "fmap":
                fnpath = glob(subdir + '/' + folder)[0]

                fn = 'sub-' + args.subjID + '_dir-AP_run-01_epi'
                rename(fnpath, r'*FIELDMAP_AP*', fn)

                fn = 'sub-' + args.subjID + '_dir-PA_run-01_epi'
                rename(fnpath, r'*FIELDMAP_PA*', fn)

                # edit spin echo field map JSON files
                spinecho = True
                SPElist = glob(fnpath + '/*json')
                SPElist.sort()

                funclist = glob(subdir + '/func/*rest*bold*nii*')
                tasklist = []
                if tasknames:
                    for taskname in set(tasknames):
                        tasklist= tasklist + glob(subdir+'/func/*{0}*bold*nii*'.format(taskname))
                # carit = glob(subdir + '/func/*carit*bold*nii*')
                # face = glob(subdir + '/func/*face*bold*nii*')
                # emotion = glob(subdir + '/func/*EMOTION*bold*nii*')

                # tasklist = carit + face + emotion
                if len(tasklist) > 0:
                    rsbasenames = ['func/' + os.path.basename(x) for x in funclist]
                    a_dict = {'IntendedFor': rsbasenames, 'TotalReadoutTime': 0.060320907}
                    if len(SPElist) > 2:
                        for i in [0,2]:
                            with open(SPElist[i]) as f:
                                data =json.load(f)
                            data.update(a_dict)
                            with open(SPElist[i], 'w') as f:
                                json.dump(data, f)
                        taskbasenames = ['func/' + os.path.basename(x) for x in tasklist]
                        a_dict = {'IntendedFor': taskbasenames, 'TotalReadoutTime': 0.060320907}
                        for i in [1,3]:
                            with open(SPElist[i]) as f:
                                data = json.load(f)
                            data.update(a_dict)
                            with open(SPElist[i], 'w') as f:
                                json.dump(data, f)
                    else:
                        allfunclist = funclist + tasklist
                        basenames = ['func/' + os.path.basename(x) for x in allfunclist]
                        a_dict = {'IntendedFor': basenames, 'TotalReadoutTime': 0.060320907}
                        for i in [0,1]:
                            with open(SPElist[i]) as f:
                                data = json.load(f)
                            data.update(a_dict)
                            with open(SPElist[i], 'w') as f:
                                json.dump(data, f)
                else:
                    rsbasenames = ['func/' + os.path.basename(x) for x in funclist]
                    a_dict = {'IntendedFor': rsbasenames, 'TotalReadoutTime': 0.060320907}
                    for i in [0, 1]:
                        with open(SPElist[i]) as f:
                            data = json.load(f)
                        data.update(a_dict)
                        with open(SPElist[i], 'w') as f:
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