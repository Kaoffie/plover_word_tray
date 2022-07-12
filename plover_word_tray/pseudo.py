import re

from typing import List, Tuple


LEFT_KEYS = {
    "SR":   [(r"s[a-z]{0,5}r", "SR"), (r"", "V")],
    "SHR":  [(r"sh.*r", "SHR"), ("", "SL")],
    "SKWR": "J",
    "SH":   "SH",
    "SPW":  [(r"int", "INT"), (r"ent", "ENT"), ("", "SB")],
    "STKPW": [(r"(s|[aeiou])[a-z]{0,5}g", "SG"), (r"d[ie][szc][a-z]{0,5}b", "DSB"), ("", "STKPW")],
    "STK":  [(r"d[ie][szc]", "DS"), ("", "SD")],
    "S":    "S",
    "THR":  [(r"th[a-z]{0,5}r", "THR"), ("", "TL")],
    "TPHR": [(r"t[a-z]{0,5}p[aeiou]?l", "TPL"), (r"t[a-z]{0,5}m[a-z]{0,5}r", "TMR"), (r"n[a-z]{0,5}r", "NR"), ("", "FL")],
    "TH":   "TH",
    "TPH":  [(r"t[a-z]{0,5}m", "TM"), ("", "N")],
    "TKPW": [(r"d.*b", "DB"), ("", "G")],
    "TP":   [(r"t[a-z]{0,5}p", "TP"), ("", "F")],
    "TK":   [(r"t[a-z]{0,5}k", "TK"), ("", "D")],
    "T":    "T",
    "KR":   [(r"[ck].*?r", "KR"), ("", "C")],
    "KHR":  [(r"ch[a-z]{0,5}r", "CHR"), ("", "KL")],
    "KWR":  "Y",
    "KH":   "CH",
    "KW":   [(r"q[^uw]", "Q"), ("", "KW")],
    "KPH": [(r"[ck][aeiou]?mm?", "KM"), (r"x[a-z]{0,5}h", "XH"), ("", "KPH")],
    "KPW":  [(r"imp", "IMP"), (r"emp", "EMP"), ("", "KB")],
    "KP":   [(r"[ie]x", "X"), (r"cc", "X"), ("", "KP")],
    "K":    "K",
    "PHR":  [(r"pl", "PL"), (r"m[aeiou]{0,2}r", "MR"), ("", "PHR")],
    "PH":   "M",
    "PW":   "B",
    "P":    "P",
    "WHR":  [(r"w.*?l", "WL"), ("", "WHR")],
    "W":    "W",
    "HR":   "L",
    "H":    "H",
    "R":    "R"
}


LEFT_STARRED = {
    "S":    [(r"z", "Z")]
}


MID_KEYS = {
    "-":        "",
    "AU":       "AU",
    "AEU":      "AI",
    "A*U":      "*AU",
    "A*EU":     "*AI",
    "AOU":      "UU",
    "AOEU":     "II",
    "AO*U":     "*UU",
    "AO*EU":    "*II",
    "AE":       [(r"ea", "EA"), ("", "AE")],
    "A*E":      [(r"ea", "*EA"), ("", "*AE")],
    "AOE":      "EE",
    "AO*E":     "*EE",
    "A*":       "A*",
    "AO*":      [(r"oo", "OO*"), (r"OA", "OA*"), ("", "AO*")],
    "AO":       [(r"oo", "OO"), (r"OA", "OA"), ("", "AO")],
    "A":        "A",
    "OU":       "OU",
    "OEU":      "OI",
    "O*U":      "*OU",
    "O*EU":     "*OI",
    "OE":       "OE",
    "O*E":      "*OE",
    "O*":       "O*",
    "O":        "O",
    "*U":       "*U",
    "*EU":      "*I",
    "*E":       "*E",
    "*":        "*",
    "EU":       "I",
    "E":        "E",
    "U":        "U"
}


RIGHT_KEYS = {
    "FPB":    [(r"(s|z|th|f)[a-z]{0,5}n", "FN"), ("", "FPB")],
    "FRB":    [(r"[fv][a-z]{0,5}sh", "FSH"), (r"[fv][a-z]{0,5}r[a-z]{0,5}b", "FRB"), ("", "RV")],
    "FRPB":   [(r"nch", "NCH"), (r"rch", "RCH"), ("", "FRN")],
    "FP":     [(r"(s|z|th|f)p", "FP"), (r"ch|c", "CH"), ("", "FP")],
    "FRP":    [(r"mp", "MP"), ("", "FRP")],
    "FR":     [(r"rf", "RF"), ("", "FR")],
    "F":      "F",
    "RPBLGZ": [(r"rn[aeiou]?l[a-z]{0,5}[zs]ing", "RNLZG"), ("", "RJZ")],
    "RPBG":   [(r"r[a-z]{0,5}p[a-z]{0,5}[ck]", "RPK"), ("", "RNG")],
    "RPBLG":  [(r"rn[aeiou]?l[a-z]{0,5}g", "RNLG"), ("", "RJ")],
    "RBG":    [(r"r[a-z]{0,5}b[a-z]{0,5}g", "RBG"), (r"(sh|ti|ci|s)[a-z]{0,5}g", "SHG"), ("", "RK")],
    "RB":     [(r"r[a-z]{0,5}b", "RB"), (r"(sh|ti|ci|s)", "SHG"), ("", "RB")],
    "RPB":    "RN",
    "R":      "R",
    "PLT":    [(r"m[a-z]{0,5}nt", "MNT"), (r"p[aoiyeu]*l", "PLT"), ("", "MT")],
    "PBGS":    [(r"p[a-z]{0,5}[ck]s", "PKS"), (r"n[aeiou]{0,2}[tsc][ie][ao]n|n[aeiou]{0,2}sh[eu]n", "NSHUN"), ("", "NGS")],
    "PBG":    [(r"p[a-z]{0,5}[ck]", "PK"), ("", "NG")],
    "PBLG":   [(r"n[a-z]{0,5}lo?g", "NLJ"), (r"n[a-z]{0,5}lch", "NLCH"), ("", "J")],
    "PL":     [(r"p[aoiyeu]*l", "PL"), ("", "M")],
    "PB":     "N",
    "P":      "P",
    "BGS":    [(r"x[aeiou]?tion", "KSHUN"), (r"x", "X"), (r"[ck][aeiou]?[tsc][ie][ao]n|[ck]sh[eu]n", "KSHUN"), (r"b[a-z]{0,5}[tsc][ie][ao]n|b[a-z]{0,5}sh[eu]n", "BSHUN"), (r"b[a-z]{0,5}gs", "BGS"), ("", "KS")],
    "BG":     [(r"b[a-z]{0,5}g", "BG"), ("", "K")],
    "B":      "B",
    "LGS":    [(r"l[a-z]{0,5}[tsc][ie][ao]n|l[a-z]{0,5}sh[eu]n", "LSHUN"), (r"[tsc][ie][ao]n[a-z]{0,5}l|sh[eu]n[a-z]{0,5}l", "SHUNL"), (r"lo?gs", "LJS"), (r"lchs", "LCHS"), ("", "LGS")],
    "LG":     [(r"lo?g", "LJ"), (r"lch", "LCH"), ("", "LG")],
    "L":      "L",
    "GS":     [(r"[tscg]h?[ie][ao]n|sh[eu]n", "SHUN"), ("", "GS")],
    "G":      "G",
    "T":      "T",
    "S":      "S",
    "D":      "D",
    "Z":      "Z"
}


RIGHT_STARRED = {
    "F":    [(r"v", "V")],
    "RPBG": [(r"r[a-z]{0,5}n[ck]k?|n[ck]k?[a-z]{0,5}r", "RNK")],
    "PBG":  [(r"n[ck]k?", "NK")],
    "PL":   [(r"mp", "MP")],
    "LG":   [(r"l[ck]k?", "LK")],
    "T":    [(r"th", "TH")]
}

# Returns: Remaining Chord, Remaining Word, Partial Pseudo Steno
def eat(chord: str, word: str, key_map: dict, star_key_map: dict, starred: bool) -> Tuple[str, str, str]:
    out_chord = ""
    for key, value in key_map.items():
        if chord.startswith(key):
            out_chord = chord[len(key):]
            if isinstance(value, str):
                return out_chord, word, value
            else:
                if starred and key in star_key_map:
                    value = star_key_map[key] + value
                for reg, psd in value:
                    if reg:
                        match = re.search(reg, word)
                        if match is not None:
                            l, r = match.span()
                            return out_chord, word[r:], psd
                    else:
                        return out_chord, word, psd

def to_pseudo_single(chord: str, word: str) -> Tuple[str, str]:
    if chord == "#":
        return "#", word

    # Parse chord into keys
    is_num = any(c.isdigit() or c == "#" for c in chord)
    all_num = all(c.isdigit() for c in chord)
    if is_num:
        brief = chord.translate(str.maketrans("1234506789", "STPHAOFPLT"))
    else:
        brief = chord

    mid = "".join(c for c in brief if c in "AO*-EU")
    if mid:
        groups = brief.replace("#", "").split(mid)
        left = groups[0]
        right = groups[1]
    elif all_num:
        mid = "-"
        left = "".join(c for c in brief if c in "STPH")
        right = "".join(c for c in brief if c in "FPLT")
    else:
        mid = "-"
        left = brief
        right = ""

    star = "*" in mid

    # Consume keys
    rem_word = word
    pseudo_header = is_num * "#"

    # Consume left bank keys
    rem_left = left
    pseudo_left = ""
    while len(rem_left):
        eaten = eat(
            rem_left, 
            rem_word, 
            LEFT_KEYS,
            LEFT_STARRED,
            star
        )

        if eaten is None:
            return (chord, word)

        rem_left, rem_word, new_pseudo = eaten
        pseudo_left += new_pseudo

    # Consume vowel keys
    rem_mid, rem_word, pseudo_mid = eat(
        mid,
        rem_word,
        MID_KEYS,
        {},
        False
    )

    # Consume right bank keys
    rem_right = right
    pseudo_right = ""
    while len(rem_right):
        rem_right, rem_word, new_pseudo = eat(
            rem_right, 
            rem_word, 
            RIGHT_KEYS,
            RIGHT_STARRED,
            star
        )

        pseudo_right += new_pseudo

    if pseudo_right and not pseudo_mid:
        pseudo_mid = "-"
    
    pseudo_builder = pseudo_header + pseudo_left + pseudo_mid + pseudo_right

    return pseudo_builder, rem_word


def format_pseudo(outline: Tuple[str, ...], word: str) -> Tuple[str, ...]:
    rem_word = word.lower()
    stroke_builder = []
    for stroke in outline:
        pseudo, rem_word = to_pseudo_single(stroke, rem_word)
        stroke_builder.append(pseudo)
    
    return tuple(stroke_builder)


test_list = [
    ("access", "KPES"),
    ("execution", "EBGS/KAOUGS"),
    ("taxation", "TA*EUBGS"),
    ("commune", "KPHAOUPB"),
    ("simpler", "SPHRER"),
    ("decision", "STKEUGS"),
    ("distinguish", "STKPWEUGS"),
    ("again", "STKPWEPB"),
    ("region", "RAOEGS"),
    ("fashion", "TPAGS"),
    ("donation", "TKOEPBGS"),
    ("mention", "PHEPBGS"),
    ("absorption", "SPWORBGS"),
    ("dark", "TKARBG"),
    ("everybody", "EFRB"),
    ("several", "SEFRL"),
    ("silver", "SEUFRL"),
    ("disposition", "TKEUFPGS"),
    ("suspicion", "SUFPGS"),
    ("resistant", "REUFPBT"),
    ("defend", "TKEFPBD"),
    ("whisper", "WHEUFP/*ER"),
    ("helpful", "HEFPL"),
    ("evidence based medicine", "PWEFPL"),
]

if __name__ == "__main__":
    for (word, outline) in test_list:
        outline_s = tuple(outline.split("/"))
        print(word, format_pseudo(outline_s, word))
