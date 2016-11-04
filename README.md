# BIDSconversion

FYI: Only takes Resting and Emotion for FMRI as of now

1. Make text file with full path to input directories for conversion
2. Run makeconfigyml.sh folders.txt OUTPUT_DIR > batchconfig.yml
3. Run batch converter: dcm2niibatch batchconfig.yml > batchconv_log.txt
4. Run BIDS-organize.py {input_directory} {output_directory} -dataset {name} -subjID {subjID}
5. Edit JSON files
6. Launch docker

