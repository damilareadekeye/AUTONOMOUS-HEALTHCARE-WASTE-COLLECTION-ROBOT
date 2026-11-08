"""On-screen status panel for the demo video (Windows, tkinter, no extra packages).

    python tools\\demo_panel.py [--geometry 640x1032+1280+0] [--file C:\\path\\hcw_status.json]

Shows the task manager's real state in plain words: the 8 steps with the current one highlighted, the tag-verification
progress, and a red banner when a task fails. Fed by scripts/demo_status_feed.py (which runs in Ubuntu).
White background, simulation only.
"""
import json
import os
import sys
import time
import tkinter as tk

FILE = os.path.expandvars(r'%LOCALAPPDATA%\Temp\hcw_status.json')
GEOMETRY = '640x1032+1280+0'
for i, a in enumerate(sys.argv):
    if a == '--geometry':
        GEOMETRY = sys.argv[i + 1]
    if a == '--file':
        FILE = sys.argv[i + 1]

STEPS = [
    ('NAVIGATE_TO_POINT', 'Drive to the collection room'),
    ('VERIFY', 'Verify the container tag'),
    ('ATTACH', 'Attach with the magnet'),
    ('NAVIGATE_TO_STORAGE', 'Carry to the storage bay'),
    ('RELEASE', 'Release at storage'),
    ('REPORT', 'Report completion'),
    ('RETURN_HOME', 'Drive back home'),
]
ROOM = {'A': 'room A (blue)', 'B': 'room B (green)', 'C': 'room C (orange)'}
BG, INK, GREY = '#ffffff', '#1d2733', '#9aa5b1'
GREEN, ORANGE, RED, BLUE = '#1f9d55', '#e8890c', '#d64545', '#2a6fdb'

root = tk.Tk()
root.title('Task status')
root.geometry(GEOMETRY)
root.configure(bg=BG)
root.attributes('-topmost', True)
root.overrideredirect(True)

def label(text, size, color=INK, bold=False, pady=(0, 0), anchor='w'):
    l = tk.Label(root, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'), bg=BG, fg=color,
                 anchor=anchor, justify='left', wraplength=590)
    l.pack(fill='x', padx=26, pady=pady)
    return l

label('Autonomous Healthcare-Waste Robot', 21, INK, True, (24, 0))
label('Simulation: ROS 2, Gazebo, Nav2, AprilTag', 12, GREY, False, (0, 14))
task = label('Waiting for a task', 20, BLUE, True, (0, 6))
banner = tk.Label(root, text='', font=('Segoe UI', 13, 'bold'), bg=BG, fg='white', anchor='w', justify='left', wraplength=580, padx=12, pady=8)
banner.pack(fill='x', padx=26, pady=(0, 8))
rows = []
for key, text in STEPS:
    r = tk.Label(root, text='', font=('Segoe UI', 15), bg=BG, fg=GREY, anchor='w', padx=14, pady=7)
    r.pack(fill='x', padx=26, pady=2)
    rows.append((key, text, r))
detail = label('', 12, INK, False, (14, 0))
label('', 6)
tk.Label(root, text='Simulation only. The magnet is simulated.', font=('Segoe UI', 10), bg=BG, fg=GREY).pack(side='bottom', pady=12)

def refresh():
    try:
        with open(FILE) as f:
            d = json.load(f)
    except (OSError, ValueError):
        root.after(300, refresh)
        return
    state, point = d.get('state', 'IDLE'), d.get('point', '')
    outcome, reached = d.get('outcome', ''), d.get('reached', '')
    keys = [k for k, _, _ in rows]
    if state in ('IDLE', '') and not outcome:
        task.config(text='Waiting for a task', fg=BLUE)
        banner.config(text='', bg=BG)
        for _, text, r in rows:
            r.config(text='   ' + text, fg=GREY, bg=BG, font=('Segoe UI', 15))
        detail.config(text='')
        root.after(250, refresh)
        return
    task.config(text='Task: collect from ' + ROOM.get(point, 'a room'), fg=BLUE)
    cur = keys.index(state) if state in keys else (keys.index(reached) if reached in keys else 0)
    failed = outcome == 'failed'
    if failed:
        cause = d.get('fail_cause') or 'stopped'
        banner.config(text='REFUSED, SAFE STOP: ' + cause, bg=RED)
        mark = keys.index(reached) if reached in keys else 1   # the step where it stopped
    elif outcome == 'completed':
        banner.config(text='TASK COMPLETED', bg=GREEN)
    else:
        banner.config(text='', bg=BG)
    finished = state == 'IDLE'
    for i, (k, text, r) in enumerate(rows):
        plain = dict(fg=GREY, bg=BG, font=('Segoe UI', 15))
        if failed:
            if i < mark:
                r.config(text='\u2713  ' + text, fg=GREEN, bg=BG, font=('Segoe UI', 15))
            elif i == mark:
                r.config(text='\u2717  ' + text, fg='white', bg=RED, font=('Segoe UI', 15, 'bold'))
            elif k == 'RETURN_HOME' and state == 'RETURN_HOME':
                r.config(text='\u25b6  ' + text, fg='white', bg=ORANGE, font=('Segoe UI', 15, 'bold'))
            elif k == 'RETURN_HOME' and finished:
                r.config(text='\u2713  ' + text, fg=GREEN, bg=BG, font=('Segoe UI', 15))
            else:
                r.config(text='   ' + text, **plain)
        elif finished or i < cur:
            r.config(text='\u2713  ' + text, fg=GREEN, bg=BG, font=('Segoe UI', 15))
        elif i == cur:
            r.config(text='\u25b6  ' + text, fg='white', bg=ORANGE, font=('Segoe UI', 15, 'bold'))
        else:
            r.config(text='   ' + text, **plain)
    exp = d.get('expected_id') or {'A': 11, 'B': 12, 'C': 13}.get(point, 0)
    if state == 'VERIFY':
        ids = d.get('detected_ids', [])
        if not ids:
            detail.config(text='Camera: no tag in view yet (looking for tag %s)' % exp)
        elif ids == [exp]:
            detail.config(text='Camera: tag %d seen, %d of 5 frames in a row' % (exp, min(5, d.get('consecutive', 0))))
        else:
            detail.config(text='Camera: tag %s seen, but tag %s is expected' % (', '.join(map(str, ids)), exp))
    elif failed:
        detail.config(text='Nothing was picked up. The robot returns home.' if mark <= 1 else 'The task was stopped. The robot returns home.')
    elif state == 'RETURN_HOME':
        detail.config(text='The container is in the storage bay. Returning home.')
    elif finished:
        detail.config(text='The container is in the storage bay. The robot is home.')
    else:
        detail.config(text='')
    root.after(250, refresh)

root.bind('<Escape>', lambda e: root.destroy())
refresh()
root.mainloop()
