"""Build the silent demo video from the two raw screen recordings (Windows, needs ffmpeg).

    python tools\\make_demo_video.py <raw_dir> <out.mp4> [work_dir]

raw_dir holds main_run_A.mkv and failure_B_wrong_container.mkv (each 1920x1032: Gazebo window on the left,
status panel on the right, see tools/demo_panel.py). The script cuts each recording into stages, speeds the boring
stages up, adds captions and a speed label, adds title/result cards, and joins everything into one 1920x1080 video
without sound. Change the SEGMENTS table to re-cut.
"""
import os
import subprocess
import sys

FFMPEG = r'C:\Users\Aorus15\ffmpeg-2025-02-24-git-6232f416b1-essentials_build\bin\ffmpeg.exe'
FONT = 'C\\:/Windows/Fonts/segoeui.ttf'
FONT_B = 'C\\:/Windows/Fonts/segoeuib.ttf'
INK, BLUE, GREY = '0x1d2733', '0x2a6fdb', '0x6b7785'

raw = sys.argv[1]
out = sys.argv[2]
work = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(out), 'work')
os.makedirs(work, exist_ok=True)

# (file, start s, end s, speed, caption)
SEGMENTS = [
    ('main_run_A.mkv', 15, 68, 3, 'Step 1: the robot drives to room A, planning its own path (Nav2)'),
    ('main_run_A.mkv', 62, 71, 1, 'Steps 2 and 3: it checks the container tag (5 frames in a row), then picks it up (simulated magnet)'),
    ('main_run_A.mkv', 71, 189, 5, 'Step 4: it carries the container to the hazardous-waste storage bay'),
    ('main_run_A.mkv', 189, 205, 1, 'Steps 5 and 6: it releases the container in the bay and reports completion'),
    ('main_run_A.mkv', 205, 270, 8, 'Step 7: it drives back to its home position'),
    ('failure_B_wrong_container.mkv', 15, 48, 3, 'The robot drives to room B. A wrong container (tag 13) was placed there'),
    ('failure_B_wrong_container.mkv', 48, 105, 2, 'It sees tag 13, but tag 12 is expected for room B'),
    ('failure_B_wrong_container.mkv', 105, 114, 1, 'Result: it refuses to pick the container up'),
    ('failure_B_wrong_container.mkv', 114, 143, 5, 'It drives home. Nothing was moved'),
]

CARDS = {
    'title': (6, [('Autonomous Healthcare-Waste Collection Robot', 64, FONT_B, INK, -60),
                  ('IEEE Rwanda Mentorship Program', 34, FONT, BLUE, 30),
                  ('Simulation demo: ROS 2 Jazzy, Gazebo, Nav2, AprilTag', 30, FONT, GREY, 100),
                  ('Team: Damilare Lekan Adekeye  |  David Parsley Kakhayanga  |  Beni Bonheur Karangwa', 30, FONT, INK, 240),
                  ('Mentor: Miracle James', 30, FONT, INK, 290)]),
    'demo1': (4, [('Demo 1: a normal task', 64, FONT_B, INK, 0),
                  ('Request: collect the waste container from room A', 34, FONT, BLUE, 95),
                  ('Waiting stages are sped up. The speed is shown in the corner.', 28, FONT, GREY, 170)]),
    'demo2': (4, [('Demo 2: a failure', 64, FONT_B, INK, 0),
                  ('A wrong container is placed at room B. The robot must refuse it.', 34, FONT, BLUE, 95)]),
    'results': (11, [('Results in simulation', 60, FONT_B, INK, 0),
                     ('67 of 67 normal tasks completed', 44, FONT_B, BLUE, 110),
                     ('room A: 37    room B: 15    room C: 15', 30, FONT, GREY, 175),
                     ('6 of 6 staged faults refused with the correct cause', 44, FONT_B, BLUE, 250),
                     ('Simulation only. The magnet is simulated.', 28, FONT, GREY, 345)]),
    'end': (6, [('Thank you', 64, FONT_B, INK, 0),
                ('github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT', 28, FONT, BLUE, 100)]),
}
ORDER = ['title', 'demo1', 0, 1, 2, 3, 4, 'demo2', 5, 6, 7, 8, 'results', 'end']


def run(args):
    r = subprocess.run([FFMPEG, '-y', '-loglevel', 'error'] + args, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        raise SystemExit('ffmpeg failed')


def textfile(name, text):
    p = os.path.join(work, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    return p.replace('\\', '/').replace(':', '\\:')


ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-an']


def make_card(key):
    dur, lines = CARDS[key]
    chain = []
    top = 380 - 40 * len(lines) // 2
    for i, (text, size, font, colour, dy) in enumerate(lines):
        tf = textfile('%s_%d.txt' % (key, i), text)
        chain.append("drawtext=fontfile='%s':textfile='%s':fontsize=%d:fontcolor=%s:x=(w-text_w)/2:y=%d"
                     % (font, tf, size, colour, top + 200 + dy - 120))
    vf = ','.join(chain)
    path = os.path.join(work, 'card_%s.mp4' % key)
    run(['-f', 'lavfi', '-i', 'color=c=white:s=1920x1080:r=30:d=%d' % dur, '-vf', vf] + ENC + [path])
    return path


def make_segment(i, seg):
    name, t0, t1, speed, caption = seg
    cap = textfile('cap%d.txt' % i, caption)
    spd = textfile('spd%d.txt' % i, 'real time' if speed == 1 else '%dx speed' % speed)
    graph = (
        "color=c=white:s=1920x1080:r=30[bg];"
        "[0:v]trim=start=%d:end=%d,setpts=(PTS-STARTPTS)/%d,fps=30,split[a][b];"
        "[a]crop=1226:920:40:110,scale=1280:960[sc];"
        "[b]crop=640:1032:1280:0[pn];"
        "[bg][sc]overlay=0:64:shortest=1[t];[t][pn]overlay=1280:24:shortest=1,"
        "drawtext=fontfile='%s':textfile='%s':fontsize=28:fontcolor=%s:box=1:boxcolor=white@0.88:boxborderw=12:x=24:y=84,"
        "drawtext=fontfile='%s':textfile='%s':fontsize=26:fontcolor=white:box=1:boxcolor=0xe8890c@0.95:boxborderw=10:x=24:y=1080-100"
        % (t0, t1, speed, FONT, cap, INK, FONT_B, spd))
    gp = os.path.join(work, 'graph%d.txt' % i)
    with open(gp, 'w', encoding='utf-8') as f:
        f.write(graph)
    path = os.path.join(work, 'seg%d.mp4' % i)
    run(['-i', os.path.join(raw, name), '-filter_complex_script', gp] + ENC + [path])
    return path


parts = []
for item in ORDER:
    if isinstance(item, str):
        parts.append(make_card(item))
    else:
        print('segment', item, SEGMENTS[item][4])
        parts.append(make_segment(item, SEGMENTS[item]))
lst = os.path.join(work, 'list.txt')
with open(lst, 'w') as f:
    for p in parts:
        f.write("file '%s'\n" % p.replace('\\', '/'))
run(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out])
print('wrote', out)
