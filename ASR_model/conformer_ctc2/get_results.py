 
import os
import codecs

import yaml
with open("main_config.yaml", "r") as main_config_file:
    main_config = yaml.load(main_config_file, Loader=yaml.SafeLoader)
    config_filename = main_config['Current_experiment']['config_filename']

with open(f"configs/{config_filename}","r") as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)

output_filename = config['decode']['output_filename']

for i in range(1,41): ## Each 'i' represents the epoch checkpoint number
    
    decode_args = [
        f"--epoch {str(i)}",
        f"--avg {config['decode']['average']}",
        f"--test_cuts_fname {config['datamodule']['test_cuts']}",
        f"--use-averaged-model={config['decode']['use_averaged_model']}",
        f"--method {config['decode']['method']}",
        f"--exp-dir {config['train']['exp_dir']}",
        f"--lang-dir {config['datamodule']['lang_dir']}",
        f"--lm-dir {config['datamodule']['lm_dir']}",
        f"--manifest-dir {config['datamodule']['manifest_dir']}",
        f"--num-decoder-layers={config['decode']['num_decoder_layers']}"
    ]

    cmd_string = f"python conformer_ctc2/decode_no_sil.py {' '.join(decode_args)} 2>> {config['train']['exp_dir']}/{output_filename}"
    print(cmd_string)
    
    #Store command
    out_handle = codecs.open(f"{config['train']['exp_dir']}/{output_filename}", "a", "utf-8")
    out_handle.write("\n\n")
    out_handle.write(cmd_string)
    out_handle.close()
    
    os.system(cmd_string)

    # #Store compilation of WER results for each epoch 
    with open(f"{config['train']['exp_dir']}/wer-summary-test_cuts.txt") as file:  ## "wer-summary-test_cuts.txt" is generated by the decode script by default, and contains the WER result
        contents = file.read().split('\n')
        WER = contents[1].split('\t')[1]

    out_handle = codecs.open(f"{config['train']['exp_dir']}/WER_compilation.txt", "a", "utf-8")
    out_handle.write(f"Epoch_{i}\t{WER}\n")
    out_handle.close()