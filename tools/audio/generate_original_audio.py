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


def step(t, i):
    phase=t%0.62; env=math.exp(-((phase-.035)/.028)**2)
    noise=random.uniform(-1,1)*math.exp(-phase*24)
    thump=math.sin(2*math.pi*(72-24*phase)*t)*env
    pan=.5+.18*math.sin(2*math.pi*.7*t)
    return (thump*.24+noise*.045)*pan,(thump*.24+noise*.045)*(1-pan+.5)

def pickup(t, i):
    env=math.exp(-t*8); f=540+760*min(1,t/.35)
    tone=math.sin(2*math.pi*f*t)+.28*math.sin(2*math.pi*f*2.01*t)
    return .18*env*tone,.17*env*math.sin(2*math.pi*(f+5)*t)

def place(t, i):
    env=math.exp(-t*7); thud=math.sin(2*math.pi*68*t)*math.exp(-t*18)
    ping=math.sin(2*math.pi*620*t)*math.exp(-((t-.12)/.10)**2)
    return .22*thud+.10*ping,.21*thud+.11*ping

def dismantle(t, i):
    env=math.exp(-t*2.5); sweep=math.sin(2*math.pi*(780-390*t)*t)
    grit=random.uniform(-1,1)*math.exp(-t*3)
    return .10*env*sweep+.035*grit,.095*env*sweep-.03*grit

def ui_cancel(t, i):
    env=math.exp(-t*13); tone=math.sin(2*math.pi*330*t)
    return .12*env*tone,.12*env*math.sin(2*math.pi*327*t)

def ui_error(t, i):
    env=math.exp(-t*5); tone=math.sin(2*math.pi*245*t)+.45*math.sin(2*math.pi*311*t)
    pulse=.5+.5*math.sin(2*math.pi*4*t)
    return .13*env*tone*pulse,.13*env*tone*pulse

def ui_open(t, i):
    env=math.exp(-t*7); f=360+440*min(1,t/.32)
    return .10*env*math.sin(2*math.pi*f*t),.10*env*math.sin(2*math.pi*(f+8)*t)

def power_switch(t, i):
    click=math.exp(-((t-.035)/.018)**2)*.45
    hum=math.sin(2*math.pi*100*t)*(.5+.5*math.tanh((t-.10)*20))
    return click+hum*.12,click*.92+hum*.11

def scan(t, i):
    pulse=math.exp(-((t%1.1)-.08)**2/.006)
    tone=math.sin(2*math.pi*(480+220*(t%1.1))*t)
    return .18*pulse*tone,.16*pulse*math.sin(2*math.pi*(tone*0+480+220*(t%1.1))*t)

def jump(t, i):
    env=math.sin(math.pi*min(1,t/.75))**1.5
    noise=random.uniform(-1,1)*.06
    whoosh=math.sin(2*math.pi*(180+420*t)*t)*.10
    return env*(whoosh+noise),env*(whoosh-noise*.7)

def land(t, i):
    env=math.exp(-t*9); low=math.sin(2*math.pi*54*t)*math.exp(-t*12)
    grit=random.uniform(-1,1)*math.exp(-t*20)
    return .28*env*low+.05*grit,.27*env*low-.04*grit

def water(t, i):
    n=random.uniform(-1,1); swell=.45+.55*(.5+.5*math.sin(2*math.pi*.11*t))
    ripple=math.sin(2*math.pi*(2.8+math.sin(t*.4))*t)**7
    return swell*(n*.045+ripple*.09),swell*(n*.04+ripple*.10)

def cave(t, i):
    n=random.uniform(-1,1); drone=.07*math.sin(2*math.pi*31*t)+.035*math.sin(2*math.pi*47*t)
    drip=math.exp(-((t%2.7)-.2)**2/.004)*.2*math.sin(2*math.pi*840*t)
    return n*.035+drone+drip,n*.032+drone*.9+drip*.8

def rain(t, i):
    n=random.uniform(-1,1); pat=(.5+.5*math.sin(2*math.pi*.17*t))
    hiss=n*.055*pat
    drops=math.exp(-((t*7.3)%1-.5)**2/.002)*.12
    return hiss+drops,hiss*.96+drops*.85

def creature(t, i):
    env=math.exp(-((t-0.48)/.28)**2)+.65*math.exp(-((t-1.35)/.22)**2)
    f=620+180*math.sin(2*math.pi*.7*t)
    chirp=math.sin(2*math.pi*f*t)+.35*math.sin(2*math.pi*f*1.51*t)
    return .12*env*chirp,.11*env*math.sin(2*math.pi*(f+12)*t)

def miner(t, i):
    pulse=.7+.3*math.sin(2*math.pi*.6*t)
    body=.18*math.sin(2*math.pi*52*t)+.09*math.sin(2*math.pi*104*t)
    rattle=.07*math.sin(2*math.pi*420*t)*(.5+.5*math.sin(2*math.pi*4*t))
    return (body+rattle)*pulse,(body*.94+rattle*.9)*pulse

def smelter(t, i):
    rumble=.16*math.sin(2*math.pi*44*t)+.08*math.sin(2*math.pi*88*t)
    flame=.07*math.sin(2*math.pi*(120+8*math.sin(t*2))*t)
    crackle=random.uniform(-1,1)*.025
    return rumble+flame+crackle,rumble*.95+flame*.9-crackle*.4

def refinery(t, i):
    motor=.14*math.sin(2*math.pi*61*t)+.07*math.sin(2*math.pi*122*t)
    hiss=random.uniform(-1,1)*.035
    valve=math.sin(2*math.pi*1.1*t)**8*.09
    return motor+hiss+valve,motor*.96-hiss*.7+valve

def generator(t, i):
    hum=.20*math.sin(2*math.pi*50*t)+.08*math.sin(2*math.pi*100*t)
    fan=.06*math.sin(2*math.pi*17*t)*math.sin(2*math.pi*370*t)
    return hum+fan,hum*.97+fan*.9

def reactor(t, i):
    hum=.13*math.sin(2*math.pi*38*t)+.08*math.sin(2*math.pi*76*t)
    pulse=.035*math.sin(2*math.pi*.25*t)*math.sin(2*math.pi*620*t)
    return hum+pulse,hum*.96+pulse*.9

sounds = {
    "machine_motor_loop": (6.0, motor),
    "drone_rotors_loop": (6.0, drone),
    "train_wheel_rail_loop": (6.0, train),
    "conveyor_belt_loop": (6.0, conveyor),
    "fluid_pump_loop": (6.0, pump),
    "pipeline_flow_loop": (6.0, fluid),
    "alien_planet_wind_loop": (8.0, wind),
    "soft_ui_confirmation": (3.0, ui),
    "footsteps_surface_loop": (6.0, step),
    "item_pickup": (0.55, pickup),
    "building_placed": (0.65, place),
    "building_dismantled": (1.8, dismantle),
    "ui_cancel": (0.45, ui_cancel),
    "ui_error": (0.8, ui_error),
    "ui_open": (0.65, ui_open),
    "power_switch": (0.8, power_switch),
    "resource_scanner_ping": (2.2, scan),
    "player_jump": (0.85, jump),
    "player_landing": (0.7, land),
    "waterfall_ambience_loop": (8.0, water),
    "cave_ambience_loop": (8.0, cave),
    "rain_ambience_loop": (8.0, rain),
    "alien_creature_chirp": (2.2, creature),
    "portable_miner_loop": (6.0, miner),
    "smelter_loop": (6.0, smelter),
    "refinery_loop": (6.0, refinery),
    "power_generator_loop": (6.0, generator),
    "nuclear_reactor_loop": (6.0, reactor),
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
    ,{"id":"footsteps_surface","file":"footsteps_surface_loop.wav","loop":True,"min_distance_m":0,"max_distance_m":5,"gain":0.45,"pitch_jitter":0.02,"source":"player"}
    ,{"id":"item_pickup","file":"item_pickup.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.4,"pitch_jitter":0.0,"source":"ui"}
    ,{"id":"building_placed","file":"building_placed.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.5,"pitch_jitter":0.0,"source":"building"}
    ,{"id":"building_dismantled","file":"building_dismantled.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.4,"pitch_jitter":0.0,"source":"building"}
    ,{"id":"ui_cancel","file":"ui_cancel.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.35,"pitch_jitter":0.0,"source":"ui"}
    ,{"id":"ui_error","file":"ui_error.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.35,"pitch_jitter":0.0,"source":"ui"}
    ,{"id":"ui_open","file":"ui_open.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.35,"pitch_jitter":0.0,"source":"ui"}
    ,{"id":"power_switch","file":"power_switch.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.45,"pitch_jitter":0.0,"source":"power_switch"}
    ,{"id":"resource_scanner_ping","file":"resource_scanner_ping.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.5,"pitch_jitter":0.0,"source":"scanner"}
    ,{"id":"player_jump","file":"player_jump.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.45,"pitch_jitter":0.0,"source":"player"}
    ,{"id":"player_landing","file":"player_landing.wav","loop":False,"min_distance_m":0,"max_distance_m":0,"gain":0.5,"pitch_jitter":0.0,"source":"player"}
    ,{"id":"waterfall_ambience","file":"waterfall_ambience_loop.wav","loop":True,"min_distance_m":4,"max_distance_m":100,"gain":0.35,"pitch_jitter":0.0,"source":"waterfall"}
    ,{"id":"cave_ambience","file":"cave_ambience_loop.wav","loop":True,"min_distance_m":0,"max_distance_m":80,"gain":0.3,"pitch_jitter":0.0,"source":"biome_ambience"}
    ,{"id":"rain_ambience","file":"rain_ambience_loop.wav","loop":True,"min_distance_m":0,"max_distance_m":140,"gain":0.3,"pitch_jitter":0.0,"source":"weather"}
    ,{"id":"alien_creature_chirp","file":"alien_creature_chirp.wav","loop":False,"min_distance_m":5,"max_distance_m":45,"gain":0.3,"pitch_jitter":0.03,"source":"creature"}
    ,{"id":"portable_miner","file":"portable_miner_loop.wav","loop":True,"min_distance_m":2,"max_distance_m":24,"gain":0.48,"pitch_jitter":0.02,"source":"portable_miner"}
    ,{"id":"smelter","file":"smelter_loop.wav","loop":True,"min_distance_m":3,"max_distance_m":38,"gain":0.48,"pitch_jitter":0.02,"source":"smelter"}
    ,{"id":"refinery","file":"refinery_loop.wav","loop":True,"min_distance_m":4,"max_distance_m":48,"gain":0.5,"pitch_jitter":0.02,"source":"refinery"}
    ,{"id":"power_generator","file":"power_generator_loop.wav","loop":True,"min_distance_m":3,"max_distance_m":45,"gain":0.5,"pitch_jitter":0.015,"source":"generator"}
    ,{"id":"nuclear_reactor","file":"nuclear_reactor_loop.wav","loop":True,"min_distance_m":5,"max_distance_m":65,"gain":0.4,"pitch_jitter":0.01,"source":"reactor"}
  ]
}
with open(os.path.join(OUT,"audio_manifest.json"),"w",encoding="utf-8") as f:
    json.dump(manifest,f,ensure_ascii=False,indent=2)
print("Wrote audio manifest with",len(manifest["events"]),"events.")
