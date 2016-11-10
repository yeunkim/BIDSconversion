# BIDSconversion

FYI: Only takes Resting and Emotion for FMRI as of now

**DO NOT USE UNDERSCORES IN SUBJECT NAMES**

1. Make text file with full path to input directories for conversion
2. Make configuration file (required for batch conversion):
  makeconfigyml.sh ${txt file with input paths} ${OUTPUT_DIR} > batchconfig.yml
3. Run batch converter: 
  dcm2niibatch batchconfig.yml > batchconv_log.txt
  * You have to download and buil dcm2niibatch (https://github.com/rordenlab/dcm2niix)
4. Rename and organize files:
  BIDS-organize.py {input_directory} {output_directory} -dataset {name} -subjID {subjID}
5. Edit JSON files (Total Readout Time for fMRI)
6. Clone https://github.com/yeunkim/HCPPipelines_dev.git and build:
  docker build -t hcp_dwi .
7. Launch docker (subject level, not batch):
  i.e. docker run -ti --rm -v {local_input_dir}:{container_input_dir} -v {local_output_dir}:{containter_output_dir} $CMD {container_input_dir} {container_output_dir} participant -n_cpus {numofcores} --license_key {FreeSurfer_licensekey}

Example usage:
docker run -ti --rm -v ~/Projects/hcp/:/dataset -v ~/Projects/hcp_output/:/output hcp_dwi /dataset /output participant -n_cpus 8 --license_key ##########
