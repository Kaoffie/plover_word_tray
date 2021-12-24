import re

from typing import List, Tuple


LEFT_KEYS = {
    "SR":   [(r"s[a-z]{0,5}r", "SR"), (r"", "V")],
    "SHR":  [(r"sh.*r", "SHR"), ("", "SL")],
    "SKWR": "J",
    "SH":   "SH",
    "SPW":  [(r"int", "INT"), (r"ent", "ENT"), ("", "SB")],
    "STK":  [(r"d[ie][sz]", "DS"), ("", "SD")],
    "S":    "S",
    "THR":  [(r"th[a-z]{0,5}r", "THR"), ("", "TL")],
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
    "KPW":  [(r"imp", "IMP"), (r"emp", "EMP"), ("", "KB")],
    "KP":   [(r"[ie]x", "X"), ("", "KP")],
    "K":    "K",
    "PHR":  [(r"m.*?r", "MR"), ("", "PL")],
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
    "FRB":    [(r"[fv][a-z]{0,5}sh", "FSH"), (r"[fv][a-z]{0,5}r[a-z]{0,5}b", "FRB"), ("", "RV")],
    "FRPB":   [(r"nch", "NCH"), (r"rch", "RCH"), ("", "FRN")],
    "FP":     "CH",
    "FRP":    [(r"mp", "MP"), ("", "FRP")],
    "FR":     [(r"rf", "RF"), ("", "FR")],
    "F":      "F",
    "RPBLGZ": [(r"rn[aeiou]?l[a-z]{0,5}[zs]ing", "RNLZG"), ("", "RJZ")],
    "RPBG":   [(r"r[a-z]{0,5}p[a-z]{0,5}[ck]", "RPK"), ("", "RNG")],
    "RPBLG":  [(r"rn[aeiou]?l[a-z]{0,5}g", "RNLG"), ("", "RJ")],
    "RB":     [(r"r[a-z]{0,5}b", "RB"), ("", "SH")],
    "RPB":    "RN",
    "R":      "R",
    "PLT":    [(r"m[a-z]{0,5}nt", "MNT"), (r"p[aoiyeu]*l", "PLT"), ("", "MT")],
    "PBG":    [(r"p[a-z]{0,5}[ck]", "PK"), ("", "NG")],
    "PBLG":   [(r"n[a-z]{0,5}lo?g", "NLJ"), (r"n[a-z]{0,5}lch", "NLCH"), ("", "J")],
    "PL":     [(r"p[aoiyeu]*l", "PL"), ("", "M")],
    "PB":     "N",
    "P":      "P",
    "BGS":    [(r"[ck][aeiou]?[tsc][ie][ao]n|[ck]sh[eu]n", "KSHUN"), (r"b[a-z]{0,5}[tsc][ie][ao]n|b[a-z]{0,5}sh[eu]n", "BSHUN"), (r"b[a-z]{0,5}gs", "BGS"), (r"x", "X"), ("", "KS")],
    "BG":     [(r"b[a-z]{0,5}g", "BG"), ("", "K")],
    "B":      "B",
    "LGS":    [(r"l[a-z]{0,5}[tsc][ie][ao]n|l[a-z]{0,5}sh[eu]n", "LSHUN"), (r"[tsc][ie][ao]n[a-z]{0,5}l|sh[eu]n[a-z]{0,5}l", "SHUNL"), (r"lo?gs", "LJS"), (r"lchs", "LCHS"), ("", "LGS")],
    "LG":     [(r"lo?g", "LJ"), (r"lch", "LCH"), ("", "LG")],
    "L":      "L",
    "GS":     [(r"[tsc][ie][ao]n|sh[eu]n", "SHUN"), ("", "GS")],
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
def eat(chord: str, word: str, key_map: dict, star_key_map: dict, starred: bool) -> (str, str, str):
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


def to_pseudo_single(chord: str, word: str) -> (str, str):
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
