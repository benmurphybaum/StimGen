StimGen

StimGen is a python GUI for designing arbitrary visual stimuli (PsychoPy). It currently supports multiple stimulus objects, including spots, rectangles, gratings, annuli, rings, and snakes (rectangles expanding in the direction of motion), as well as some initial support for Motion Clouds (Ravello et al., 2019). Circular and rectangular masks/windows are also supported. 

Sequences:
All stimulus variables can accept 'sequences', in which a variable has a different value for each subsequent presentation. i.e. if you want to present a moving spot 8 times, in 8 different directions, you could assign the sequence '0,45,90,135,180,225,270,315' to the 'Angle' variable. 

Trajectories:
Moving objects can be defined in single linear trajectories or by arbitrary nonlinear trajectories. i.e. if I want a spot to change direction in the middle of a 2 second presentation, I could define a trajectory of 1 second at 0°, followed by 1 second at 90°. 

Triggers:
Supports input/output triggers through a parallel port. Some personal coding to define triggers is usually necessary.

Gamma Correction:
Comes with linear and gamma-2.2 tables that can be applied to the presentation monitor. Custom tables can also be loaded. 
