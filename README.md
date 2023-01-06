Version of StimGen used for Srivastava et al. (2022). Spatiotemporal properties of glutamate input support direction selectivity in the dendrites of retinal starburst amacrine cells. eLife.

--------------------
StimGen is python-based user interface for designing and presenting arbitrary visual stimuli through a projector or monitor.

No coding by the user is required, barring some snags with specific setup configurations, especially for sending/receiving TTL triggers. 

Once set up, users can fully design the spatial and temporal properties of their visual stimulus, which can include an arbitrary number of independently controlled objects. Supported objects are circles, rectangles, gratings, plaids, snakes, motion clouds, windmills, concentric rings, white noise, and natural images.

Users can design stimuli in sequences, such that single or multiple stimulus parameters can change for each subsequent stimulation (i.e. increasing spot diameter, different directions of motion, etc.).

Stimuli can be saved in a 'stimulus bank' so that they can be reused from session to session. 

--------------------
Install as a conda environment using the included environment file: environment.yml

conda env create --name envname --file=environment.yml
