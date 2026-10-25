# -*- coding: utf-8 -*-
"""Thin wrapper around mmd_tools' pure-python PMX reader (Blender 3.6 / mmd_tools 1.0.2 copy).
Adds: flip(9)/impulse(10) morph support, raw texture path retention, pickle cache."""
import importlib.util, os, sys, pickle, hashlib, struct, logging

PMX_MOD_PATH = r"C:\Users\haoni\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\mmd_tools\core\pmx\__init__.py"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')

spec = importlib.util.spec_from_file_location("mmd_pmx", PMX_MOD_PATH)
pmx = importlib.util.module_from_spec(spec)
sys.modules['mmd_pmx'] = pmx
spec.loader.exec_module(pmx)
logging.disable(logging.CRITICAL)

# ---- raw texture path
def _tex_load(self, fs):
    self.raw_path = fs.readStr()
    self.path = self.raw_path
pmx.Texture.load = _tex_load

# ---- flip / impulse morphs
class FlipMorphOffset:
    def load(self, fs):
        self.morph = fs.readMorphIndex()
        self.factor = fs.readFloat()
class FlipMorph(pmx.Morph):
    def type_index(self): return 9
    def load(self, fs):
        n = fs.readInt()
        self.offsets = []
        for i in range(n):
            o = FlipMorphOffset(); o.load(fs); self.offsets.append(o)
class ImpulseMorphOffset:
    def load(self, fs):
        self.rigid = fs.readRigidIndex()
        self.local = fs.readByte()
        self.velocity = fs.readVector(3)
        self.torque = fs.readVector(3)
class ImpulseMorph(pmx.Morph):
    def type_index(self): return 10
    def load(self, fs):
        n = fs.readInt()
        self.offsets = []
        for i in range(n):
            o = ImpulseMorphOffset(); o.load(fs); self.offsets.append(o)

_CLASSES = {0: pmx.GroupMorph, 1: pmx.VertexMorph, 2: pmx.BoneMorph, 3: pmx.UVMorph, 4: pmx.UVMorph,
            5: pmx.UVMorph, 6: pmx.UVMorph, 7: pmx.UVMorph, 8: pmx.MaterialMorph, 9: FlipMorph, 10: ImpulseMorph}
def _create(fs):
    name = fs.readStr(); name_e = fs.readStr()
    category = fs.readSignedByte(); typeIndex = fs.readSignedByte()
    ret = _CLASSES[typeIndex](name, name_e, category, type_index=typeIndex)
    ret.type_idx = typeIndex
    ret.load(fs)
    return ret
pmx.Morph.create = staticmethod(_create)

def load(path, use_cache=True):
    st = os.stat(path)
    key = hashlib.md5((os.path.abspath(path) + str(st.st_size) + str(st.st_mtime)).encode('utf-8')).hexdigest()
    cp = os.path.join(CACHE, key + '.pkl')
    if use_cache and os.path.exists(cp):
        with open(cp, 'rb') as f:
            return pickle.load(f)
    m = pmx.load(path)
    # convert vertices to numpy-friendly compact arrays to make pickles smaller
    import numpy as np
    nv = len(m.vertices)
    co = np.array([v.co for v in m.vertices], dtype=np.float64) if nv else np.zeros((0, 3))
    wtype = np.array([v.weight.type for v in m.vertices], dtype=np.int8)
    bidx = np.full((nv, 4), -1, dtype=np.int32)
    bw = np.zeros((nv, 4), dtype=np.float64)
    sdef_c = {}
    for i, v in enumerate(m.vertices):
        w = v.weight
        if w.type == 0:
            bidx[i, 0] = w.bones[0]; bw[i, 0] = 1.0
        elif w.type == 1:
            bidx[i, :2] = w.bones; bw[i, 0] = w.weights[0]; bw[i, 1] = 1.0 - w.weights[0]
        elif w.type == 2:
            bidx[i, :4] = w.bones; bw[i, :4] = w.weights
        elif w.type == 3:
            bidx[i, :2] = w.bones; bw[i, 0] = w.weights.weight; bw[i, 1] = 1.0 - w.weights.weight
            sdef_c[i] = (w.weights.c, w.weights.r0, w.weights.r1)
    uv = np.array([v.uv for v in m.vertices], dtype=np.float32) if nv else np.zeros((0, 2))
    edge = np.array([v.edge_scale for v in m.vertices], dtype=np.float32) if nv else np.zeros((0,))
    m.np_co = co; m.np_wtype = wtype; m.np_bidx = bidx; m.np_bw = bw; m.np_uv = uv; m.np_edge = edge
    m.sdef = sdef_c
    m.vertices = None  # drop heavy objects
    m.faces = list(m.faces)
    with open(cp, 'wb') as f:
        pickle.dump(m, f, protocol=pickle.HIGHEST_PROTOCOL)
    return m
