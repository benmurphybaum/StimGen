StimGen is python-based user interface for designing and presenting arbitrary visual stimuli through a projector or monitor. It uses the Qt and psychopy libraries to control the GUI and stimulus presentation, respectively. 

No coding by the user is required, barring some snags with specific setup configurations, especially for sending/receiving TTL triggers. 

Once set up, users can fully design the spatial and temporal properties of their visual stimulus, which can include an arbitrary number of independently controlled objects. Supported objects are circles, rectangles, gratings, plaids, snakes, motion clouds, windmills, concentric rings, white noise, and natural images.

Users can design stimuli in sequences, such that single or multiple stimulus parameters can change for each subsequent stimulation (i.e. increasing spot diameter, different directions of motion, etc.).

Stimuli can be saved in a 'stimulus bank' so that they can be reused from session to session. 

--------------------
Each stimulus is dropped into an output .h5 file, which can be picked up by a different program to incorporate into data acquisition.

--------------------
Install as a conda environment using the included environment file: environment.yml

conda env create --name envname --file=environment.yml
