# BIDSconversion

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
7. Clone https://github.com/yeunkim/HCPPipelines.git and check out the psychopy2fsl branch:

```bash 
  git clone https://github.com/yeunkim/HCPPipelines.git
  cd HCPPipelines
  git checkout psychopy2fsl
  docker build -t hcppipelines .
```

7. Launch docker (subject level, not batch):
  i.e. docker run -ti --rm -v {local_input_dir}:{container_input_dir} -v {local_output_dir}:{containter_output_dir} $CMD {container_input_dir} {container_output_dir} -subjID {subjID} -dataset {study_name} --n_cpus {numofcores} --license_key {FreeSurfer_licensekey}

Example usage:
```bash
docker run -ti --rm -v ~/Projects/hcp/:/dataset -v ~/Projects/hcp_output/:/output hcppipelines /dataset /output -subjID k001 --n_cpus 4 -dataset DEPRESSION --license_key ########## 
```
