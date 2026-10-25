# -*- coding: utf-8 -*-
import numpy as np

def vb_pairs(m):
    """unique (vertex, bone) pairs with summed weight (w>0)."""
    if hasattr(m, '_vb'):
        return m._vb
    bidx, bw = m.np_bidx, m.np_bw
    nb = len(m.bones) + 1
    V = len(bidx)
    vv = np.repeat(np.arange(V, dtype=np.int64), 4)
    bb = bidx.reshape(-1).astype(np.int64)
    ww = bw.reshape(-1)
    mask = (bb >= 0) & (ww > 0)
    keys = vv[mask] * nb + bb[mask]
    uk, inv = np.unique(keys, return_inverse=True)
    wsum = np.bincount(inv, weights=ww[mask])
    m._vb = (uk // nb, uk % nb, wsum)
    return m._vb

def weights_per_bone2(m):
    v, b, w = vb_pairs(m)
    nb = len(m.bones)
    cnt = np.bincount(b, minlength=nb)[:nb]
    sm = np.bincount(b, weights=w, minlength=nb)[:nb]
    y = m.np_co[v, 1]
    ymin = np.full(nb, np.inf); ymax = np.full(nb, -np.inf)
    np.minimum.at(ymin, b, y); np.maximum.at(ymax, b, y)
    return cnt, sm, ymin, ymax

def influences_per_vertex(m):
    v, b, w = vb_pairs(m)
    return np.bincount(v, minlength=len(m.np_co))
