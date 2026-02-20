# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c) 2018 Meraka Institute, CSIR, South Africa.                    #
#                                                                             #
# See the 'LICENSE' file in the project root folder for                       #
# licensing information.                                                      #
#                                                                             #
###############################################################################
#                                                                             #
# AUTHOR  : Aby Louw                                                          #
# DATE    : March 2018                                                        #
#                                                                             #
###############################################################################
"""
A G2P module, using rewrite rules.
"""

import re
import os
import codecs
import logging
from rewrites import Rewrites


class G2Prewrites(Rewrites):
    """
    Class to contain and implement the application of rewrite
    rules to predict pronunciations of isolated words.
    """

    WHITESPACE_CHAR = " "

    def __init__(self, rules_fn, gnulls_fn=None, graphs_fn=None,
                 phones_fn=None):
        """
        Load files and initialize rules.

        Args:
            rules_fn (str): Full path and file name to the rules file.
            gnulls_fn (str): Full path and file name to the gnulls
                             mapping file.
            graphs_fn (str): Full path and file name to the grapheme
                             mapping file.
            phones_fn (str): Full path and file name to the phoneset
                             mapping file.
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        super(G2Prewrites, self).__init__()

        if gnulls_fn is not None:
            self._load_gnulls(gnulls_fn)
        else:
            self.gnulls = None

        if graphs_fn is not None:
            self._load_graphs(graphs_fn)
        else:
            self.grapheme_map = None

        if phones_fn is not None:
            self._load_phones(phones_fn)
        else:
            self.phoneset_map = None

        self._load_rules(rules_fn)

    def __str__(self):
        """
        Returns:
            (str): A string representation of the rules.
        """
        rules = []
        for A in self.ruleset.keys():
            for rule in self.ruleset[A]:
                rules.append(str(rule))

        return str(rules)

    def _load_rules(self, rules_fn):
        """
        Load the ruleset file and convert it to rules.

        The format of the file is one rule per line, semicolon separated
        graphene;left-context;right-context;phoneme;rule_counter;numi
        for example:::

        F;dvari;teite;0;26;1


        Args:
            rules_fn (str): Full path and file name of the ruleset
                            mapping file.
        Note:
            We do not use the 'numi' variable, we can also load files that
            do not have the 'numi' variable.
        """
        if not os.path.exists(rules_fn):
            raise RuntimeError("the given path to the ruleset file '{}' does "
                               "not exist".format(rules_fn))

        with codecs.open(rules_fn, "rb", "utf-8") as fh:
            lines = [x.strip("\n").split(";") for x in
                     fh.readlines() if x != "\n"]

        for count, line in enumerate(lines):
            if (len(line) != 5) and (len(line) != 6):
                raise RuntimeError("format error in line {} of ruleset "
                                   "'{}': {}".
                                   format(count, rules_fn, line))
            self.add_rule(line[0:5])

        # make sure the rules are in the right order
        self._sort_all_rules()

    def _load_phones(self, phones_fn):
        """
        Load the phoneset file and convert it to a dictionary.

        The format of the file is one mapping per line, tab separated
        phoneme to mapping, for example:::

        H       A:r


        Args:
            phones_fn (str): Full path and file name of the phoneset
                             mapping file.
        """
        if not os.path.exists(phones_fn):
            raise RuntimeError("the given path to the phoneset mapping file "
                               "'{}' does not exist".format(phones_fn))

        with codecs.open(phones_fn, "rb", "utf-8") as fh:
            lines = [x.strip("\n").split("\t") for x in
                     fh.readlines() if x != "\n"]

        self.phoneset_map = {}
        for count, line in enumerate(lines):
            if len(line) != 2:
                raise RuntimeError("format error in line {} of phoneset "
                                   "mapping file '{}': {}".
                                   format(count, phones_fn, line))
            self.phoneset_map[line[0]] = line[1]

    def _load_graphs(self, graphs_fn):
        """
        Load the "graphs"/graphemes file and convert it to a dictionary.

        The format of the file is one mapping per line, tab separated
        grapheme to mapping, for example:::

        ä       B


        Args:
            graphs_fn (str): Full path and file name of the graphemes
                             mapping file.
        """
        if not os.path.exists(graphs_fn):
            raise RuntimeError("the given path to the grapheme mapping file "
                               "'{}' does not exist".format(graphs_fn))

        with codecs.open(graphs_fn, "rb", "utf-8") as fh:
            lines = [x.strip("\n").split("\t") for x in
                     fh.readlines() if x != "\n"]

        self.grapheme_map = {}
        for count, line in enumerate(lines):
            if len(line) != 2:
                raise RuntimeError("format error in line {} of grapheme "
                                   "mapping file '{}': {}".
                                   format(count, graphs_fn, line))
            self.grapheme_map[line[0]] = line[1]

    def _load_gnulls(self, gnulls_fn):
        """
        Load the "gnulls" file and convert it to a dictionary.

        The format of the file is one gnull per line, semicolon separated
        grapheme group to gnull mapping, for example:::

        du;d0u


        Args:
            gnulls_fn (str): Full path and file name of the gnulls file.
        """
        if not os.path.exists(gnulls_fn):
            raise RuntimeError("the given path to the gnulls file "
                               "'{}' does not exist".format(gnulls_fn))

        with codecs.open(gnulls_fn, "rb", "utf-8") as fh:
            lines = [x.strip("\n").split(";") for x in
                     fh.readlines() if x != "\n"]

        self.gnulls = {}
        for count, line in enumerate(lines):
            if len(line) != 2:
                raise RuntimeError("format error in line {} of gnulls file "
                                   "'{}': {}".format(count, gnulls_fn, line))
            self.gnulls[line[0]] = line[1]

    def _sort_all_rules(self):
        """
        Make sure that all rulelists associated with each grapheme
        are sorted in the correct order for application (i.e. from
        most specific context to least specific context - based on the
        RewriteRule.ordinal)
        """
        for g in self.ruleset:
            self.ruleset[g].sort(key=lambda x: x.ordinal, reverse=True)

    def _apply_gnulls(self, word):
        """
        Apply gnulls to word if applicable.

        Args:
            word (str): The word for which to apply the `gnulls`.

        Returns:
            (str): Word with `gnulls` replaced.
        """

        if self.gnulls:
            for gnull in self.gnulls:
                word = re.sub(gnull, self.gnulls[gnull], word)

        return word

    def apply(self, word):
        """
        Predict phone sequence given word.

        Args:
            word (str): The word on which to apply G2P transformation.

        Returns:
            (list): A list of phonemes.
        """

        # first map word if there is a grapheme map
        gword = u""
        if self.grapheme_map:
            for l in word:
                if l in self.grapheme_map:
                    gword += self.grapheme_map[l]
                else:
                    gword += l
                logging.debug("grapheme mapped '{}' -> '{}'".
                              format(word.encode("utf-8"),
                                     gword.encode("utf-8")))
        else:
            gword = word
            logging.debug("no grapheme map")

        phones = []

        # append and prepend whitespace_char
        gword = gword.join([self.WHITESPACE_CHAR, self.WHITESPACE_CHAR])

        # apply gnulls
        gword = self._apply_gnulls(gword)

        # find matching rule and thus phoneme for each grapheme.
        tmp = self.rewrite(list(gword), word)

        # remove empty ("") phones
        for i in tmp:
            if i != "" and i != "0":
                if self.phoneset_map:
                    if i in self.phoneset_map:
                        phones.append(self.phoneset_map[i])
                    else:
                        phones.append(i)
                else:
                    phones.append(i)

        return phones
