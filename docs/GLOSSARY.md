# Glossary — Plain-Language Guide

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program

For anyone who has never used ROS and wants to understand what we're building and how it works.
Based only on the docs in this repository. Anything that is a guess rather than something the
docs confirm is marked "(check)".

## ROS 2

ROS 2 (Robot Operating System 2) is the software framework that lets different parts of the
robot's code talk to each other. It is not an operating system in the usual sense; it runs on
top of Ubuntu. Each piece of functionality (driving, navigation, camera processing) runs as a
separate program, called a node, and nodes send each other messages over named channels called
topics. This project uses ROS 2 Jazzy Jalisco, a long-term-support version.

## Gazebo

Gazebo is the simulator: a program that creates a 3D virtual world with realistic physics
(gravity, collisions) and simulates what a robot's sensors would see or measure in that world.
This project uses Gazebo Harmonic, the version that pairs with ROS 2 Jazzy. Instead of needing
a real robot and a real building, we run the robot's code against this virtual world.

## Simulation

Simulation means running the robot's whole system (its code, its movement, its sensors) inside
Gazebo instead of on a physical robot. It lets the team develop and test navigation, perception
and task logic without needing real hardware, a real hospital, or real waste containers. Our
first working version will be built entirely this way.

## TurtleBot 4

TurtleBot 4 is the robot model we use in simulation: a wheeled mobile robot with a camera and a
LiDAR sensor, driven by two wheels. It is not a robot we built ourselves; it comes as a ready-made
model and description used by Nav2's own official examples, which is part of why it was chosen
as the trusted starting point.

## LiDAR

LiDAR stands for Light Detection and Ranging. It is a sensor that spins and measures distances
to nearby objects in a full circle, which the robot uses to detect walls and obstacles around it.
Our TurtleBot 4's LiDAR publishes its readings on the `/scan` topic at about 10 times per second.

## Map

A map here is a saved 2D picture of the building's floor plan, built once and reused afterward.
It is stored as an image file (`.pgm`) plus a small settings file (`.yaml`) that says how the
image lines up with real-world coordinates. The robot uses this saved map to know where walls
and open corridors are when it navigates later.

## SLAM

SLAM stands for Simultaneous Localization and Mapping. It is the process of building a map of an
unknown space while also keeping track of where the robot is inside it, using the LiDAR as the
robot drives around. We use a tool called SLAM Toolbox to do this once, to produce the saved map
described above, before normal navigation begins.

## Localisation (AMCL)

Localisation means figuring out where the robot currently is on an already-known map. AMCL
(Adaptive Monte Carlo Localization) is the specific method used: it compares live LiDAR readings
against the saved map to estimate the robot's position and orientation, using many simulated
guesses ("particles") that narrow down over time. This is different from SLAM, which builds the
map; AMCL assumes the map already exists and only tracks the robot's position on it.

## Nav2

Nav2 is the navigation system that actually drives the robot from one point to another. Given a
destination, it plans a path, avoids obstacles along the way, and sends the wheel commands needed
to follow that path. In this project, Nav2 is the only part of the system allowed to move the
robot; no other part is allowed to send motor commands directly.

## AprilTag

An AprilTag is a small, printed black-and-white marker, similar in spirit to a QR code, that a
camera can reliably recognise and identify by a unique number. We attach a different tag to each
container (tag 11 for collection point A, 12 for B, 13 for C, and 14 as a deliberately wrong
container for testing), so the robot can confirm, using its camera, that it has found the correct
container before picking it up.

## Camera

The robot's camera is an RGB-D camera (meaning it captures a normal colour image plus depth
information) mounted on the TurtleBot 4. It is what the AprilTag detection system reads from
to recognise which container, if any, the robot is currently looking at.

## Task manager / state machine

The task manager is the part of the system that runs the overall job from start to finish: it
receives a request to collect a specific container, and coordinates Nav2, the camera verification
and the simulated magnet in the right order. It works as a state machine, meaning it is always in
exactly one named stage (such as "driving to the collection point" or "verifying the container")
and moves to the next stage only when that stage's condition is met.

## The magnet

The "magnet" is a simplified, simulated way of picking up and putting down a container. Rather
than building a real robotic gripper in Gazebo, which is slow to build and unreliable to get
working reliably, the container model is simply made to follow the robot once it is "attached",
and left behind once "released". In the demo, this is described to the audience as a magnetic
latch, even though in the simulation it is really just the container's position following the
robot's position.

## Real-time factor

The real-time factor is a number Gazebo reports that compares simulated time to actual clock
time. A real-time factor of 1.0 (or 100%) means the simulation is running exactly as fast as it
would in real life. A lower number, such as 0.03, means the simulation is running much slower
than real life, usually because the camera and LiDAR have too many detailed 3D models to render
at once. This is why the project uses a simplified, mostly-empty version of the hospital
building rather than the full, highly detailed one.

## How one task flows

1. The task manager starts idle, waiting for a request to collect container A, B or C.
2. When a request arrives, it asks Nav2 to drive the robot to that collection point.
3. At the collection point, it asks the perception system to check for the correct AprilTag.
4. If the right tag is seen clearly and consistently, the container counts as verified; if not,
   the robot waits briefly and tries again a few times before giving up.
5. Once verified, the simulated magnet "attaches" the container to the robot.
6. Nav2 then drives the robot to the storage point.
7. At storage, the magnet releases the container, and the task manager reports the task as
   completed.
8. The robot drives back home and returns to idle, ready for the next task; if anything fails
   along the way, it reports the failure and still returns home safely instead of continuing.
