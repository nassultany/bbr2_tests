# bbr2_tests
This repo contains the code used to peform this project. The python script is used to set up the mininet topology and run various experiments.
There are commented lines that tell what which parameters to change in order to test certain configurations. For example you can modify the 
loss rates at r1, the bandwidth and buffer size at r2's link to r3, the rtt for different hosts, and the TCP algorithms they run.

The logs directory contains some experimental results we obtained while testing the different configurations, and also a simple script to help
parse the data for easier visualization.

To run the experiment, make sure you have the TCP algorithms already installed in your kernel. Then, you can do

sudo python3 ProjectTopo.py.

If you wish to terminate it early for any reason, then you can do a simple ctrl-c, but make sure you then kill the bird routing protocol processes 
as well. Failure to do so will cause an error next time you try to run the program.

sudo pkill -f bird.

.
