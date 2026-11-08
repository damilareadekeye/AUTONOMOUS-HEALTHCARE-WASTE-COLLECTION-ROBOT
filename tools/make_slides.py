"""Build the presentation deck (python-pptx, Windows), then run tools\\animate_slides.ps1 to add animations.

    python tools\\make_slides.py <slides_dir>      # needs <slides_dir>\\img\\*.png and ..\\video\\hcw_demo_silent.mp4

Design: daylight-friendly. Three themes alternate: CREAM (cream background, black text, blue accent), BLUE (blueprint
grid, white text) and INK (near-black, cream text). Giant Impact headlines. Everything stays inside the slide.
Shapes named "aNN_<effect>" are animated by animate_slides.ps1 (wipe, fade, fly, zoom, wipeP = by paragraph).
Speaker notes: Presenter 1 = slides 1-3, Presenter 2 = slides 4-7, Presenter 3 = slides 8-11.
"""
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

D = sys.argv[1]
IMG = os.path.join(D, 'img')
VIDEO = os.path.join(os.path.dirname(D), 'video', 'hcw_demo_silent.mp4')
OUT = os.path.join(D, 'HCW_Presentation.pptx')


def rgb(h):
    return RGBColor(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


THEMES = {
    'cream': dict(bg='#F6F1E6', head='#111418', body='#1F2328', muted='#555A62', card='#FFFFFF', line='#D8D0BF',
                  accent='#1F4FD8', chip='#111418', chip_t='#F6F1E6', pill='#111418', pill_t='#F6F1E6', hi='#E6ECFF'),
    'ink': dict(bg='#111418', head='#F6F1E6', body='#E9E5DC', muted='#B5B0A4', card='#1D2229', line='#3A424D',
                accent='#6C95FF', chip='#F6F1E6', chip_t='#111418', pill='#F6F1E6', pill_t='#111418', hi='#26304A'),
    'blue': dict(bg='#0B3F96', head='#FFFFFF', body='#E6EEFF', muted='#BCD0F5', card='#0F55C4', line='#7FA8F2',
                 accent='#FFFFFF', chip='#FFFFFF', chip_t='#0B3F96', pill='#FFFFFF', pill_t='#0B3F96', hi='#1B63D6'),
}
T = dict(THEMES['cream'])
HEAD, BODY = 'Impact', 'Segoe UI'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
order = {'n': 0}


def C(key):
    return rgb(T[key])


def anim(shape, kind):
    order['n'] += 1
    shape.name = 'a%02d_%s' % (order['n'], kind)
    return shape


def rect(s, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE, line=None, lw=1.0, rot=0):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid()
        r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line
        r.line.width = Pt(lw)
    r.shadow.inherit = False
    r.rotation = rot
    return r


def text(s, x, y, w, h, content, size=18, color=None, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, space=0, ls=1.0):
    color = color or C('body')
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    items = content if isinstance(content, list) else [content]
    for i, it in enumerate(items):
        t, o = (it, {}) if isinstance(it, str) else it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = o.get('align', align)
        p.space_after = Pt(o.get('space', space))
        p.line_spacing = o.get('ls', ls)
        r = p.add_run()
        r.text = t
        r.font.name = o.get('font', font)
        r.font.size = Pt(o.get('size', size))
        r.font.bold = o.get('bold', bold)
        r.font.color.rgb = o.get('color', color)
    return tb


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body


def asterisk(s, x, y, size=0.8, color=None):
    color = color or C('accent')
    for ang in (0, 60, 120):
        rect(s, x - size / 2, y - size * 0.09, size, size * 0.18, color, MSO_SHAPE.ROUNDED_RECTANGLE, rot=ang).adjustments[0] = 0.5


def new_slide(theme):
    global T
    T = dict(THEMES[theme])
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 13.333, 7.5, C('bg'))
    if theme == 'blue':
        for i in range(1, 27):
            c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(i * 0.5), 0, Inches(i * 0.5), Inches(7.5))
            c.line.color.rgb, c.line.width = rgb('#2460C0'), Pt(0.5)
        for j in range(1, 15):
            c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, Inches(j * 0.5), Inches(13.333), Inches(j * 0.5))
            c.line.color.rgb, c.line.width = rgb('#2460C0'), Pt(0.5)
    asterisk(s, 12.3, 0.85, 0.8)
    return s


def tag(s, label):
    text(s, 0.7, 0.32, 8, 0.4, label, 14, C('accent') if T['bg'] != '#0B3F96' else C('muted'), BODY, True)


def title(s, lines, size=76, x=0.65, y=0.75, w=10.5):
    tb = text(s, x, y, w, size / 72 * len(lines) + 0.4, [(l, {}) for l in lines], size, C('head'), HEAD, ls=0.9)
    return anim(tb, 'wipeP')


def card(s, x, y, w, h, hi=False, radius=0.07):
    c = rect(s, x, y, w, h, C('hi') if hi else C('card'), MSO_SHAPE.ROUNDED_RECTANGLE, line=C('line'), lw=1.25)
    c.adjustments[0] = radius
    return c


def chip(s, n, x, y, size=0.55):
    rect(s, x, y, size, size, C('chip'))
    text(s, x, y, size, size, str(n) + '.', 22, C('chip_t'), HEAD, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def pill(s, label, x, y, w, h, size=15):
    p = rect(s, x, y, w, h, C('pill'), MSO_SHAPE.ROUNDED_RECTANGLE)
    p.adjustments[0] = 0.5
    text(s, x, y, w, h, label, size, C('pill_t'), BODY, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    return p


def picture(s, name, x, y, w=None, h=None):
    kw = {}
    if w:
        kw['width'] = Inches(w)
    if h:
        kw['height'] = Inches(h)
    p = s.shapes.add_picture(os.path.join(IMG, name), Inches(x), Inches(y), **kw)
    p.line.color.rgb, p.line.width = C('head'), Pt(2.5)
    return p


# ============================================================ 1 title (cream)
s = new_slide('cream')
text(s, 0.7, 0.32, 8, 0.4, 'IEEE RWANDA MENTORSHIP PROGRAM', 14, C('accent'), BODY, True)
anim(text(s, 0.7, 0.9, 6, 0.8, 'AUTONOMOUS', 40, C('accent'), HEAD), 'wipe')
anim(text(s, 0.65, 1.45, 7.9, 3.8, [('HEALTHCARE', {'size': 92}), ('WASTE', {'size': 92}), ('COLLECTION ROBOT', {'size': 54})], 90, C('head'), HEAD, ls=0.88), 'wipeP')
anim(text(s, 0.7, 5.3, 7.9, 0.4, 'Finds, checks and delivers hazardous-waste containers, in simulation.', 15, C('body')), 'fade')
anim(text(s, 0.7, 5.95, 3, 0.4, 'PRESENTED BY:', 18, C('head'), HEAD), 'fade')
anim(text(s, 0.7, 6.3, 8.2, 0.4, 'Damilare Lekan Adekeye   |   David Parsley Kakhayanga   |   Beni Bonheur Karangwa', 15, C('body')), 'fade')
anim(text(s, 0.7, 6.7, 6, 0.4, 'MENTOR: Miracle James', 15, C('accent'), BODY, True), 'fade')
rect(s, 8.95, 1.85, 3.9, 2.55, C('accent'))
anim(picture(s, 'bay.png', 8.6, 1.5, w=3.9), 'fly')
notes(s, "PRESENTER 1 (slides 1 to 3)\n\n"
         "Good day everyone. We are Damilare, David and Beni, and our mentor is Miracle James. "
         "Our project is an autonomous healthcare-waste collection robot. In the next few minutes we will show you the problems it helps with, "
         "what it does, how it works, what we measured, and where we want to take it next.\n\n"
         "Tip: say clearly that the demo is a simulation of the robot in a clinic.")

# ============================================================ 2 problems (cream)
s = new_slide('cream')
tag(s, '01  /  WHY WE BUILT IT')
title(s, ['PROBLEMS', 'WE SOLVE'], 76)
probs = [('RISKY HANDLING', 'Infectious and sharp waste can harm anyone who carries it by hand.', 'carries the waste, so people do not have to'),
         ('WRONG CONTAINER', 'Taking or mixing up the wrong container is a safety incident.', 'reads the tag and refuses if it is wrong or missing'),
         ('NO CLEAR RECORD', 'Manual notes depend on people remembering to write things down.', 'logs every task: time, place, result and cause of any stop'),
         ('TIRING, REPEATED WORK', 'Same rooms, same walk, many times a day. Tired people make mistakes.', 'drives the same route the same way, every time')]
for i, (h, p, f) in enumerate(probs):
    x = 0.65 + i * 3.1
    anim(card(s, x, 3.05, 2.9, 3.9), 'fade')
    chip(s, i + 1, x + 0.25, 3.25)
    text(s, x + 0.2, 3.95, 2.55, 0.8, h, 22, C('head'), HEAD, ls=0.95)
    text(s, x + 0.2, 4.65, 2.55, 1.0, p, 14, C('body'))
    rect(s, x + 0.25, 5.6, 2.4, 0.04, C('accent'))
    text(s, x + 0.2, 5.68, 2.55, 0.3, 'OUR ROBOT', 12, C('accent'), BODY, True)
    text(s, x + 0.2, 5.95, 2.55, 0.95, f, 14, C('head'), BODY, True)
notes(s, "We started from real problems in how healthcare waste is handled. Four of them.\n\n"
         "One, risky handling: infectious and sharp waste can harm anyone who carries it by hand. The robot carries it so people do not have to.\n"
         "Two, wrong container: taking or mixing up the wrong container is a safety incident. The robot reads a tag on the container and refuses if it is wrong or missing.\n"
         "Three, no clear record: manual notes depend on people remembering. Our robot logs every task, with time, place, result, and the cause of any stop.\n"
         "Four, tiring repeated work: the same rooms and the same walk many times a day. The robot drives the same route the same way every time.")

# ============================================================ 3 solution (ink)
s = new_slide('ink')
tag(s, '02  /  OUR SOLUTION')
title(s, ['COLLECT.  CHECK.', 'DELIVER.'], 76, w=11.5)
flow = [('REQUEST', 'A staff member asks for room A, B or C.'), ('COLLECT', 'The robot drives to that room on its own.'),
        ('CHECK', 'It reads the container tag. Wrong or missing: it refuses.'), ('DELIVER', 'It picks the container up and carries it to the storage bay.'),
        ('REPORT', 'It reports the result, then drives home.')]
for i, (h, b) in enumerate(flow):
    x = 0.65 + i * 2.48
    anim(card(s, x, 3.2, 2.3, 2.65, hi=(i == 2)), 'fade')
    chip(s, i + 1, x + 0.2, 3.4, 0.5)
    text(s, x + 0.2, 4.05, 2.0, 0.5, h, 26, C('head'), HEAD)
    text(s, x + 0.2, 4.6, 1.95, 1.2, b, 14, C('body'))
pill(s, 'SAFETY FIRST: ANY DOUBT, NO PICK-UP, STRAIGHT HOME', 0.65, 6.2, 7.3, 0.62, 16)
text(s, 8.3, 6.2, 4.4, 0.62, 'Same flow for rooms A, B and C.', 16, C('muted'), BODY, True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "Here is what the robot does, from one request. Request: a staff member asks for room A, B or C. Collect: the robot drives to that room on its own. "
         "Check: it reads the tag on the container with its camera. If the tag is right, it picks the container up with a magnet, which is simulated. "
         "Deliver: it carries the container to the hazardous-waste storage bay. Report: it reports the result and drives home.\n\n"
         "The most important rule is the check. If anything is wrong, the robot does not pick up and goes straight home.\n\n"
         "Now my colleague will explain how it works.")

# ============================================================ 4 how it works (blue)
s = new_slide('blue')
tag(s, '03  /  UNDER THE HOOD')
title(s, ['HOW IT', 'WORKS'], 76)
pill(s, 'REQUEST: ROOM A, B OR C', 5.6, 1.05, 4.3, 0.7, 18)
blocks = [('TASK MANAGER', 'The brain. Runs the 7 steps in order, decides when to stop, and logs every task.'),
          ('NAVIGATION', 'Nav2 plans the path. A map from SLAM and AMCL tell the robot where it is.'),
          ('PERCEPTION', 'Camera + AprilTag. The expected tag must be seen in 5 frames in a row, and no other tag.'),
          ('SIMULATED MAGNET', 'Attaches the container to the robot and releases it at the storage bay.')]
for i, (h, b) in enumerate(blocks):
    x = 0.65 + i * 3.1
    anim(card(s, x, 3.05, 2.9, 2.8, radius=0.06), 'fade')
    chip(s, i + 1, x + 0.22, 3.25, 0.5)
    text(s, x + 0.2, 3.9, 2.55, 0.5, h, 22, C('head'), HEAD)
    text(s, x + 0.2, 4.45, 2.55, 1.4, b, 14, C('body'))
bar = rect(s, 0.65, 6.2, 12.0, 0.7, C('pill'), MSO_SHAPE.ROUNDED_RECTANGLE)
bar.adjustments[0] = 0.5
anim(bar, 'fade')
text(s, 0.65, 6.2, 12.0, 0.7, 'ALL ON ROS 2 JAZZY   |   TURTLEBOT 4 IN A GAZEBO CLINIC   |   CAMERA + LIDAR', 17, C('pill_t'), BODY, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
notes(s, "PRESENTER 2 (slides 4 to 7)\n\n"
         "Inside, there are four building blocks. The task manager is the brain: it runs the seven steps in order, decides when to stop, and logs every task.\n"
         "Navigation uses Nav2. The robot has a map of the clinic, built with SLAM, and it works out where it is on that map.\n"
         "Perception uses a camera and AprilTag markers. A container only counts as verified when the expected tag is seen in five camera frames in a row, "
         "and no other tag is seen. That avoids one-frame mistakes.\n"
         "The magnet is simulated: in the simulator the container is attached to the robot and released at the bay.\n\n"
         "All of it runs on ROS 2 Jazzy, with a TurtleBot 4 robot in a Gazebo clinic.")

# ============================================================ 5 one task (cream)
s = new_slide('cream')
tag(s, '04  /  ONE TASK')
title(s, ['STEP BY STEP'], 76)
steps = ['Drive to the collection room', 'Verify the container tag', 'Attach with the magnet', 'Carry to the storage bay',
         'Release at storage', 'Report completion', 'Drive back home']
for i, t in enumerate(steps):
    y = 2.0 + i * 0.7
    anim(card(s, 0.65, y, 5.6, 0.58, hi=(i == 1), radius=0.25), 'fade')
    chip(s, i + 1, 0.65, y, 0.58)
    text(s, 1.4, y, 4.8, 0.58, t, 17, C('head'), BODY, i == 1, anchor=MSO_ANCHOR.MIDDLE)
picture(s, 'panel_done.png', 6.75, 1.95, w=3.0)
picture(s, 'panel_refusal.png', 9.95, 1.95, w=3.0)
text(s, 6.75, 5.3, 3.0, 0.6, 'A normal task: every step ticked, green result', 13, C('muted'), align=PP_ALIGN.CENTER)
text(s, 9.95, 5.3, 3.0, 0.6, 'A wrong container: red stop at the check', 13, C('muted'), align=PP_ALIGN.CENTER)
pill(s, 'STEP 2 IS THE SAFETY GATE', 6.75, 5.95, 6.2, 0.55, 16)
text(s, 6.75, 6.55, 6.2, 0.6, 'Wrong tag, no tag or an unstable tag: no pick-up. The robot goes home and logs the cause.', 14, C('body'))
notes(s, "This is one complete task, in seven steps. Drive to the room, verify the tag, attach with the magnet, carry to the storage bay, release, report, and drive home.\n\n"
         "On the right is the status panel you will see in the video. The left screenshot is a normal task: all steps ticked and a green result. "
         "The right screenshot is a failure: the camera saw tag 13 but tag 12 was expected, so the robot stopped at the check, picked nothing up, and went home.\n\n"
         "Step two is the safety gate for the whole project.")

# ============================================================ 6 world (blue)
s = new_slide('blue')
tag(s, '05  /  THE WORLD')
title(s, ['THE CLINIC'], 76)
anim(picture(s, 'map.png', 0.65, 2.0, h=4.25), 'fly')
text(s, 0.65, 6.32, 4.6, 0.7, 'Clinic ground floor map with the named places: Home, A, B, C and Storage.', 12, C('muted'))
anim(picture(s, 'bay.png', 5.6, 2.0, w=4.25), 'fly')
text(s, 5.6, 4.9, 4.25, 0.4, 'The hazardous-waste storage bay', 13, C('muted'))
pts = [('ROOMS A, B, C', 'Each has a colour-coded container with its own tag: blue, green, orange.'),
       ('STORAGE BAY', 'Hazard-striped floor, shelves, signs and bins: it looks like a hazardous-waste store.'),
       ('HOSPITAL LOOK', 'Beds, desks and furniture, kept simple so the simulation stays fast.')]
for i, (h, b) in enumerate(pts):
    y = 2.0 + i * 1.6
    anim(card(s, 10.05, y, 2.75, 1.5), 'fade')
    text(s, 10.15, y + 0.06, 2.55, 0.4, h, 18, C('head'), HEAD)
    text(s, 10.15, y + 0.48, 2.55, 1.0, b, 12, C('body'))
notes(s, "The world is the ground floor of a clinic. This map was built by the robot itself using SLAM, and we marked the named places on it: Home, the three collection rooms, and Storage.\n\n"
         "Each collection room has a container with a different colour and its own tag: blue for A, green for B, orange for C.\n\n"
         "The storage area is dressed as a hazardous-waste store, with hazard stripes on the floor, shelves, signs and bins.\n\n"
         "The rooms have beds and desks so it looks like a hospital, but we kept the objects simple so the simulation stays fast.")

# ============================================================ 7 video (ink)
s = new_slide('ink')
tag(s, '06  /  DEMO')
title(s, ['SEE IT RUN'], 60, y=0.7, w=8)
s.shapes.add_movie(VIDEO, Inches(2.2), Inches(1.7), Inches(8.9), Inches(5.0), poster_frame_image=os.path.join(IMG, 'verify_A.png'), mime_type='video/mp4')
text(s, 1.6, 6.8, 10.1, 0.4, 'A normal task at room A, then a wrong container at room B. Silent video, 2 min 40 s.', 13, C('muted'), align=PP_ALIGN.CENTER)
notes(s, "We will now play the demo video. It has no sound, so we will explain while it plays.\n\n"
         "First, a normal task at room A: the robot drives there, checks the tag, picks the container up, and carries it to the hazardous-waste bay. "
         "Parts of the video are sped up, and the speed is shown in the corner.\n\n"
         "Then a failure: a wrong container is placed at room B. Watch the panel on the right. The camera sees tag 13, but tag 12 is expected, "
         "and the robot refuses and goes home.\n\n"
         "If the video does not play, say so and move on; the screenshots on slide 5 show the same two cases.")

# ============================================================ 8 results (cream)
s = new_slide('cream')
tag(s, '07  /  RESULTS IN SIMULATION')
title(s, ['THE NUMBERS'], 60, y=0.7, w=9)
for i, (big, small, col) in enumerate([('67/67', 'NORMAL TASKS COMPLETED', C('head')), ('6/6', 'STAGED FAULTS REFUSED WITH THE CORRECT CAUSE', C('accent'))]):
    x = 0.65 + i * 6.2
    card(s, x, 1.85, 5.95, 2.95)
    anim(text(s, x, 1.95, 5.95, 1.9, big, 130, col, HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE), 'zoom')
    text(s, x + 0.2, 3.95, 5.55, 0.7, small, 17, C('head'), BODY, True, PP_ALIGN.CENTER)
card(s, 0.65, 5.05, 5.95, 1.95)
text(s, 0.95, 5.12, 5.4, 0.4, 'NORMAL TASKS BY ROOM', 20, C('head'), HEAD)
for i, (r, n, col) in enumerate([('Room A', 37, '#2E6BFF'), ('Room B', 15, '#1FA85A'), ('Room C', 15, '#F08A00')]):
    y = 5.6 + i * 0.45
    text(s, 0.95, y, 1.2, 0.4, r, 14, C('body'))
    rect(s, 2.1, y + 0.07, 3.3 * n / 37, 0.26, rgb(col), MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 2.15 + 3.3 * n / 37, y, 0.8, 0.4, str(n), 14, C('head'), BODY, True)
card(s, 6.85, 5.05, 5.95, 1.95)
text(s, 7.15, 5.12, 5.4, 0.4, 'WHAT IT SHOWS', 20, C('head'), HEAD)
text(s, 7.15, 5.6, 5.4, 1.35, 'The full chain works end to end: request, drive, check, carry, deliver, report. All the wrong or missing containers we staged were caught and refused.', 15, C('body'))
notes(s, "PRESENTER 3 (slides 8 to 11)\n\n"
         "Here are our results from the simulation. We logged 67 normal tasks and all 67 completed: 37 to room A, 15 to room B and 15 to room C.\n\n"
         "We also staged 6 faults, such as a wrong container or a missing container, and the robot refused all 6, with the correct cause written in the log.\n\n"
         "These are simulation results. They show the whole chain works from request to report, and that the safety check does its job. "
         "The next step is to run many more tasks and then test on real hardware.")

# ============================================================ 9 fixes (cream)
s = new_slide('cream')
tag(s, '08  /  HOW WE IMPROVED IT')
title(s, ['WHAT WE FIXED'], 60, y=0.7, w=10)
probs = [('SLOW TRIPS TO ROOM A', 'Some trips took 84 to 98 seconds. Logging the robot position showed it stopped 0.02 rad outside its turning tolerance and kept correcting.', 'We widened the heading tolerance from 0.10 to 0.15 rad. Trips to A then took about 39 seconds.'),
         ('SIMULATION TOO SLOW', 'With hundreds of models, the simulator ran at only 1 to 3 percent of real time.', 'We simplified the world and kept decoration to simple shapes. It now runs near real time.'),
         ('CONTAINER LEFT IN THE CORRIDOR', 'The first version released the container in the middle of a hallway. It looked wrong and unsafe.', 'We moved the drop point against the wall and built a marked hazardous-waste bay there.')]
for i, (h, p, f) in enumerate(probs):
    y = 1.85 + i * 1.7
    anim(card(s, 0.65, y, 12.05, 1.55), 'fade')
    chip(s, i + 1, 0.85, y + 0.5, 0.55)
    text(s, 1.65, y + 0.15, 2.7, 1.3, h, 22, C('head'), HEAD, anchor=MSO_ANCHOR.MIDDLE, ls=0.95)
    text(s, 4.55, y + 0.1, 4.0, 0.3, 'PROBLEM', 12, C('accent'), BODY, True)
    text(s, 4.55, y + 0.4, 4.05, 1.15, p, 13, C('body'))
    text(s, 8.8, y + 0.1, 3.8, 0.3, 'FIX', 12, C('accent'), BODY, True)
    text(s, 8.8, y + 0.4, 3.8, 1.15, f, 13, C('head'), BODY, True)
notes(s, "Of course, not everything worked at first. Three examples.\n\n"
         "One: trips to room A were sometimes very slow, 84 to 98 seconds. We recorded where the robot was when it stalled and found it was a tiny fraction of a radian outside its turning tolerance, so it kept correcting. "
         "We widened that tolerance a little, and trips to A went back to about 39 seconds.\n\n"
         "Two: the simulation ran at only one to three percent of real time because the world had too many objects. We simplified it.\n\n"
         "Three: the first version dropped the container in the middle of the hallway. We moved the drop point to the wall and built a proper marked storage bay.")

# ============================================================ 10 future ideas (blue)
s = new_slide('blue')
tag(s, '09  /  WHERE WE CAN TAKE IT')
title(s, ['FUTURE IDEAS'], 60, y=0.7, w=10)
ideas = [('REAL ROBOT', 'Run the same software on a real TurtleBot 4 with a real magnet or gripper.'),
         ('MORE TESTING', 'Run many more tasks, long shifts, and failures while carrying a container.'),
         ('REQUEST SCREEN', 'A simple screen or app so staff can ask for a collection in one tap.'),
         ('ALERTS AND DASHBOARD', 'Live status and a message to staff when a task is refused.'),
         ('MORE ROOMS, MORE FLOORS', 'Add rooms and floors, using lifts, as the clinic grows.'),
         ('A TEAM OF ROBOTS', 'Several robots sharing the work in a busy hospital.')]
for i, (h, b) in enumerate(ideas):
    x = 0.65 + (i % 3) * 4.1
    y = 1.9 + (i // 3) * 2.5
    anim(card(s, x, y, 3.9, 2.3), 'fade')
    chip(s, i + 1, x + 0.25, y + 0.2, 0.5)
    text(s, x + 0.25, y + 0.85, 3.45, 0.5, h, 22, C('head'), HEAD)
    text(s, x + 0.25, y + 1.35, 3.45, 0.9, b, 14, C('body'))
notes(s, "Here are ideas for how we could improve the project further. A real robot: the same software on a real TurtleBot 4 with a real magnet or gripper. "
         "More testing: many more tasks, long shifts, and failures while carrying. A request screen so staff can ask for a collection in one tap. "
         "Alerts and a dashboard. More rooms and floors. And in a bigger hospital, a team of robots sharing the work.")

# ============================================================ 11 thanks (ink)
s = new_slide('ink')
tag(s, 'IEEE RWANDA MENTORSHIP PROGRAM')
anim(text(s, 0.65, 1.2, 11.5, 2.2, 'THANK YOU', 130, C('head'), HEAD, ls=0.9), 'wipe')
anim(text(s, 0.7, 3.5, 8, 0.8, 'QUESTIONS?', 54, C('accent'), HEAD), 'fade')
anim(text(s, 0.7, 4.8, 9, 0.4, 'PRESENTED BY:', 18, C('head'), HEAD), 'fade')
anim(text(s, 0.7, 5.2, 11, 0.4, 'Damilare Lekan Adekeye   |   David Parsley Kakhayanga   |   Beni Bonheur Karangwa', 15, C('body')), 'fade')
anim(text(s, 0.7, 5.6, 8, 0.4, 'MENTOR: Miracle James', 15, C('muted'), BODY, True), 'fade')
anim(text(s, 0.7, 6.4, 11, 0.4, 'github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT', 14, C('accent')), 'fade')
notes(s, "Thank you for listening. We are happy to take your questions.\n\n"
         "Likely questions and short honest answers (for us only):\n"
         "- Is it a real robot? Not yet. We built and tested it in simulation, and the same software is designed to move to a real TurtleBot 4.\n"
         "- Where is the storage? It is a marked hazardous-waste bay in the corridor. A separate room would need a new section of the map and new tuning.\n"
         "- How do you know it picks the right container? It must see the expected tag in five frames in a row and no other tag.\n"
         "- Did you train a model? No. The robot is not machine-learned: it uses planning, a map and tag detection. The 67 tasks are test runs, not training data.\n"
         "- What if the robot moves to another place in the hospital? We update the map for that area (remapping) and the place coordinates, then re-test.")

# ---------------------------------------------------------------- safety check: nothing outside the slide
W, H = prs.slide_width, prs.slide_height
bad = []
for n, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.rotation:
            continue
        if sh.left < -10 or sh.top < -10 or sh.left + sh.width > W + 10 or sh.top + sh.height > H + 10:
            bad.append((n, sh.name, round(sh.left / 914400, 2), round(sh.top / 914400, 2), round(sh.width / 914400, 2), round(sh.height / 914400, 2)))
print('shapes outside the slide:', bad if bad else 'none')
prs.save(OUT)
print('saved', OUT)
