# BIDSconversion

FYI: Only takes Resting and Emotion for FMRI as of now

1. Make text file with full path to input directories for conversion
2. Make configuration file (required for batch conversion):
  makeconfigyml.sh ${txt file with input paths} ${OUTPUT_DIR} > batchconfig.yml
3. Run batch converter: 
  dcm2niibatch batchconfig.yml > batchconv_log.txt
  * You have to download and buil dcm2niibatch (https://github.com/rordenlab/dcm2niix)
4. Rename and organize files:
  BIDS-organize.py {input_directory} {output_directory} -dataset {name} -subjID {subjID}
5. Edit JSON files (Total Readout Time for fMRI)
6. Launch docker:
  i.e. docker run -ti --rm -v {local_input_dir}:{container_input_dir} -v {local_output_dir}:{containter_output_dir} $CMD {container_input_dir} {container_output_dir} participant -n_cpus {numofcores} --license_key {FreeSurfer_licensekey}

