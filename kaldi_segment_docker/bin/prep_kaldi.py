# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2019 Meraka Institute, CSIR, South Africa.                    #
#                                                                             #
# See the 'LICENSE' file in the project root folder for                       #
# licensing information.                                                      #
#                                                                             #
###############################################################################
#                                                                             #
# AUTHOR  : Jaco Badenhorst                                                   #
# DATE    : May 2019                                                          #
#                                                                             #
###############################################################################
"""
A module encapsulating functionality to prepare compatible L.fst and G.fst
files Kaldi requires for a specific acoutic model and dictionary.
"""

import logging
import os
import codecs
import subprocess
#import openfst_python as fst_lib



SPHINX_JSGF2FSG_DIR = "/opt/sphinxbase/src/sphinx_jsgf2fsg"

class GetGraph(object):
    """
    A simple class implementing process to generate HCLG.fst graph.
    """

    def __init__(self, config):
        """
        Initialize generation process with an input configuration
        and execute.

        Args:
            config (dict): A dictionary with configuration settings.

        """

        self.config = config

        logging.getLogger(__name__).addHandler(logging.NullHandler())

        #Create L.fst
        self.prep_dict(config["UTILS"], config["DICT"], os.path.join(self.config["MAIN_DIR"], config["DICT_DIR"]), config["DICT_OUT"],
                       config["NO_SIL_PHS"], config["SIL_PHS"], config["OPT_SIL_PHS"], config["EXTRA_QUES"])

        self.prep_lang(config["UTILS"], os.path.join(config["MODEL_DIR"], "phones.txt"), os.path.join(self.config["MAIN_DIR"], config["DICT_DIR"]),
                       os.path.join(self.config["MAIN_DIR"], config["TMP_DIR"]),
                       os.path.join(self.config["MAIN_DIR"], config["LANG_DIR"]))

        #Create G.fst
        if config["LM_SWITCH"]:
            self.arpa_to_fst(config["UTILS"], self.config["LM"], os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"], "words.txt"), os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"]))

        elif config["FST_SWITCH"]:
            self.fst_to_compatible(config["UTILS"], self.config["GFST"], self.config["GFST_MAP"], os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"], "words.txt"), os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"]), os.path.join(self.config["MAIN_DIR"], self.config["GRAM_DIR"]))
            
        else:

            self.to_fsm(os.path.join(self.config["MAIN_DIR"], self.config["GRAM_DIR"]),
                    self.config["JSGF"], self.config["FSM"], self.config["SYMTAB"])

            self.map_word_ids(os.path.join(self.config["MAIN_DIR"], self.config["GRAM_DIR"]),
                          self.config["SYMTAB"], os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"], "words.txt"), self.config["MAPPED_SYMTAB"])

            self.fst_compile(os.path.join(self.config["MAIN_DIR"], self.config["GRAM_DIR"]),
                         self.config["MAPPED_SYMTAB"], self.config["FSM"], self.config["FST"], os.path.join(self.config["MAIN_DIR"], self.config["LANG_DIR"]))


        #Create HCLG.fst
        self.make_graph(config["UTILS"], os.path.join(self.config["MAIN_DIR"], config["LANG_DIR"]), config["MODEL_DIR"],
                        os.path.join(self.config["MAIN_DIR"], config["GRAPH_DIR"]))


    def prep_dict(self, utils_dir, pronun, dict_dir, out_pronun, nosil_phs, sil_phs, opt_sil_phs, extra_ques):
        """
        Create Kaldi compatible pronunciation dictionary directory.
        """

        #Remove </s> and <s>, sort

        dict_entries = []
        non_sil_phones = []
        sil_phones = ["sil"]
        opt_sil_phones = ["sil"]
        with codecs.open(pronun, "r", "utf-8") as dict_handle:
            for line in dict_handle:
                line_parts = line.split()
                wtoken = line_parts[0]
                wpronun = line_parts[1:]
                if wtoken not in ["</s>","<s>"]:
                    dict_entries.append([wtoken, wpronun])

                    for phone in wpronun:
                        if phone not in sil_phones and phone not in non_sil_phones:
                            non_sil_phones.append(phone)

        #Add to the lexicon the silences, noises etc.
        dict_entries.append(["!SIL", ["sil"]])

        non_sil_phones.sort()
        dict_entries.sort(key=lambda x:x[0], reverse=False)

        with codecs.open(os.path.join(dict_dir, out_pronun), "w", "utf-8") as dict_handle:
            for entry in dict_entries:
                dict_handle.write("".join(["\t".join([entry[0]," ".join(entry[1])]),"\n"]))

        #make list of non-silence phones
        with codecs.open(os.path.join(dict_dir, nosil_phs), "w", "utf-8") as phones_handle:
            for ph in non_sil_phones:
                phones_handle.write("".join([ph, "\n"]))

        #make list of silence phones
        with codecs.open(os.path.join(dict_dir, sil_phs), "w", "utf-8") as phones_handle:
            for ph in sil_phones:
                phones_handle.write("".join([ph, "\n"]))

        #make list of optional silence phones
        with codecs.open(os.path.join(dict_dir, opt_sil_phs), "w", "utf-8") as phones_handle:
            for ph in opt_sil_phones:
                phones_handle.write("".join([ph, "\n"]))

        #make extra questions - not used in current setup
        codecs.open(os.path.join(dict_dir, extra_ques), 'w').close()


        cmd_string = " ".join([os.path.join(utils_dir,"validate_dict_dir.pl"), dict_dir])
#        result = subprocess.check_output(cmd_string, shell=True)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

        logging.info(result)

    def prep_lang(self, utils_dir, ph_sym_table, dict_dir, tmp_dir, lang_dir):
        """
        Create L.fst with phone symbol labels matching an existing Kaldi acoustic model.
        """

        cmd_string = " ".join([os.path.join(utils_dir,"prepare_lang.sh"),
                               "--position-dependent-phones", "false", "--num-sil-states", "3",
                               "--phone_symbol_table", ph_sym_table, dict_dir,
                               "'!SIL'", tmp_dir, lang_dir])
#        os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))


    def arpa_to_fst(self, utils_dir, lm, kaldi_words, lang_dir):
        """
        Given an ARPA language model produce the required G.fst
        """

        cmd_string = " ".join([os.path.join(utils_dir,"find_arpa_oovs.pl"), kaldi_words, lm, ">", os.path.join(lang_dir,"oovs.txt")])
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))
        #os.system(cmd_string)


        #Note - If LM in correct format and kaldi_words correct this should be able to be much shorter.
        #Should only require arpa2fst with the correct settings.
        cmd_string = " ".join(["cat",lm,"|","grep -v \'<s> <s>\'","|","grep -v \'</s> <s>\'","|",
                              "grep -v \'</s> </s>\'","|","arpa2fst","- |","fstprint","|",
                              os.path.join(utils_dir, "remove_oovs.pl"),os.path.join(lang_dir,"oovs.txt"),
                              "|",os.path.join(utils_dir, "eps2disambig.pl"),"|",os.path.join(utils_dir, "s2eps.pl"),
                              "|","fstcompile","".join(["--isymbols=",kaldi_words]),"".join(["--osymbols=",kaldi_words]),
                              "--keep_isymbols=false","--keep_osymbols=false","|","fstrmepsilon","|","fstarcsort",
                              "--sort_type=ilabel",">",os.path.join(lang_dir,"G.fst")])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

    def to_fsm(self, gram_dir, jsgf, fsm, symtab):
        """
        Convert JSGF file to Sphinx FSM and symtab files.
        """

        cmd_string = " ".join([os.path.join(SPHINX_JSGF2FSG_DIR, "sphinx_jsgf2fsg"), "-jsgf",
                               jsgf, "-fsm", os.path.join(gram_dir, fsm),
                               "-symtab", os.path.join(gram_dir, symtab)])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))


    def map_word_ids(self, gram_dir, in_symtab, kaldi_words, out_symtab):
        """
        Map the labels in the symtab file to be compatible with the word labels of
        L.fst.
        """

        #Read Kaldi words map
        kaldi_words_map = {}

        with codecs.open(kaldi_words, "r", "utf-8") as map_handle:
            for line in map_handle:
                line_parts = line.split()
                wtoken = line_parts[0]
                wint = line_parts[1]

                if wtoken not in kaldi_words_map:
                    kaldi_words_map[wtoken] = wint
                else:
                    print("Warning - duplicate token in Kaldi words file!")

        symbol_map = []

        with codecs.open(os.path.join(gram_dir, in_symtab), "r", "utf-8") as symtab_handle:
            for line in symtab_handle:
                line_parts = line.split()
                wtoken = line_parts[0]
                wint = line_parts[1]

                new_wint = kaldi_words_map[wtoken]
                symbol_map.append([wtoken, int(new_wint)])

        symbol_map.sort(key=lambda x:x[1], reverse=False)

        with codecs.open(os.path.join(gram_dir, out_symtab), "w", "utf-8") as symtab_handle:
            for map_item in symbol_map:
                symtab_handle.write("".join([" ".join([map_item[0],str(map_item[1])]),"\n"]))


    def fst_compile(self, gram_dir, symtab, fsm, fst, lang_dir):
        """
        Create an FST acceptor from the Sphinx FSM applying appropriate symtab.
        Ilable sort the FST to be compatible with Kaldi.
        Check if Gfst is stochastic.
        """

        cmd_string = " ".join(["fstcompile", "--acceptor", "".join(["--isymbols=",os.path.join(gram_dir, symtab)]), "".join(["--osymbols=",os.path.join(gram_dir, symtab)]), "--keep_isymbols=false", "--keep_osymbols=false", os.path.join(gram_dir, fsm), os.path.join(gram_dir, fst)])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))


        cmd_string = " ".join(["fstarcsort", "--sort_type=ilabel", os.path.join(gram_dir, fst), ">", os.path.join(lang_dir, "G.fst")])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

        cmd_string = " ".join(["fstisstochastic", os.path.join(lang_dir, "G.fst")])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

        #result = subprocess.check_output(cmd_string, shell=True)
        #logging.info(result)

    def make_graph(self, utils_dir, lang_dir, model_dir, graph_dir):
        """
        Create complete graph required for decoding: HCLG.fst
        """

        cmd_string = " ".join([os.path.join(utils_dir, "mkgraph.sh"), lang_dir, model_dir, graph_dir])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

    def fst_to_compatible(self, utils_dir, fst, fst_map, kaldi_words, lang_dir, gram_dir):
        """
        Given G.fst produce the required G.fst compatible with L.fst
        kaldi_words contain the int word map for L.fst
        """
        
        fst_labels = {}
        new_labels = {}
        
        with codecs.open(kaldi_words, "r", "utf-8") as map_handle:
            for line in map_handle:
                line_parts = line.split()
                wtoken = line_parts[0]
                wint = int(line_parts[1])
                new_labels[wtoken] = wint
        
        with codecs.open(fst_map, "r", "utf-8") as old_map_handle:
            for line in old_map_handle:
                line_parts = line.split()
                wtoken = line_parts[0]
                wint = int(line_parts[1])
                fst_labels[wint] = new_labels[wtoken]
        
        self.relabel_gfst_manual(fst, fst_labels, gram_dir, lang_dir)
        
        #Using openfst-python
        #gfst = fst_lib.Fst.read(fst)
        #gfst = self.relabel_gfst(gfst, fst_labels)
        #gfst.write(os.path.join(lang_dir, "G.fst"))
        

    def relabel_gfst_manual(self, gfst, int_dict, gram_dir, lang_dir):
        """
        """
        
        cmd_string = " ".join(["fstprint", gfst, os.path.join(gram_dir, "G.txt")])
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))
        
        with codecs.open(os.path.join(gram_dir, "G_new.txt"), "w", "utf-8") as fst_out_handle:
            with codecs.open(os.path.join(gram_dir, "G.txt"), "r", "utf-8") as fst_handle:
                for line in fst_handle:
                    line_parts = line.strip().split()
                    if len(line_parts) > 2:
                        new_line = " ".join([line_parts[0],line_parts[1],str(int_dict[int(line_parts[2])])])
                        if len(line_parts) > 3:
                            #new_line = " ".join([new_line," ".join(line_parts[3:])])
                            new_line = " ".join([new_line, line_parts[3]])
                        new_line = "".join([new_line,"\n"])
                    else:
                        new_line = line
                        
                    fst_out_handle.write(new_line)
        
        #cmd_string = " ".join(["fstcompile", "--acceptor", "--keep_isymbols=true", "--keep_osymbols=true", os.path.join(gram_dir,"G_new.txt"), os.path.join(gram_dir, "G_new.fst")])
        cmd_string = " ".join(["fstcompile", "--keep_isymbols=true", "--keep_osymbols=true", os.path.join(gram_dir,"G_new.txt"), os.path.join(gram_dir, "G_new.fst")])
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))
        
        cmd_string = " ".join(["fstarcsort", "--sort_type=ilabel", os.path.join(gram_dir, "G_new.fst"), ">", os.path.join(lang_dir, "G.fst")])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))

        cmd_string = " ".join(["fstisstochastic", os.path.join(lang_dir, "G.fst")])
        #os.system(cmd_string)
        print("going to run '{}'".format(cmd_string))
        proc = subprocess.Popen(cmd_string, shell=True,  stdout=subprocess.PIPE)
        proc.wait()
        result = proc.communicate()[0]
        print("result = {}".format(result))
        

    # gfst : OpenFST object
    # int_dict : keys are old labels (ints from old G.fst), values are new labels (ints compatible with L.fst)
    #            eg { 0: 0, 1: 34, 2: 2034 }
    def relabel_gfst(self, gfst,int_dict):
        # create new fst object
        f = fst_lib.Fst()
        # loop through states
        for s in gfst.states():
            # loop through outgoing arcs
            for a in gfst.arcs(s):
                # look up new label
                label = int_dict[a.ilabel]
                # add relabelled arc to new fst
                f.add_arc(s,fst_lib.Arc(label,label,fst_lib.Weight.One('tropical'),a.nextstate))
            # set final weight to one if applicable
            if gfst.final(s) == fst_lib.Weight.One('tropical'):
                f.set_final(s,0)
        # set start state
        f.set_start(gfst.start)
        return f
