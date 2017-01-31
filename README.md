# BIDSconversion

FYI: Only takes Resting and Emotion for FMRI as of now

Git clone BIDSConversion

```bash
git clone https://yeunkim@bitbucket.org/yeunkim/bidsconversion.git
```

**DO NOT USE UNDERSCORES IN SUBJECT NAMES**

1. Make text file with full path to input directories for conversion
2. Make configuration file (required for batch conversion):
```bash
  bash BIDSConversion/makeconfigyml.sh ${txt file with input paths} ${OUTPUT_DIR} > batchconfig.yml
```
3. Run batch converter: 
```bash
  dcm2niibatch batchconfig.yml > batchconv_log.txt
```
  * You have to download and buil dcm2niibatch (https://github.com/rordenlab/dcm2niix)
  * Also make sure to have just one T1w and T2w folders
4. Rename and organize files:
```bash
  BIDSConversion/bin/BIDS-organize.py {input_directory} {output_directory} -dataset {name} -subjID {subjID}
```
  * Make a copy of the T2w_inplane files and rename the copy as *_T2w.nii.gz and *_T2w.json
5. Edit JSON files (Total Readout Time for fMRI)
6. Clone https://github.com/yeunkim/HCPPipelines.git and check out the dwi branch:

```bash 
  git clone https://github.com/yeunkim/HCPPipelines.git
  cd HCPPipelines
  git checkout dwi
  docker build -t hcp_dwi .
```

7. Launch docker (subject level, not batch):
  i.e. docker run -ti --rm -v {local_input_dir}:{container_input_dir} -v {local_output_dir}:{containter_output_dir} $CMD {container_input_dir} {container_output_dir} participant -n_cpus {numofcores} --license_key {FreeSurfer_licensekey}

Example usage:
```bash
docker run -ti --rm -v ~/Projects/hcp/:/dataset -v ~/Projects/hcp_output/:/output hcp_dwi /dataset /output participant -n_cpus 8 --license_key ##########
```