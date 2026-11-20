import json as J, os, sys, time, urllib.request as U2
U = os.environ.get("MAKEFUN_ENV_URL")
MS = int(os.environ.get("CHESS_MS", "3500"))
INF = 10 ** 7
MATE = 100000
V = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}
MGD = {'p': "&K>>>>>>>~'Ob~%``#x~%M~%|CKQC`5~&,~%|DY7M@3C~&#:W;OC3B~&(=T>8K>\\~%|'`+;FeL~%mT>>>>>>>", 'n': '$`~\';u/~\'[~$i~\'?~%M`^~\'^~&\'1e~%r& ~\'X\'ZQk~%q!~%tX@`.^~%vB~&(OJ;M5@!/LS<G<F~&"1&gG@Q~&+9~%S~\'A~&&WN3G:', 'b': '&._~%SkJ-o/,h~&)Ci[~&"~%h]sD;9M1~&$<GL]1> 5:Q>KF(<8:M>>=K568I?.ELJ~&+~&)\\37F?#P', 'r': '&8DLN=5~%}I,Z:IFC-1#QKH-L4+:JTG?~&!D6eM6;D;=:J:C<C5J4G:F;J-D69=F:@?9=', 'q': '&J-GQ%48+MYQ5DE,B/N1G;EJ50-O=F<E8&>FG:ADE 7EH:NI1~&%@LHB5U2~&)K9?;I49', 'k': '&LG45?66AIABD8<+H8J/G>6Q3 I=?:EI68F7C1D=@<AA774H=R>19DB:6W:=.<L79'}
EGD = {'p': '&K>>>>>>>~(A9/&K/_T~%LD/,3;[@~%u6367DK>::2:>=I:CA=9=9B7S9>@A1@5E>>>>>>>', 'n': '%oRW/;B~&\'~&\'~\'7O-U7.?"ZB\\=464(VRQ>>3;$>JTG5?1(9R@N91-<*THCA,;)M(ZF7B~&+0', 'b': '&=7HA?<67NBI+G4G4N4F==F8B7JA;C:7=6GHD2A18;GI@A446?:IDC182BL0P:7I2', 'r': '&X;F;;>:;D@><0DC9B>><=7<@E=H2?=<A?@A:5=<;EB9B89B6H>D@3><F8I?::6O&', 'q': '&:>>;;>>>E>>>>>>>M>>>>>>>E>>>>>>>@>>>>>>>A>>>>>>>B>>>>>>>@>>>>>>>', 'k': "%_eO>EX3)C[;A>S/2=ED6CW=~&,)\\@A=E7')LWAA:0*6NLH@75.,NMG?452~&'QKH-L4+"}
def _dec(s):
    out = [(ord(s[0]) - 33) * 94 + ord(s[1]) - 33 - 512]
    oa = out.append
    i = 2
    while i < len(s):
        if s[i] == "~":
            oa(out[-1] + (ord(s[i + 1]) - 33) * 94 + ord(s[i + 2]) - 33 - 512)
            i += 3
        else:
            oa(out[-1] + ord(s[i]) - 62)
            i += 1
    return out
MG = {k: _dec(MGD[k]) for k in MGD}
EG = {k: _dec(EGD[k]) for k in EGD}
PH = 12 * (V["n"] + V["b"] + V["r"]) + 2 * V["q"]
A = "abcdefgh"
PROM = ("q", "r", "b", "n")
OFF_N = (-25, -23, -14, -10, 10, 14, 23, 25)
OFF_B = (-13, -11, 11, 13)
OFF_R = (-12, -1, 1, 12)
OFF_Q = OFF_B + OFF_R
OFF_K = OFF_Q
SLIDE = {"b": OFF_B, "r": OFF_R, "q": OFF_Q}
for _i in range(120):
    pass
class TimeUp(Exception):
    pass
class Pos:
    __slots__ = ("b", "w", "hst", "nodes", "deadln", "ep", "cr")
    def __init__(self):
        self.b = [" "] * 120
        for i in range(120):
            r, c = divmod(i, 10)
            if not (2 <= r <= 9 and 1 <= c <= 8):
                self.b[i] = "#"
        self.w = True
        self.hst = []
        self.nodes = 0
        self.deadln = 0.0
        self.ep = 0
    def setup(self, fen):
        b = ["."] * 144
        for i in range(144):
            if not (2 <= i // 12 <= 9 and 2 <= i % 12 <= 9):
                b[i] = "#"
        ef = fen.split()
        for ri, row in enumerate(ef[0].split("/")):
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch)
                else:
                    b[(ri + 2) * 12 + 2 + f] = ch
                    f += 1
        self.b = b
        self.w = ef[1] == "w"
        cr = ef[2] if len(ef) > 2 else "-"
        self.cr = (cr, "K" in cr, "Q" in cr, "k" in cr, "q" in cr)
        self.ep = A.index(ef[3][0]) + 2 + (10 - int(ef[3][1])) * 12 if len(ef) > 3 and ef[3] != "-" else 0
        self.hst = []
    def atkd(self, sq, w2):
        b = self.b
        w = w2
        d = 12 if w else -12
        if b[sq + d - 1] == ("P" if w else "p") or b[sq + d + 1] == ("P" if w else "p"):
            return True
        nk = "N" if w else "n"
        for o in OFF_N:
            if b[sq + o] == nk:
                return True
        kg = "K" if w else "k"
        for o in OFF_K:
            if b[sq + o] == kg:
                return True
        bi, ro, qu = ("B", "R", "Q") if w else ("b", "r", "q")
        for o in OFF_B + OFF_R:
            s = sq + o
            c = b[s]
            while c == ".":
                s += o
                c = b[s]
            if c == bi or c == qu or (c == ro and o in OFF_R):
                return True
        return False
    def king(self, w):
        b = self.b
        t = "K" if w else "k"
        for s in range(26, 118):
            if b[s] == t:
                return s
        return 0
    def gen(self, co=False):
        b = self.b
        w = self.w
        res = []
        ra = res.append
        for s in range(26, 118):
            p = b[s]
            if p == "#" or p == "." or p.isupper() != w:
                continue
            lo = p.lower()
            if lo == "p":
                d = -12 if w else 12
                st = s + d
                q = b[st]
                pro = (st // 12 == 2) if w else (st // 12 == 9)
                if q == ".":
                    if pro:
                        for i in range(4):
                            ra((s, st, 1, i))
                    elif not co:
                        ra((s, st, 0, 0))
                    if s // 12 == (8 if w else 3) and b[st + d] == ".":
                        ra((s, st + d, 0, 0))
                for dc in (-1, 1):
                    t = s + d + dc
                    tp = b[t]
                    if tp != "#" and tp != "." and tp.isupper() != w:
                        if pro:
                            for i in range(4):
                                ra((s, t, 1, i))
                        else:
                            ra((s, t, 0, 0))
                    elif t == self.ep and self.ep:
                        ra((s, t, 0, 0))
            elif lo in SLIDE:
                for o in SLIDE[lo]:
                    t = s + o
                    tp = b[t]
                    while tp == ".":
                        if not co:
                            ra((s, t, 0, 0))
                        t += o
                        tp = b[t]
                    if tp != "#" and tp.isupper() != w:
                        ra((s, t, 0, 0))
            elif lo == "k":
                for o in OFF_K:
                    t = s + o
                    tp = b[t]
                    if tp == ".":
                        if not co:
                            ra((s, t, 0, 0))
                    elif tp != "#" and tp.isupper() != w:
                        ra((s, t, 0, 0))
            elif lo == "n":
                for o in OFF_N:
                    t = s + o
                    tp = b[t]
                    if tp == "." :
                        if not co:
                            ra((s, t, 0, 0))
                    elif tp != "#" and tp.isupper() != w:
                        ra((s, t, 0, 0))
        if not co:
            f = 114 if w else 30
            if b[f] in "Kk" and not self.atkd(f, not w):
                for d1, d2, dr, ci in ((1, 2, 117, 1), (-1, -2, 110, 2), (1, 2, 33, 3), (-1, -2, 26, 4)):
                    if self.cr[ci] and b[f + d1] == "." and b[f + d2] == "." and b[dr] == ("R" if w else "r") and \
                            not self.atkd(f + d1, not w):
                        ra((f, f + d2, 2, 0))
        return res
    def make(self, m):
        s, t, pm, pi = m
        b = self.b
        cap = b[t]
        p = b[s]
        w = self.w
        ie = p.lower() == "p" and t == self.ep and cap == "." and s % 12 != t % 12
        self.hst.append((b[t + (12 if w else -12)] if ie else cap, self.ep, ie, self.cr))
        b[s] = "."
        b[t] = PROM[pi].upper() if pm == 1 and w else (PROM[pi] if pm == 1 else p)
        if pm == 2:
            if t == 116: b[115], b[117] = b[117], "."
            elif t == 112: b[113], b[110] = b[110], "."
            elif t == 32: b[31], b[33] = b[33], "."
            else: b[29], b[26] = b[26], "."
        if ie:
            b[t + (12 if w else -12)] = "."
        self.ep = (s + t) // 2 if (p == "P" or p == "p") and abs(t - s) == 24 else 0
        c = list(self.cr)
        if p == "K": c[1] = c[2] = False
        elif p == "k": c[3] = c[4] = False
        for q, ci in ((117, 1), (110, 2), (33, 3), (26, 4)):
            if s == q or t == q:
                c[ci] = False
        self.cr = tuple(c)
        self.w = not w
        return cap
    def unmake(self, m, cap):
        s, t, pm, pi = m
        b = self.b
        self.w = not self.w
        ocap, oep, ie, ocr = self.hst.pop()
        self.cr = ocr
        p = b[t]
        if pm == 1:
            p = "P" if self.w else "p"
        b[s] = p
        b[t] = "." if ie else ocap
        if pm == 2:
            if t == 116: b[115], b[117] = ".", b[115]
            elif t == 112: b[113], b[110] = ".", b[113]
            elif t == 32: b[31], b[33] = ".", b[31]
            else: b[29], b[26] = ".", b[29]
        if ie:
            b[t + (12 if self.w else -12)] = ocap
        self.ep = oep
    def legal(self, co=False):
        out = []
        oa = out.append
        me = self.w
        for m in self.gen(co):
            cap = self.make(m)
            ks = self.king(me)
            ok = not self.atkd(ks, not me)
            self.unmake(m, cap)
            if ok:
                oa(m)
        return out
def uci(m, flip):
    s, t, pm, pi = m
    f = lambda x: A[(x % 12) - 2] + str(10 - x // 12)
    r = f(s) + f(t)
    if pm == 1:
        r += PROM[pi]
    return r
def from_uci(x, flip):
    s = A.index(x[0]) + 2 + (10 - int(x[1])) * 12
    t = A.index(x[2]) + 2 + (10 - int(x[3])) * 12
    pi = PROM.index(x[4]) if len(x) > 4 else 0
    return (s, t, 1 if len(x) > 4 else 0, pi)
def ev(pos):
    b = pos.b
    mg = eg = ph = 0
    s = 26
    for r in range(8):
        for c in range(8):
            p = b[s + c]
            if p != ".":
                lo = p.lower()
                w2 = p.isupper()
                i = r * 8 + c if w2 else (7 - r) * 8 + c
                v = V[lo]
                t = MG[lo][i] + v - EG[lo][i] - v
                if w2:
                    mg += MG[lo][i] + v
                    eg += EG[lo][i] + v
                else:
                    mg -= MG[lo][i] + v
                    eg -= EG[lo][i] + v
                if v > 1 and lo != "k":
                    ph += v
        s += 12
    ph = PH if ph > PH else ph
    sc = (mg * ph + eg * (PH - ph)) // PH
    return sc if pos.w else -sc
def mvsc(pos, m, ply):
    s, t, pm, pi = m
    b = pos.b
    tp = b[t]
    sc = 0
    if tp != "." and tp != "#":
        sc += 10000 + V[tp.lower()] - V[b[s].lower()] // 10
    if pm:
        sc += 8000 + pi * 100
    return sc
def qsrch(pos, al, be, ply):
    pos.nodes += 1
    if not pos.nodes & 1023 and time.time() > pos.deadln:
        raise TimeUp
    stand = ev(pos)
    if stand >= be:
        return be
    al = max(al, stand)
    ms = pos.legal(True)
    ms.sort(key=lambda m: mvsc(pos, m, ply), reverse=True)
    for m in ms:
        cap = pos.make(m)
        try:
            sc = -qsrch(pos, -be, -al, ply + 1)
        finally:
            pos.unmake(m, cap)
        if sc >= be:
            return be
        al = max(al, sc)
    return al
def search(pos, depth, al, be, ply):
    pos.nodes += 1
    if not pos.nodes & 1023 and time.time() > pos.deadln:
        raise TimeUp
    if ply >= 40:
        return ev(pos)
    ms = pos.legal()
    if not ms:
        return -MATE + ply if pos.atkd(pos.king(pos.w), not pos.w) else 0
    if depth <= 0:
        return qsrch(pos, al, be, ply)
    ms.sort(key=lambda m: mvsc(pos, m, ply), reverse=True)
    best = -INF
    for m in ms:
        cap = pos.make(m)
        try:
            sc = -search(pos, depth - 1, -be, -al, ply + 1)
        finally:
            pos.unmake(m, cap)
        if sc > best:
            best = sc
        if best > al:
            al = best
        if al >= be:
            return best
    return best
def pick(pos, lu):
    ms = [from_uci(x, False) for x in lu]
    flip = False
    best = ms[0]
    if len(ms) == 1:
        return uci(best, flip)
    pos.deadln = time.time() + MS / 1000.0 * 0.9
    pos.nodes = 0
    try:
        for d in range(1, 12):
            sc = -INF
            cand = best
            for m in ms:
                cap = pos.make(m)
                try:
                    v = -search(pos, d - 1, -INF, INF, 1)
                finally:
                    pos.unmake(m, cap)
                if v > sc:
                    sc, cand = v, m
                if sc > MATE - 100:
                    break
            best = cand
            if sc > MATE - 100:
                break
    except TimeUp:
        pass
    return uci(best, flip)
def post(p, b):
    r = U2.Request(U + p, data=J.dumps(b).encode(), headers={"content-type": "application/json"})
    return J.load(U2.urlopen(r))
def main():
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            print("done", g.get("wins"), g.get("draws"), g.get("losses"), file=sys.stderr)
            return
        pos = Pos()
        while g["status"] == "your_move":
            pos.setup(g["fen"])
            move = pick(pos, g["legal_moves"])
            g = post("/move", {"game": g["game"], "move": move})
if __name__ == "__main__" and U:
    main()
