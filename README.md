StimGen is python-based user interface for designing and presenting arbitrary visual stimuli through a projector or monitor. It uses the Qt and psychopy libraries to control the GUI and stimulus presentation, respectively. 

No coding by the user is required, barring some snags with specific setup configurations, especially for sending/receiving TTL triggers. 

Once set up, users can fully design the spatial and temporal properties of their visual stimulus, which can include an arbitrary number of independently controlled objects. Supported objects are circles, rectangles, gratings, plaids, snakes, motion clouds, windmills, concentric rings, white noise, and natural images.

Users can design stimuli in sequences, such that single or multiple stimulus parameters can change for each subsequent stimulation (i.e. increasing spot diameter, different directions of motion, etc.).

Stimuli can be saved in a 'stimulus bank' so that they can be reused from session to session. 

--------------------
In addition to the stimulus log, the full parameter set of the most recent stimulus is saved as currentStimulus.h5, which gets overwritten for each stimulus presentation. 
This file can be picked up by a different program and saved elsewhere. Use case: I pick up the currentStimulus.h5 file using electrophysiology acquisition software at the end of an acquisition sweep.
The stimulus information then gets saved into the same .h5 file that holds the acquired data, so I always have a record of what stimulus was presented.

--------------------
Install as a conda environment using the included environment file: environment.yml

conda env create --name envname --file=environment.yml

