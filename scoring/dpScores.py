#cython: language_level=3

#--------------------------------------------------------------------------
# Author: Marelie Davel, marelie.davel@gmail.com
# Translated to Python3 by Rynhardt Kruger, rkruger@csir.co.za
#--------------------------------------------------------------------------


import sys, re
import logging

debug = 1
display_width = 15
HTK_NORMALIZATION = 10000000
MARGIN_FACTOR = 1

#spn = 'SPN'
spn = 'spn'
SIL_NAMES = {'SIL-ENCE': 1, '<s>': 1, '</s>': 1, 'TRUE_SP': 1, spn: 1}
IGNORE_IDS = {'sp': 1, 'sil': 1, '<s>': 1, '</s>': 1, 'nse': 1}

COLLAPSE_REPEATED_REF = 1     # Default. Set to 0 if repeated phonemes phonemic in language.
COLLAPSE_REPEATED_OBS = 1
IGNORE_INTRAWORD_SIL = 1
RESOLVE_WORD_BOUNDARIES = 0
NORM_WORD = 1
best_ref_scores = {}


#--------------------------------------------------------------------------
# INPUT FUNCTIONS
#--------------------------------------------------------------------------

def read_matrix(matrix_fname, matrix):
    matrix_f = open(matrix_fname)
    heading = matrix_f.readline()
    phones = heading.split()
    num = int(phones[0])
    phones = phones[1:]
    if num != len(phones):
        print("Error! Expected %d phones, but found %d"%(num, len(phones)), file=sys.stderr)
        sys.exit(1)
    for line in matrix_f:
        parts = line.split()
        ref = parts[0]
        parts = parts[1:]
        if len(parts)!=len(phones):
            print("Error! Expected %d phones, but found %d", len(phones), len(parts))
            sys.exit(1)
        for obs in range(0, len(phones)):
            if not ref in matrix:
                matrix[ref]={}
            matrix[ref][phones[obs]]=float(parts[obs])
    #print(matrix)


def create_default_matrix(phones):
    smat = {}
    if not "-" in phones:
        phones.append("-")
    for ref in phones:
        for obs in phones:
            if not ref in smat:
                smat[ref]={}
            if ref=="-" or obs=="-":
                smat[ref][obs]=-0.5
            elif ref==obs:
                smat[ref][obs]=1
            else:
                smat[ref][obs]=-1.0
    return smat

def read_dict(dict_fname, dict_p):
    with open(dict_fname) as dict_f:
        for line in dict_f:
            parts = line.split()
            if len(parts)!=2:
                print("Error in dictionary!", file=sys.stderr)
                sys.exit(1)
            word, pron = parts
            if not word in dict_p:
                dict_p[word]= []
            pron.replace("sil", "sp")
            dict_p[word].append(pron)

def read_basic(lab_fname, use_sil, lab_p):
    with open(lab_fname) as lab_f:
        for line in lab_f:
            parts = line.split()
            if len(parts)<2:
                print("Wrong format %s", line, file=sys.stderr)
            else:
                for i in range(len(parts)):
                    match = re.match(r'^.*\-(.*)\+.*$', parts[i])
                    if match:
                        parts[i] = match.group(1)
                name = parts[0]
                lab_p[name]=parts[1:]


def read_timed_basic(lab_fname, use_sil, lab_p):
      # Create structure @{$lab_p->{'name'}{<label>}} = @list
    # where <label> is 's' | 'e' | 'i' | 'l' for start, end, id and likelihood values
    if debug:
        print(f"Reading {lab_fname}")
    with open(lab_fname) as lab_f:
        name = ""
        for line in lab_f:
            line = line.strip()
            match = re.search(r"^ID\s+(.*)$", line)
            if match:
                name = match.group(1)
                lab_p[name]= {}
                lab_p[name]['s'] = []
                lab_p[name]['e'] = []
                lab_p[name]['i'] = []
                lab_p[name]['l'] = []
            else:
                parts = line.split()
                if len(parts) < 3:
                    print(f"Error: this line only contained {line}")
                else:
                    start,dur,id,*rest = parts;
                    if id in IGNORE_IDS:
                        id = 'sil'
                    if ((not id in IGNORE_IDS) or (use_sil==1 and float(dur)>0)):
                        lab_p[name]['s'].append(float(start))
                        lab_p[name]['e'].append(float(start)+float(dur))
                        lab_p[name]['i'].append(id)
                        lab_p[name]['l'].append(0)      # temporary while ll not used


def read_mlf(mlf_fname, mlf_p):
    read_mlf_sil(mlf_fname, 0, mlf_p)

def read_mlf_file(mlf_file, mlf_p):
    read_mlf_sil_file(mlf_file, 0, mlf_p)

def read_mlf_sil(mlf_fname, use_sil, mlf_p):
    with open(mlf_fname) as mlf_f:
        read_mlf_sil_file(mlf_f, use_sil, mlf_p)

def read_mlf_sil_file(mlf_f, use_sil, mlf_p):
    name = ""
    for line in mlf_f.read().strip().split('\n'):
        line = line.strip()
        if 'MLF' in line:
            continue
        match = re.search(r"([^/]+)\.((lab)|(rec))", line)
        if match:
            name = match.group(1)
            mlf_p[name] = []
        elif line == ".":
            name = ""
        else:
            parts = line.split()

            logging.debug(f"Reading parts {parts}")
            id, start, end = "", 0.0, 0.0
            timing_info = 0
            if len(parts)==1:
                id = parts[0]
            elif len(parts)>=3:
                timing_info = 1
                start, end, id = float(parts[0]), float(parts[1]), parts[2]
            else:
                print ("Error: currently assuming decoded MLF contains either ID only or", file=sys.stderr)
                print("at least start time, end time and ID", file=sys.stderr)
                print (f"This line {name} contained [{line}]", file=sys.stderr)
                exit(1)
            match = re.match(r"^.*\-(.*)\+.*$", id)
            if match:
                id = match.group(1)
            if not id in IGNORE_IDS:
                if not name in mlf_p:
                    mlf_p[name]=[]
                mlf_p[name].append(id)
            elif ( ((timing_info==1) and (use_sil>0) and (end-start>0.0)) or
                    ((timing_info==0) and (use_sil>0)) ):
                # Only keep non-empty sil
                if use_sil == 2:
                    if len(parts) < 5:
                        print (f"Error: silence marker expected at line {line}", file=sys.stderr)
                    if spn in parts[4]:
                        mlf_p[name].append(spn)
                else:
                    mlf_p[name].append('sil')


def read_timed_mlf(mlf_fname, use_sil, mlf_p):
    # Create structure @{$mlf_p->{'name'}{<label>}} = @list
    # where <label> is 's' | 'e' | 'i' | 'l' for start, end, id and likelihood values
    if debug==1:
        print(f"Reading {mlf_fname}")
    with open(mlf_fname) as mlf_f:
        name = ""
        for line in mlf_f:
            line = line.strip()
            if line.startswith(".") or "MLF" in line:
                continue
            match = re.search(r"([^/]+)\.((lab)|(rec))", line)
            if match:
                name = match.group(1)
                mlf_p[name]= {}
                mlf_p[name]['s'] = []
                mlf_p[name]['e'] = []
                mlf_p[name]['i'] = []
                mlf_p[name]['l'] = []
                mlf_p[name]['w'] = {}
            else:
                parts = line.split()
                if len(parts) < 4:
                    print(f"Error, this line only contained {line}", file=sys.stderr)
                    exit(1)
                elif len(parts) >=4:
                    start, end, id, *ll = float(parts[0]), float(parts[1]), parts[2], parts[3]
                    if id in IGNORE_IDS:
                        id = 'sil'
                    if id not in IGNORE_IDS or (use_sil==1 and end>start):
                        mlf_p[name]['s'].append(start)
                        mlf_p[name]['e'].append(end)
                        mlf_p[name]['i'].append(id)
                        mlf_p[name]['l'].append(ll)
                    if len(parts)==5:
                        if (use_sil==1) or (not (parts[4] in SIL_NAMES)):
                            i = len(mlf_p[name]['s'])-1
                            mlf_p[name]['w'][i] = parts[4]
                else:
                    print(f"Warning: line {line} in MLF {mlf_fname} ignored.", file=sys.stderr)



def read_set(set_fname, set_p):
    with open (set_fname) as set_f:
        for line in set_f:
            line = line.strip()
            set_p[line] = 1

# only version for untimed MLF implemented

def mlf_to_phones(mlf_p, phones_p):
    for name in mlf_p.keys():
        pstr = mlf_p[name]
        for p in pstr:
            phones_p[p] = 1


#--------------------------------------------------------------------------
# SCORING HELPER FUNCTIONS
#--------------------------------------------------------------------------

def get_adjusted(str_p, _from, _to):
    """ Find and return adjusted index of $from and $to after '-' symbols have been added """
    i_adj = []
    i_adj.append(0)
    for i in range(0, _to+1):
        while str_p[i_adj[i]] == '-':
            i_adj[i]+=1
        i_adj.insert(i+1,i_adj[i]+1)
    return i_adj[_from], i_adj[_to]


def get_readjusted(str_p, _from, _to):
    """ Find and return adjusted index of $from and $to after '-' symbols have been removed 
    i_adj contains the original index of the symbol originally now at index i (post alignment) """
    i_adj = []
    match = -1
    i = 0
    while i <= _to:
        while str_p[i] == '-':
            i_adj[i] = match
            i+=1
        match+=1
        i_adj[i] = match
        i+=1
    while str_p[_from] == '-':
        _from+=1
    return i_adj[_from], i_adj[_to]


def ignore_intraword_sil(aligned_p, decoded_p):
    to_delete = []
    for i in range(0, len(decoded_p)):
        if len(aligned_p) <=i:
            break
        if (decoded_p[i] == 'sil') and (aligned_p[i] == '-'):
            to_delete.append(i)
        elif (decoded_p[i] == '-') and (aligned_p[i] == 'sil'):
            to_delete.append(i)
    i = len(to_delete)-1
    while i >=0:
        del aligned_p[to_delete[i]]
        del decoded_p[to_delete[i]]
        i-=1


def collapse_repeated_phones(aligned_p, decoded_p):
    # Assumes no '-' to '-' alignments left pre collapsing
    to_delete = []
    for i in range(0, len(decoded_p)-1):
        if (i+1) >=len(aligned_p):
            break
        if (COLLAPSE_REPEATED_OBS == 1) and (decoded_p[i] == decoded_p[i+1]):
            if aligned_p[i] == '-':
                to_delete.append(i)
            elif aligned_p[i+1] == '-':
                to_delete.append(i+1)
            # else keep repeated phone
        if (COLLAPSE_REPEATED_REF == 1) and (aligned_p[i] == aligned_p[i+1]):
            if decoded_p[i] == '-':
                to_delete.append(i)
            elif decoded_p[i+1] == '-':
                to_delete.append(i+1)
            # else keep repeated phone
    i = len(to_delete)-1
    while i >= 0:
        del aligned_p[to_delete[i]]
        del decoded_p[to_delete[i]]
        i-=1


def init_ref_scores(smat_p):
    global best_ref_scores
    best_ref_scores = {}
    for r in smat_p.keys():
        if r == '-':
            continue
        max = -1000
        for o in smat_p[r].keys():
            if smat_p[r][o] > max:
                max = smat_p[r][o]
        best_ref_scores[r] = max


def get_perfect_score(pron_p):
    best = 0
    cnt = 0
    for ri in range(0, len(pron_p)):
        r = pron_p[ri]
        if r == '-':
            continue
        if not r in best_ref_scores:
            print(best_ref_scores, file=sys.stderr)
            print (f"Trying to access best_ref_scores{r} which doesn't exist!", file=sys.stderr)
            exit(1)
        best += best_ref_scores[r]
        cnt+=1
    if cnt==0:
        print ("WARNING: valid count for [pron_p] is 0!")
        return 0
    return best/cnt



#--------------------------------------------------------------------------
# ALIGNMENT FUNCTIONS
#--------------------------------------------------------------------------

def pad_strings(in_p, out_p):
    out_p.extend(in_p)
    out_p.append('-')
    out_p.insert(0, '-')
    return len(out_p)



def align_strings(ref_p, obs_p, smat_p, ref_out_p, obs_out_p):
    # Get limits
    ref, obs = [], []
    num_ref = pad_strings(ref_p,ref)
    num_obs = pad_strings(obs_p,obs)

    #Populate value matrix
    # (Visualise as rectangle with observed string left to right
    # and reference string top to bottom. Find best path from top left
    # to bottom right.)

    val = {}
    btrack = {}
    val[0]= {}
    btrack[0] = {}
    val[0][0] = 0
    for r in range(1, num_ref):
        val[r] = {}
        btrack[r] = {}
        if not '-' in smat_p[ref[r]]:
            print ("ERROR: problem aligning %s to %s", ' '.join(ref), ' '.join(obs))
            sys.exit(1)
        val[r][0] = val[r-1][0] + smat_p[ref[r]]['-']
        btrack[r][0] = "%d:0"%(r-1)
    for o in range(1, num_obs):
        if not obs[o] in smat_p['-']:
            print (f"Unknown score requested '-' to {obs[o]}, {obs}")
            sys.exit(1)
        val[0][o] = val[0][o-1] + smat_p['-'][obs[o]]
        btrack[0][o] = "0:%d"%(o-1)
    for r in range(1, num_ref):
        for o in range(1, num_obs):
            if not obs[o] in smat_p[ref[r]]:
                print ("ERROR: problem aligning %s to %s", ' '.join(ref), ' '.join(obs))
                sys.exit(1)
            #assume SPN only in aligned (reference) string for now
            left = val[r][o-1] + smat_p['-'][obs[o]]
            if spn in ref[r]:
                left = val[r][o-1] + smat_p[spn][obs[o]]
            diag = val[r-1][o-1] + smat_p[ref[r]][obs[o]]
            top = val[r-1][o] + smat_p[ref[r]]['-']
            # Only keep a single path if tied
            best = diag
            btrack[r][o] = "%d:%d"%((r-1),(o-1))
            if left > best:
                btrack[r][o] = "%d:%d"%(r,(o-1))
                best = left
            if top > best:
                btrack[r][o] = "%d:%d"%((r-1),o)
                best = top
            val[r][o] = best
    ref_path = []
    obs_path = []
    oi = num_obs-1
    ri = num_ref-1
    while (ri>0) or (oi>0):
        ref_path.insert(0, ri)
        obs_path.insert(0, oi)
        (ri_s,oi_s) = btrack[ri][oi].split(":")
        ri=int(ri_s)
        oi=int(oi_s)


    
    # Create aligned strings
    ref_out_p.insert(0, ref[ref_path[0]])
    for i in range(1, len(ref_path)):
        while not i < len(ref_out_p):
            ref_out_p.append('-')
        if (ref_path[i] == ref_path[i-1]):
            if (spn in ref_out_p[i-1]):
                ref_out_p[i] = spn
            else:
                ref_out_p[i] = '-'
        else:
            ref_out_p[i] = ref[ref_path[i]]
    
    score = val[num_ref-1][num_obs-1]
    # TODO: fix 0-anchor within DP code later
    # automatically only applicable if $use_sil == 2
    if len(ref_out_p) >= 2 and ((ref_out_p[0] == '-') and (ref_out_p[1] == spn)):
        ref_out_p[0] = spn
        score = score + smat_p[spn][obs_out_p[0]] - smat_p['-'][obs_out_p[0]]
    
    obs_out_p.insert(0, obs[obs_path[0]])
    for i in range(1, len(obs_path)):
        while not i < len(obs_out_p):
            obs_out_p.append('-')
        if (obs_path[i] == obs_path[i-1]):
            obs_out_p[i] = '-'
        else:
            obs_out_p[i] = obs[obs_path[i]]
    
    i = len(obs_path)-1
    while i >= 0:
        if ((obs_out_p[i] == '-') and (ref_out_p[i] == '-')):
            del obs_out_p[i]
            del ref_out_p[i]
            score = score - smat_p['-']['-']
        i-=1
    
    # Return score
    num = len(ref_out_p)-1
    if num==0:
        print("WARNING: 0 score returned")
        return 0
    else:
        if (NORM_WORD == 1):
            best = get_perfect_score(ref_out_p)
            score = score - best
        score = (score/num)
        return score



def align_and_score(in1_p,in2_p,smat_p):
    out1=[]
    out2=[]
    dps = align_strings(in1_p,in2_p,smat_p,out1,out2)
    return dps

def get_aligned_score_ignore_spn(pron_p, decode_p, smat_p, skip_spn):
    score = 0
    num_spn = 0
    for i in range(0, len(pron_p)):
        r = pron_p[i]
        o = decode_p[i]
        cost = smat_p[r][o]
        if ((skip_spn==1) and ((spn in r) or (spn in o))):
            num_spn+=1
        else:
            score += cost
    
    num = len(pron_p) - num_spn
    if num==0:
        print("WARNING: 0 score returned")
        return 0
    else:
        score = (score/num)
        if NORM_WORD == 1:
            best = get_perfect_score(pron_p)
            score = score-best
        return score



def get_aligned_score(pron_p, decode_p, smat_p):
    return get_aligned_score_ignore_spn(pron_p, decode_p, smat_p,0)


#--------------------------------------------------------------------------
# DISPLAY HELPER FUNCTIONS
#--------------------------------------------------------------------------

def  get_phn_str(mlf_p,name,array_p):
    array_p = mlf_p[name]['i']
    return len(array_p)


def display_aligned(list1_p,list2_p):
    list1 = list1_p
    list2=list2_p
    num_lines = int((len(list1)-1) / display_width)
    remainder = (len(list1)-1) % display_width
    _to=0
    for l in range(0, num_lines)+1:
        _from = l*display_width
        if l == num_lines:
            _to = _from + remainder
        else:
            _to = (l+1)*display_width - 1
        display1 = list1[_from:_to]
        display1.insert(0, "r]") #Reference transcription
        display2 = list2[_from:_to]
        display2.insert(0, "d]")        #Decoded transcription)
        display_diff = []
        for d in range(0, len(display1)):
            if display1[d] == display2[d]:
                display_diff[d] = " "
            else:
                display_diff[d] = "|"
        print ("%s\n"%("\t".join(display1)))
        print ("%s\n"%("\t".join(display_diff)))
        print ("%s\n"%("\t".join(display2)))


def  write_score(word,name,score,start,end,pron_p,decode_p,out,out_r):
    plen = len(pron_p)
    dlen = len(decode_p)
    _len = dlen
    if plen>dlen:
        _len= plen
    out.write("%s\t%s\t%d\t%d\t%d\t%.3f\t[%s]\t[%s]\n"%(word, name, start, end, plen, score, ' '.join(pron_p), ' '.join(decode_p)))
    out_r.write("%-20s\t%-18s %9d %9d %2d %.3f aligned: "%(word, name, start, end, plen, score))
    for p in pron_p:
        out_r.write("%-4s "%(p))
    out_r.write("\n")
    out_r.write("%-20s\t%-18s %9d %9d %2d %.3f decoded: "%(word, name, start, end, dlen, score))
    for p in decode_p:
        out_r.write("%-4s "%(p))
    out_r.write("\n")


def resolve_word_boundaries(pron_p, decode_p, utt_pron_p, utt_decode_p, start, end):
    orig = ' '.join(decode_p)
    if start > 0:
        start_decode = utt_decode_p[start]
        start_pron = utt_pron_p[start]
        prev_pron = utt_pron_p[start-1]
        prev_decode = utt_decode_p[start-1]
        if (start_decode == '-') and (prev_pron == start_pron) and (prev_decode == prev_pron):
            decode_p[0] = prev_pron
            print ("INFO: adjusted [%s] to [%s] in [%s]"%(orig, ' '.join(decode_p), ' '.join(utt_decode_p)))
    
    if end <len(utt_pron_p)-1:
        end_decode = utt_decode_p[end]
        end_pron = utt_pron_p[end]
        next_pron = utt_pron_p[end+1]
        next_decode = utt_decode_p[end+1]
        if (end_decode == '-') and (end_pron == next_pron) and (next_decode == next_pron):
            decode_p.append(end_pron)
            print("INFO: adjusted [%s] to [%s] in [%s]"%(orig, ' '.join(decode_p), ' '.join(utt_decode_p)))



def display_score_per_word(name,pron_p,decode_p,index_p,start_p,end_p,smat_p,n_pron,out,out_r):
    utt_pron = pron_p
    utt_decode = decode_p
    cuts = list(index_p.keys())
    cuts.sort()
    prev_adj_to = 0
    prev_start = 0
    prev_end = 0
    for i in range(0, len(cuts)):
        _from = cuts[i]
        _to = _from
        if i == len(cuts)-1:
            _to = n_pron
        else:
            _to = cuts[i+1]-1
        (adj_from,adj_to) = get_adjusted(utt_pron,_from,_to)
        if adj_from > prev_adj_to+1:
            ins_pron = utt_pron[prev_adj_to+1:adj_from-1]
            ins_decode = utt_decode[prev_adj_to+1:adj_from-1]
            ins_score = get_aligned_score(ins_pron,ins_decode,smat_p)
            write_score('<ins>',name,ins_score,prev_end,prev_end,ins_pron,ins_decode,out,out_r)
        pron = utt_pron[adj_from:adj_to+1] # fix off by one error
        decode = utt_decode[adj_from:adj_to+1]
        if (COLLAPSE_REPEATED_OBS == 1) or (COLLAPSE_REPEATED_REF == 1):
            collapse_repeated_phones(pron,decode)
        if IGNORE_INTRAWORD_SIL == 1:
            ignore_intraword_sil(pron,decode)
        if RESOLVE_WORD_BOUNDARIES == 1:
            resolve_word_boundaries(pron, decode, utt_pron, utt_decode, adj_from, adj_to)
        score = get_aligned_score(pron,decode,smat_p)

        # Check if all required variables set
        if not _from in index_p:
            print(f"Error: unknown word at {_from}")
        word = index_p[_from]
        if not _from in start_p:
            print(f"Error: unknown start time at {_from} (for word \'{word}\')")
        if not _from in end_p:
            print(f"Error: unknown end time at {_from} (for word \'{word}\')")
        # write score for current word
        start = start_p[_from]
        end = end_p[_from]
        write_score(word,name,score,start,end,pron,decode,out,out_r)
        prev_adj_to = adj_to
        prev_end = end
    # also write out any dangling insertions
    if prev_adj_to < len(utt_decode)-1:
        #print "DBG: Adding dangling <ins>\n";
        ins_pron = utt_pron[prev_adj_to+1:len(utt_decode)]
        ins_decode = utt_decode[prev_adj_to+1:len(utt_decode)]
        ins_score = get_aligned_score(ins_pron,ins_decode,smat_p)
        write_score('<ins>',name,ins_score,prev_end,prev_end,ins_pron,ins_decode,out,out_r)



def display_score_per_word_decoded_times(name,pron_p,decode_p,index_p,mlf_p,smat_p,n_pron,out,out_r):
    utt_pron = pron_p
    utt_decode =decode_p
    cuts = list(index_p.keys())
    cuts.sort()
    prev_adj_to = 0
    prev_start = 0
    prev_end = 0
    for i in range(0, len(cuts)):
        _from = cuts[i]
        _to = _from
        if i == len(cuts)-1:
            _to = n_pron
        else:
            _to = cuts[i+1]-1

        # Adjust original indices for insertions/deletions during alignment
        (adj_from,adj_to) = get_adjusted(utt_pron,_from,_to)
        (re_from,re_to) = get_readjusted(utt_decode,adj_from,adj_to)

        # If a dangling insertion found, write score
        if (adj_from > prev_adj_to+1):
            (ins_from,ins_to) = get_readjusted(utt_decode,prev_adj_to+1,adj_from-1)
            ins_pron = utt_pron[prev_adj_to+1:adj_from]
            ins_decode = utt_decode[prev_adj_to+1:adj_from]
            ins_score = get_aligned_score(ins_pron,ins_decode,smat_p)
            ins_start = mlf_p['s'][ins_from]
            ins_end = mlf_p['e'][ins_to]
            write_score('<ins>',name,ins_score,ins_start,ins_end,ins_pron,ins_decode,out,out_r)

        # Obtain strings and score associated with current word
        pron = utt_pron[adj_from:adj_to+1]
        decode = utt_decode[adj_from:adj_to+1]

        # Now clean phone strings
        if (COLLAPSE_REPEATED_OBS == 1) or (COLLAPSE_REPEATED_REF == 1):
            collapse_repeated_phones(pron,decode)
        if (IGNORE_INTRAWORD_SIL == 1):
            ignore_intraword_sil(pron,decode)
        if (RESOLVE_WORD_BOUNDARIES == 1 ):
            resolve_word_boundaries(pron, decode, utt_pron, utt_decode, adj_from, adj_to)

        # Score on word level 
        if not _from in index_p:
            print(f"Error: unknown word at {_from}")
        word = index_p[_from]
        score = get_aligned_score(pron,decode,smat_p)

        # Get timing from original decoded MLF
        start = mlf_p['s'][re_from]
        end = mlf_p['e'][re_to]

        # Write to file
        write_score(word,name,score,start,end,pron,decode,out,out_r)

        # and update end index and end time
        prev_adj_to = adj_to
        prev_end = end
    
    # Write out any dangling insertions at end
    if prev_adj_to < len(utt_decode)-1:
        #print "DBG: Adding dangling <ins> at $name\n";
        ins_pron = utt_pron[prev_adj_to+1:len(utt_decode)]
        ins_decode = utt_decode[prev_adj_to+1:len(utt_decode)]
        ins_score = get_aligned_score(ins_pron,ins_decode,smat_p)
        (ins_from,ins_to) = get_readjusted(utt_decode,prev_adj_to+1,len(utt_decode)-1)
        ins_start = mlf_p['s'][ins_from]
        ins_end = mlf_p['e'][ins_to]
        write_score('<ins>',name,ins_score,prev_end,prev_end,ins_pron,ins_decode,out,out_r)
        # Before ending off with last <sil> (always present)
        last_pron = ['sil']
        last_score = smat_p['sil']['sil'] 
        (last_from,last_to) = get_readjusted(utt_decode,len(utt_decode)-1,len(utt_decode)-1)
        last_start = mlf_p['s'][last_from]
        last_end = mlf_p['e'][last_to]
        write_score('<sil>',name,last_score,last_start,last_end,last_pron,last_pron,out,out_r)




def add_spn(smat_p, id, val):
    if not id in smat_p:
        smat_p[id]={}
    for r in smat_p.keys():
        smat_p[r][id] = val
        for o in smat_p[r].keys():
            smat_p[id][o] = val


#--------------------------------------------------------------------------
# MAIN FUNCTIONS
#--------------------------------------------------------------------------

def calc_word_dp_scores_from_mlfs(aligned_mlf_name, decode_mlf_name, smat_name, use_sil, out_name):
    _in = None
    out = None
    decode_mlf_f = None
    try:
        _in = open(aligned_mlf_name)
    except:
        print(f"Error opening {aligned_mlf_name}", file=sys.stderr)
        return
    try:
        out = open(out_name, 'w')
    except:
        print(f"Error opening {out_name}", file=sys.stderr)
        return
    try:
        decode_mlf_f = open(decode_mlf_name)
    except:
        print(f"Error opening {decode_mlf_name}", file=sys.stderr)
        return
    read_matrix(smat_name, smat)
    calc_word_dp_scores_from_mlfsm_buffers(_in, decode_mlf_f, smat, use_sil, out)
    _in.close()
    out.close()

def calc_word_dp_scores_from_mlfs_buffers(_in, decode_mlf_f, smat, use_sil, out, out_name="/tmp/out.readable"):
    decoded = {}
    init_ref_scores(smat)
    if use_sil==2:
        read_mlf_sil_file(decode_mlf_f, 0, decoded)
        add_spn(smat,spn,0)
    else:
        read_mlf_sil_file(decode_mlf_f, use_sil, decoded)
    out_r = None
    try:
        out_r = open(out_name+".readable",'w')
    except:
        print(f"Cannot open file {out_name}.readable")
        sys.exit(1)

    name = ""
    pron_str = []
    decode_str = []
    word_index = {}
    end_index = {}
    start_index = {}
    prev_i=0

    for line in _in:
        line = line.strip()
        if 'MLF' in line:
            continue
        #Edit to suit specific label format
        match = re.search(r"([^/]+)\.((lab)|(rec))", line)
        if match:
            name = match.group(1)
        elif line == '.':
            if not name in decoded:
                print (f"WARNING: {name} skipped")
            else:
                decode_str = decoded[name]
                aligned_pron = []
                aligned_decode = []
                # First align strings globally (across words)
                align_strings(pron_str, decode_str, smat, aligned_pron, aligned_decode)
                #printf "DBG: aligned=%s\ndecode=%s\n", (join ' ',@pron_str), (join ' ',@decode_str);
                #printf "DBG: aligned=%s\ndecode=%s\n", (join ' ',@aligned_pron), (join ' ',@aligned_decode);
                # Now extract and score strings on a per-word basis
                display_score_per_word(name, aligned_pron, aligned_decode, word_index, start_index, end_index, smat, len(pron_str)-1, out, out_r)
            #Clean vars for next round
            name = ""
            pron_str = []
            word_index = {}
            start_index = {}
            end_index = {}
            prev_i = 0
        else:
            parts = line.split()
            #print "Adding @parts\n";
            if len(parts)<3:
                print ("Error: assuming aligned MLF contains at least start,end and phone id")
                print (f"This line ({name}) contained only [{line}]")
                sys.exit(1)
            (start,end,id) = (float(parts[0]),float(parts[1]),parts[2])
            match = re.match(r"^.*\-(.*)\+.*$", id)
            if match:
                id = match.group(1)
            
            # RPK: continuously update end_index, to account for end of sequence
            end_index[len(pron_str)] = end
            #If start of new word, record position
            if len(parts)== 5:
                word = parts[4]
                current_i = len(pron_str)
                if current_i > 0:
                    end_index[prev_i] = start
                if word in SIL_NAMES:
                    end_index[current_i] = end
                if id in IGNORE_IDS:
                    word = "<sil>"
                if (use_sil>0) or (id not in IGNORE_IDS):
                    start_index[current_i] = start
                    prev_i = current_i
                    word_index[current_i] = word
            if id not in IGNORE_IDS:
                pron_str.append(id)
            elif (use_sil==1) and (end-start)>0:
                pron_str.append('sil')
            elif ((use_sil==2) and (spn in word_index[prev_i] )):
                pron_str.append(spn)
    _in.close()
    out.close()
    out_r.close()



def calc_word_dp_scores_from_mlfs_decoded_times(aligned_mlf_name, decode_mlf_name, smat_name, use_sil, out_name):
    if use_sil == 2:
        print("Error: SPN not yet implemented in _decoded_times")
        sys.exit(1)
    decoded = {}
    smat = {}
    read_timed_mlf(decode_mlf_name,use_sil,decoded)
    read_matrix(smat_name,smat)
    init_ref_scores(smat)
    _in = None
    out = None
    out_r = None
    try:
        _in = open(aligned_mlf_name)
    except:
        print(f"Cannot open file {aligned_mlf_name}")
        sys.exit(1)
    try:
        out = open(out_name, 'w')
    except:
        print(f"Cannot open file {out_name}")
        sys.exit(1)
    try:
        out_r = open(out_name+".readable",'w')
    except:
        print(f"Cannot open file {out_name}.readable")
        sys.exit(1)
    name = ""
    pron_str = []
    decode_str = []
    word_index = {}
    end_index = {}
    start_index = {}
    prev_i=0
    for line in _in:
        line = line.strip()
        if 'MLF' in line: #strip MLF markers, may be multiple in file
            continue
        #Edit to suit specific label format
        match = re.search(r"([^/]+)\.((lab)|(rec))", line)
        if match:
            name = match.group(1)
        elif line == '.':
            if not name in decoded:
                print (f"WARNING: {name} skipped")
            else:
                # first make sure starting point is 0
                if decoded[name]['s'][0] != 0:
                    new_end = decoded[name]['s'][0]
                    decoded[name]['s'].insert(0, 0)
                    decoded[name]['e'].insert(0, new_end)
                    decoded[name]['i'].insert(0, 'sil')
                    decoded[name]['l'].insert(0, -100)                
                get_phn_str(decoded,name,decode_str)
                aligned_pron=[]
                aligned_decode=[]
                # First align strings globally (across words)
                align_strings(pron_str, decode_str, smat, aligned_pron, aligned_decode)
                # Now extract and score strings on a per-word basis
                display_score_per_word_decoded_times(name, aligned_pron, aligned_decode, word_index, decoded[name], smat, len(pron_str)-1, out, out_r)
            #Clean vars for next round
            name = ""
            pron_str = []
            word_index = {}
            start_index = {}
            end_index = {}
            prev_i = 0
        else:
            parts = line.split()
            if len(parts) < 3:
                print ("Error: assuming aligned MLF contains at least start,end and phone id")
                print(f"This line ({name}) contained only [{line}]")
                sys.exit(1)
            (start,end,id) = (float(parts[0]),float(parts[1]),parts[2])
            match = re.search(r"^.*\-(.*)\+.*$", id)
            if match:
                id = match.group(1)
            #If start of new word, record position (using raw indices)
            if len(parts)==5:
                word = parts[4]
                current_i = len(pron_str)
                if id not in IGNORE_IDS:
                    word_index[current_i] = word
                elif use_sil==1:
                    word_index[current_i] = '<sil>'
            if not id in IGNORE_IDS:
                pron_str.append(id)
            if (use_sil==1) and (end-start>0):
                pron_str.append('sil')
    _in.close()
    out.close()
    out_r.close()



def calc_utt_dp_scores_from_mlfs(aligned_mlf_name, decode_mlf_name, smat_name, use_sil, out_name):
    _in = None
    out = None
    decode_mlf_f = None
    try:
        _in = open(aligned_mlf_name)
    except:
        print(f"Error opening {aligned_mlf_name}", file=sys.stderr)
        return
    try:
        out = open(out_name, 'w')
    except:
        print(f"Error opening {out_name}", file=sys.stderr)
        return
    try:
        decode_mlf_f = open(decode_mlf_name)
    except:
        print(f"Error opening {decode_mlf_name}", file=sys.stderr)
        return
    smat = {}
    read_matrix(smat_name, smat)
    calc_utt_dp_scores_from_mlfs_buffers(_in, decode_mlf_f, smat, use_sil, out)
    _in.close()
    out.close()

def calc_utt_dp_scores_from_mlfs_buffers(_in, decode_mlf_f, smat, use_sil, out):
    decoded = {}
    read_mlf_file(decode_mlf_f,decoded)
    init_ref_scores(smat)
    add_spn(smat,spn,0)
    name = ""
    pron_str = []
    decode_str = []
    duration = 0.0
    for line in _in:
        line = line.strip()
        if 'MLF' in line:
            continue
        #Edit to suit specific label format
        match = re.search(r"([^/]+)\.((lab)|(rec))", line)
        if match:
            name = match.group(1)
        elif line == '.':
            if not name in decoded:
                print (f"WARNING: {name} skipped\n")
            else:
                decode_str = decoded[name]
                aligned_pron = []
                aligned_decode = []
                # First align strings globally (across words)
                score = align_strings(pron_str, decode_str, smat, aligned_pron, aligned_decode)
                if (COLLAPSE_REPEATED_OBS == 1) or (COLLAPSE_REPEATED_REF == 1):
                    collapse_repeated_phones(aligned_pron,aligned_decode)
                if use_sil == 2:
                    score = get_aligned_score_ignore_spn(aligned_pron,aligned_decode,smat,use_sil)
                else:
                    score = get_aligned_score(aligned_pron,aligned_decode,smat)
                #printf "DBG: aligned=%s\ndecode=%s\n", (join ' ',@pron_str), (join ' ',@decode_str);
                _len = len(aligned_pron)
                out.write("%s\t%.4f\t%d\t%.3f\t[%s]\t[%s]\n"%(name, score, _len, duration/HTK_NORMALIZATION, " ".join(aligned_pron), " ".join(aligned_decode)))
            #Clean vars for next round
            name = ""
            pron_str = []
            duration = 0.0
        else:
            parts = line.split()
            #print (f"Adding {parts}")
            id,start,end = "", 0.0,0.0
            timing_info = 0
            if len(parts)==1:
                id = parts[0]
            elif len(parts)>=3:
                timing_info = 1
                start, end, id = float(parts[0]), float(parts[1]), parts[2]
                duration = duration + (end - start)
            else:
                print("kaas")
                print("Error: currently assuming MLF contains either ID only or")
                print ("at least start time, end time and ID")
                print (f"This line ({name}) contained [{line}]")
                sys.exit(1)
            match = re.search(r'^.*\-(.*)\+.*$', id)
            if match:
                id = match.group(1)
            if not id in IGNORE_IDS:
                pron_str.append(id)
                #print "Adding $id\n";

                # TODO: Different set-ups exist. Customise for now... fix later.
            elif use_sil==2:
                if len(parts)>4:
                    print(f"Error: silence marker expected at line {line}")
                    sys.exit(1)
                if spn in parts[4]:
                    pron_str.append(spn)
            elif ((timing_info==1) and (IGNORE_INTRAWORD_SIL==0) and (end-start>0)) or ((timing_info==0) and (IGNORE_INTRAWORD_SIL==0)):
                # Only keep non-empty sil
                pron_str.append('sil')
