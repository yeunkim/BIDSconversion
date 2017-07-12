#!/usr/bin/python

import os
import operator

def natsort(text):
    return (int(text[text.rfind('_') + 1:]))

class readFileName(object):
    def __init__(self, inputdir):
        self.dicoms = os.listdir(inputdir)
        self.fmridict = {}
        self.spedict = {}
        self.sorted_fmridict = {}
        self.sorted_spedict = {}
        self.pairdict = {}
        self.flippairdict = {}
        self.createDict()
        self.pairfMRItoSPE()
        self.flipSPEtofMRI()

    def createDict(self):
        for dicom in self.dicoms:
            if "FMRI" in dicom:
                self.fmridict[str(dicom)] = natsort(dicom)
            if "SPINECHOFIELDMAP" in dicom:
                self.spedict[dicom] = natsort(dicom)

        self.sorted_fmridict = sorted(self.fmridict.items(), key=operator.itemgetter(1))
        self.sorted_spedict = sorted(self.spedict.items(), key=operator.itemgetter(1))

    def pairfMRItoSPE(self):
        for fmri, order in self.sorted_fmridict:
            spes = [ spe for spe, num in self.sorted_spedict if num < order ]
            # print(spes)
            self.pairdict[fmri] = spes[-2:]
            # check if there is AP and PA
            assert any("AP" in s for s in spes) and any("PA" in s for s in spes)

    def flipSPEtofMRI(self):
        spes = self.pairdict.values()
        unique = set(key for spe in spes for key in spe)

        for spe in unique:
            self.flippairdict[spe] = []
            for fmri, fieldmaps in self.pairdict.iteritems():
                if any(spe in f for f in fieldmaps):
                    self.flippairdict[spe].append(fmri)

