#!/usr/bin/env python3
"""Generate original stereo industrial/alien ambience for the Satisfactory-inspired project.
These are synthesized sound studies, not samples or reconstructions of game audio.
Output: assets/audio/generated/*.wav (48 kHz, 16-bit, stereo).
"""
import json, math, os, random, struct, wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "audio", "generated")
os.makedirs(OUT, exist_ok=True)
SR = 48000
random.seed(2100)

def clamp(x): return max(-1.0, min(1.0, x))

def write_wav(name, seconds, sample_fn):
    frames = int(SR * seconds)
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        chunk = bytearray()
        for i in range(frames):
            t = i / SR
            l, r = sample_fn(t, i)
            chunk += struct.pack("<hh", int(clamp(l)*32767), int(clamp(r)*32767))
            if len(chunk) >= 65536:
                wf.writeframesraw(chunk); chunk.clear()
        if chunk: wf.writeframesraw(chunk)
    return path

def fade(t, duration, edge=.15):
    return min(1.0, t/(duration*edge), (duration-t)/(duration*edge))

def motor(t, i):
    # Warm low-frequency motor bed, upper bearing whine and gentle load oscillation.
    load = .72 + .18*math.sin(2*math.pi*.31*t) + .08*math.sin(2*math.pi*.07*t)
    base = (math.sin(2*math.pi*58*t) + .34*math.sin(2*math.pi*116*t) +
            .15*math.sin(2*math.pi*174*t) + .07*math.sin(2*math.pi*412*t))*load
    return base*.22, base*.20 + .018*math.sin(2*math.pi*420*t)

def drone(t, i):
    # Multi-rotor pulse train with a subtle moving stereo image.
    rotor = sum(math.sin(2*math.pi*(94+k*2.7)*t + .28*k) for k in range(4))*.12
    blade = math.sin(2*math.pi*23*t)**8
    body = rotor + .20*blade*math.sin(2*math.pi*188*t) + .05*math.sin(2*math.pi*690*t)
    pan = .55 + .18*math.sin(2*math.pi*.13*t)
    return body*pan, body*(1.1-pan)

def train(t, i):
    # Rail rhythm: low rolling rumble plus short wheel-joint knocks.
    rumble = .22*math.sin(2*math.pi*39*t) + .10*math.sin(2*math.pi*78*t)
    phase = (t*3.4) % 1.0
    click = math.exp(-((phase-.08)/.025)**2)*.42 + math.exp(-((phase-.58)/.035)**2)*.23
    metallic = click*(math.sin(2*math.pi*970*t)+.35*math.sin(2*math.pi*1480*t))
    return rumble+metallic*.35, rumble*.92+metallic*.42

def conveyor(t, i):
    # Repeating belt seam/roller texture over a quiet drive motor.
    phase = (t*2.6) % 1
    thump = math.exp(-((phase-.12)/.035)**2)*.33
    roller = .09*math.sin(2*math.pi*82*t)+.04*math.sin(2*math.pi*164*t)
    tick = thump*(math.sin(2*math.pi*520*t)+.3*math.sin(2*math.pi*920*t))
    return roller+tick, roller*.96+tick*.92

def pump(t, i):
    pulse = .5 + .5*math.sin(2*math.pi*1.7*t)
    body = .20*math.sin(2*math.pi*48*t) + .12*math.sin(2*math.pi*96*t)
    valve = .07*math.sin(2*math.pi*(260+12*math.sin(2*math.pi*.4*t))*t)
    return (body+valve)*(.55+.45*pulse), (body+valve)*(.52+.48*pulse)

def fluid(t, i):
    n = random.uniform(-1,1)
    # Filtered-feeling bubbling noise with slow swells and a few resonant glugs.
    swell = .4 + .6*(.5+.5*math.sin(2*math.pi*.23*t))
    glug = math.sin(2*math.pi*(5.5+1.2*math.sin(2*math.pi*.17*t))*t)**9
    return (n*.035 + glug*.14)*swell, (n*.032 + glug*.15)*swell

def wind(t, i):
    n = random.uniform(-1,1)
    slow = .5+.5*math.sin(2*math.pi*.045*t)
    tone = .08*math.sin(2*math.pi*37*t)+.035*math.sin(2*math.pi*73*t)
    return n*.09*slow+tone, n*.08*(1-slow*.25)+tone*.9

def ui(t, i):
    # Soft original electronic confirmation pulse, designed as a loop-safe bed.
    env = math.exp(-((t-1.0)/.16)**2)+.65*math.exp(-((t-2.2)/.20)**2)
    tone = math.sin(2*math.pi*880*t)+.35*math.sin(2*math.pi*1320*t)
    return .13*env*tone, .12*env*math.sin(2*math.pi*884*t+.1)

sounds = {
    "machine_motor_loop": (6.0, motor),
    "drone_rotors_loop": (6.0, drone),
    "train_wheel_rail_loop": (6.0, train),
    "conveyor_belt_loop": (6.0, conveyor),
    "fluid_pump_loop": (6.0, pump),
    "pipeline_flow_loop": (6.0, fluid),
    "alien_planet_wind_loop": (8.0, wind),
    "soft_ui_confirmation": (3.0, ui),
}
for name, (duration, fn) in sounds.items():
    write_wav(name, duration, fn)
    print("Generated stereo WAV:", name)

manifest = {
  "format": "WAV PCM, 48000 Hz, 16-bit, stereo",
  "provenance": "Original procedural synthesis; no Satisfactory game audio sampled or copied.",
  "playback": {
    "spatial_mode": "3D positional source with stereo output",
    "stereo_note": "The game audio mixer should preserve stereo ambience but spatialize mono point emitters with HRTF/panning as supported.",
    "distance_model": "inverse",
    "default_rolloff": 1.0,
    "fade_when_far": "Smoothly attenuate to silence between min_distance and max_distance; do not hard-cut.",
    "occlusion": "Apply low-pass filtering and gain reduction when walls or terrain block line of sight.",
    "reverb": "Use zone-based send; factory interiors and open alien terrain use different impulse responses."
  },
  "events": [
    {"id":"machine_motor","file":"machine_motor_loop.wav","loop":True,"min_distance_m":3,"max_distance_m":42,"gain":0.55,"pitch_jitter":0.025,"source":"moving_machine_emitter"},
    {"id":"drone_rotors","file":"drone_rotors_loop.wav","loop":True,"min_distance_m":4,"max_distance_m":65,"gain":0.62,"pitch_jitter":0.04,"source":"drone_body"},
    {"id":"train_wheels","file":"train_wheel_rail_loop.wav","loop":True,"min_distance_m":8,"max_distance_m":120,"gain":0.7,"pitch_jitter":0.02,"source":"train_bogie"},
    {"id":"conveyor_belt","file":"conveyor_belt_loop.wav","loop":True,"min_distance_m":2,"max_distance_m":28,"gain":0.4,"pitch_jitter":0.015,"source":"conveyor_drive"},
    {"id":"fluid_pump","file":"fluid_pump_loop.wav","loop":True,"min_distance_m":3,"max_distance_m":36,"gain":0.45,"pitch_jitter":0.02,"source":"pump_motor"},
    {"id":"pipeline_flow","file":"pipeline_flow_loop.wav","loop":True,"min_distance_m":2,"max_distance_m":20,"gain":0.3,"pitch_jitter":0.01,"source":"pipe_segment"},
    {"id":"alien_wind","file":"alien_planet_wind_loop.wav","loop":True,"min_distance_m":0,"max_distance_m":180,"gain":0.3,"pitch_jitter":0.0,"source":"biome_ambience"},
    {"id":"ui_confirm","file":"soft_ui_confirmation.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.35,"pitch_jitter":0.0,"source":"ui"}
  ]
}
with open(os.path.join(OUT,"audio_manifest.json"),"w",encoding="utf-8") as f:
    json.dump(manifest,f,ensure_ascii=False,indent=2)
print("Wrote audio manifest with",len(manifest["events"]),"events.")
