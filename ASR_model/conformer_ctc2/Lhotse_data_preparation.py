from lhotse import RecordingSet, Recording
from lhotse import SupervisionSet, SupervisionSegment
from lhotse import CutSet, Fbank

import os
import codecs

import yaml
with open("conformer_ctc2/main_config.yaml", "r") as main_config_file:
    main_config = yaml.load(main_config_file, Loader=yaml.SafeLoader)
    config_filename = main_config['Current_experiment']['config_filename']

with open(f"conformer_ctc2/configs/{config_filename}","r") as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)

class Lhotse_data_prep:
    def __init__(self):
        self.lang = config['dataset']['lang']
        self.main_audio_dir = config['dataset']['audio_dir']
        self.preprocessed_trans_dir = config['dataset']['transcription_dir']
        self.lists_dir = config['dataset']['lists_dir']
        self.train_lst = config['dataset']['train_list']
        self.test_lst =  config['dataset']['test_list']
        self.dev_lst = config['dataset']['dev_list']
        self.data_dir = config['datamodule']['manifest_dir']
        self.train_cuts_filename = config['datamodule']['train_cuts']
        self.dev_cuts_filename = config['datamodule']['dev_cuts']
        self.test_cuts_filename = config['datamodule']['test_cuts']
        self.gender_in_filename = config['dataset']['gender_in_filename'] # NCHLT speaker folders contain gender in the name, for example "nchlt_afr_001m_0003.wav", but broadcast news filenames do not contain genders.
                 
    def getRecordings(self, list_name):
        new_recordings = []
        with open(os.path.join(self.lists_dir, list_name), 'r') as file:
            fnames = file.read().split('\n')
            if self.gender_in_filename == 'yes':
                for fname in fnames:
                    if len(fname) > 1:
                        spk_dir = fname.split("_")[2][:-1]
                        new_recording = Recording.from_file(os.path.join(self.main_audio_dir,spk_dir,"".join([fname,".wav"]))) 
                        new_recordings.append(new_recording) 

            elif self.gender_in_filename == 'no':
                for fname in fnames:
                    if len(fname) > 1:
                        spk_dir = fname.split("_")[2]
                        new_recording = Recording.from_file(os.path.join(self.main_audio_dir,spk_dir,"".join([fname,".wav"])))  
                        new_recordings.append(new_recording)

        recs_all = RecordingSet.from_recordings(new_recordings)
        return recs_all

    def getSupervisions(self, list_name, recSet):
        supervision_segments = []
        
        with open(os.path.join(self.lists_dir, list_name), 'r') as file:
            fnames = file.read().split('\n')
            for fname in fnames:
                if len(fname) > 1:
                    trans_path = os.path.join(self.preprocessed_trans_dir, "".join([fname,".txt"]))
                    trans_file_handle = codecs.open(trans_path, "r", "utf-8")
                    trans = trans_file_handle.readlines()[0].split('\n')[0]
                    trans_file_handle.close()
                    
                    supervision_id = "".join([fname,"-sup"])
                    recording_id = fname
                    rec_duration = recSet.duration(recording_id)
                    transcription = trans

                    if self.gender_in_filename == 'yes':
                        spk_dir = fname.split("_")[2][:-1]
                    if self.gender_in_filename == 'no':
                        spk_dir = fname.split("_")[2]
        
                    sup_seg = SupervisionSegment(id=supervision_id, recording_id=recording_id, start=0, duration=rec_duration, channel=0, text=transcription, speaker=spk_dir, language=self.lang)
                    supervision_segments.append(sup_seg)
                    
            sups_all = SupervisionSet.from_segments(supervision_segments)
        
        return sups_all

    def saveManifest(self, recs, sups, jsonl_prefix):
        """
        """
        recs.to_file(os.path.join(self.data_dir,"".join([jsonl_prefix,"_recordings.jsonl"])))
        sups.to_file(os.path.join(self.data_dir,"".join([jsonl_prefix,"_supervisions.jsonl"])))

        return

    def cutsetFromManifests(self, recs, sups):
        """
        """
        cuts = CutSet.from_manifests(recordings=recs, supervisions=sups)
        
        return cuts

    def featuresFbank(self, cuts, cutset_filename):
        """
        """
        prefix = "_".join(cutset_filename.split("_")[:-1])  # e.g. if cutset name is "zul_nchlt_train_cuts.jsonl" then fbank output will be "zul_nchlt_train_feats"
        return cuts.compute_and_store_features(extractor=Fbank(), storage_path=os.path.join(self.data_dir, "fbank","".join([prefix,"_","feats"])))
        
    def saveCuts(self, cuts, cutset_output_filename):
        """
        """
        
        cuts.to_file(os.path.join(self.data_dir, cutset_output_filename))

        return
    
    def generate_cutset(self, split):
        if split == 'train':
            list_name = self.train_lst
            cutset_filename = self.train_cuts_filename

        elif split == 'dev':
            list_name = self.dev_lst
            cutset_filename = self.dev_cuts_filename

        elif split == 'test':
            list_name = self.test_lst
            cutset_filename = self.test_cuts_filename

        recs_all = self.getRecordings(list_name)
        sups_all = self.getSupervisions(list_name, recs_all)
        #saveManifest(recs_all, sups_all, f'{self.lang}_{option}')
        cuts_all = self.cutsetFromManifests(recs_all, sups_all)
        cuts_all = self.featuresFbank(cuts_all, cutset_filename)
        self.saveCuts(cuts_all, cutset_filename)
        cuts_all.describe()
            
if __name__ == "__main__":
    data_prep = Lhotse_data_prep()  
    data_prep.generate_cutset(split="train")
    data_prep.generate_cutset(split="dev")
    data_prep.generate_cutset(split="test")