"""
utils/sound.py  —  Synthesised sound effects using pygame / numpy.
"""

import time
import threading
import numpy as np
from core.deps import PYGAME_OK, pygame


class SoundFX:
    @staticmethod
    def _beep(freq=880, dur=0.08, vol=0.4, shape="sine"):
        if not PYGAME_OK:
            return
        try:
            sr2 = 44100
            n   = int(sr2 * dur)
            t   = np.linspace(0, dur, n, endpoint=False)
            if shape == "square":
                w = np.sign(np.sin(2*np.pi*freq*t)).astype(np.float32)
            elif shape == "saw":
                w = (2*(t*freq - np.floor(t*freq+0.5))).astype(np.float32)
            elif shape == "robot":
                w = (0.6*np.sign(np.sin(2*np.pi*freq*t)) +
                     0.3*np.sign(np.sin(2*np.pi*freq*1.5*t)) +
                     0.1*np.sign(np.sin(2*np.pi*freq*2*t))).astype(np.float32)
            else:
                w = np.sin(2*np.pi*freq*t).astype(np.float32)
            attack  = min(int(sr2*.003), n)
            release = min(int(n*.25), n)
            env = np.ones(n, dtype=np.float32)
            env[:attack]   = np.linspace(0, 1, attack)
            env[-release:] = np.linspace(1, 0, release)
            w = (w * env * vol * 32767).astype(np.int16)
            stereo = np.ascontiguousarray(np.column_stack((w, w)))
            pygame.sndarray.make_sound(stereo).play()
        except Exception:
            pass

    @staticmethod
    def click():
        SoundFX._beep(1400, .03, .2, "square")

    @staticmethod
    def alert():
        if not PYGAME_OK: return
        def _p():
            for f in [660, 880, 660, 1100, 880]:
                SoundFX._beep(f, .1, .5, "robot"); time.sleep(.12)
        threading.Thread(target=_p, daemon=True).start()

    @staticmethod
    def boot():
        if not PYGAME_OK: return
        def _p():
            seq = [(220,.08),(330,.06),(440,.06),(550,.06),(660,.08),
                   (880,.1),(1100,.1),(1320,.12),(1100,.1),(880,.18)]
            for f, d in seq:
                SoundFX._beep(f, d, .35, "robot"); time.sleep(d+.02)
        threading.Thread(target=_p, daemon=True).start()

    @staticmethod
    def thinking():
        if not PYGAME_OK: return
        def _p():
            for f in [440, 520, 480, 560]:
                SoundFX._beep(f, .06, .15, "saw"); time.sleep(.08)
        threading.Thread(target=_p, daemon=True).start()

    @staticmethod
    def error():
        if not PYGAME_OK: return
        for f in [880, 440, 220]:
            SoundFX._beep(f, .12, .5, "square"); time.sleep(.14)

    @staticmethod
    def ack():
        if not PYGAME_OK: return
        def _p():
            SoundFX._beep(1100, .04, .3, "robot"); time.sleep(.05)
            SoundFX._beep(1320, .06, .3, "robot")
        threading.Thread(target=_p, daemon=True).start()

    @staticmethod
    def alarm_beep():
        if not PYGAME_OK: return
        def _p():
            for _ in range(8):
                SoundFX._beep(1200, .12, .7, "robot"); time.sleep(.15)
        threading.Thread(target=_p, daemon=True).start()

    @staticmethod
    def wake():
        if not PYGAME_OK: return
        def _p():
            for f in [800, 1000, 1200]:
                SoundFX._beep(f, .05, .4, "robot"); time.sleep(.06)
        threading.Thread(target=_p, daemon=True).start()