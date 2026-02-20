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
A rule rewriting module, can be used for G2P, syllabification, etc...
"""

import logging


class RewriteRule(object):
    """
    A simple class to keep rules together.
    Rules are: LC [ A ] RC => B
    """

    def __init__(self, LC, A, RC, B, ordinal):
        """
        Initialize a rule with a left context, a grapheme,
        a right context and a phoneme.

        Args:
           LC (str): A list of graphemes that make up the left context of the
                      rule.
           A (str): The grapheme of the rule.
           RC (str): A list of graphemes that make up the right context of the
                      rule.
           B (str): The phoneme of the rule.
           ordinal (int): The rule number.
        """
        # fix LC
        if LC is not None:
            tmp = list()
            skip = False
            for i in range(0, len(LC)):
                if skip:
                    skip = False
                    continue
                if (i < len(LC) - 1) and ((LC[i + 1] == "*") or
                                          (LC[i + 1] == "+")):
                    tmp.append(LC[i + 1])
                    skip = True
                tmp.append(LC[i])
            tmp.reverse()
            self.LC = tmp
        else:
            self.LC = LC
        self.A = A
        self.RC = RC
        self.B = B
        self.ordinal = int(ordinal)

    def __str__(self):
        """
        Print in 'semicolon format'...
        """
        return ";".join([str(self.A),
                         str(self.LC),
                         str(self.RC),
                         str(self.B),
                         str(self.ordinal)])

    def get_right_hand_side(self):
        return self.B

    def context_match(self, pattern, string):
        """
        Returns True if this rule matches the given context.

        Args:
            pattern (str): The rule left or right context.
            string (str): The itape.

        Returns:
            (boolean): True if context is a match, otherwise False.
        """
        if len(pattern) == 0:
            # rule context is none, so match
            return True
        elif len(string) == 0:
            # rule context is not none and itape context is none
            return False
        elif len(pattern) > 1 and pattern[1] == "*":
            r = self.context_match(pattern[2:], string)
            tmp = pattern[2:]
            tmp.insert(0, pattern[0])
            s = self.context_match(tmp, string)
            t = pattern[0] == string[0] and \
                self.context_match(pattern, string[1:])
            return (r or s or t)
        elif len(pattern) > 1 and pattern[1] == "+":
            r = pattern[0] == string[0]
            tmp = pattern[2:]
            tmp.insert(0, "*")
            tmp.insert(0, pattern[0])
            s = self.context_match(tmp, string[1:])
            return (r and s)
        elif pattern[0] == string[0]:
            return self.context_match(pattern[1:], string[1:])
        else:
            return False

    def rule_matches(self, LC, RC):
        """
        Returns this rule if it matches the given context.

        Args:
            LC (list): The left context to match.
            RC (list): The right context to match.

        Returns:
            tuple(list, list)
        """

        # right context (actually A + RC) must be at least as long as rule's A
        if len(RC) < len(self.A):
            return None

        # check if [ A ] matches
        counter = 0
        for c1, c2 in zip(self.A, RC):
            if c1 != c2:
                return None
            counter += 1

        # Check LC: LC may have some limited regex stuff
        rLC = list(LC)
        rLC.reverse()
        if self.context_match(self.LC, rLC) and \
           self.context_match(self.RC, RC[counter:]):
            return RC[counter:]
        else:
            return None


class Rewrites(object):
    """
    Class to contain and implement the application of rewrite
    rules to predict pronunciations of isolated words.

    Ruleset is a dict of lists where the each list contains all
    RewriteRules associated with a specific grapheme.
    """

    def __init__(self):
        """
        Initialize the ruleset.
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self.ruleset = {}

    def add_rule(self, raw_rule):
        """
        Create a new rule from the given "raw_rule" and add it to the
        ruleset. The "raw_rule" is a list containing the grapheme, the
        left-context, the right-context, the phoneme and the rule_counter.

        Args:
            raw_rule (list): The list containing the rule definitions.
        """
        if not isinstance(raw_rule, list):
            raise RuntimeError("expected a list, got '{}'".
                               format(type(raw_rule)))

        if len(raw_rule) != 5:
            raise RuntimeError("expected a list of length 5, got length = {}".
                               format(len(raw_rule)))
        index = raw_rule[0]
        LC = raw_rule[1]
        A = raw_rule[0]
        RC = raw_rule[2]
        B = raw_rule[3]
        ordinal = raw_rule[4]
        rule = RewriteRule(LC, A, RC, B, ordinal)
        try:
            self.ruleset[index].append(rule)
        except KeyError:
            self.ruleset[index] = []
            self.ruleset[index].append(rule)

    def rewrite(self, itape, word):
        """
        Run rules on itape (LC A RC) to create rewrites otape (B)

        Args:
            itape (list): Input tape consisting of LC A RC
            word (str): Original word, for debugging purposes.

        Returns:
            (list): Output tape B, or in this case the list of
                    predicted phones.
        """

        LC = itape[0:1]
        RC = itape[1:]
        otape = list()

        #Debug
        #print word

        while len(RC) > 1:

            found_rule = False

            # search through rewrite rules to find matching one
            if RC[0] not in self.ruleset:
                logging.warning("ignoring unknown character '{}' in word "
                                "'{}'".format(RC[0], word.encode("utf-8")))
                RC.pop(0)
                continue

            for rule in self.ruleset[RC[0]]:
                newRC = rule.rule_matches(LC, RC)
                if newRC is not None:
                    logging.debug("found rule '{}' for grapheme '{}' of "
                                  "itape '{}'".format(rule.__str__(),
                                                      RC[0], itape))
                    found_rule = True
                    break

            if not found_rule:
                raise RuntimeError("Failed to find rewrite rule for itape "
                                   "sequence '{}'".format(str(itape)))

            otape += rule.get_right_hand_side()
            LC = LC + RC[0:len(RC) - len(newRC)]
            RC = newRC

        return otape
