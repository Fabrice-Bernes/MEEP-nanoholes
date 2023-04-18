#! /usr/bin/python


"""         ---LIBRARIES---         """

import os
import shutil
import subprocess
import datetime
import subprocess
import argparse
import re
import ast

os.chdir(os.path.dirname(__file__))
os.mkdir("simulations") if not os.path.exists("simulations") else print("sims dir exists")

"""
All parameters are optional. If not set, will be chosen from default or last used value
-p <PATH> to read parameters from existing simulation DIRECTORY
-Hw : Hole width
-Hd : Hole depth/thickness
-Hs : Separation between holes
-Hq : Hole quantity
-Gd : Glass thickness
-Ss : Source distance
-Sa : Source angle
-Sf : Source frequency
"""

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--simulation", dest="simulation_basename", help="run from simulation")
parser.add_argument("-Hw", "--HoleWid", dest="HoleWid", default="NaN", help="Hole Width")
parser.add_argument("-Hd", "--HoleDpt", dest="HoleDpt", default="NaN", help="Hole Thickness")
parser.add_argument("-Hs", "--HoleSep", dest="HoleSep", default="NaN", help="Hole Separation")
parser.add_argument("-Hq", "--HoleQty", dest="HoleQty", default="NaN", help="Hole Quantity")
parser.add_argument("-Gd", "--GlassDpt", dest="GlassDpt", default="NaN", help="Glass Thickness")
parser.add_argument("-Ss", "--SrcDist", dest="SrcDist", default="NaN", help="Source Distance")
parser.add_argument("-Sa", "--SrcTheta", dest="SrcTheta", default="NaN", help="Angle between Sources")
parser.add_argument("-Sf", "--Srcfreq", dest="SrcFreq", default="NaN", help="Source Frequency") #TODO unused
args = parser.parse_args()

class Simulation:
    """Class with the ability to read configs and write logs and so on"""

    def __init__(self, SimName):
        self.name = SimName
        self.logfile = "simulations/" + self.name+ "/LOG.txt"
        self.guile_params = (args.HoleQty,
                        args.HoleSep,
                        args.HoleWid,
                        args.HoleDpt,
                        args.GlassDpt,
                        args.SrcDist,
                        args.SrcTheta,
                        args.SrcFreq)

    def get_real_config(self):
        """Returns array with values of /.SimParams"""
        with open(".SimParams", mode="r+") as defaults_file:
            defaults_array = defaults_file.readline().rstrip()
            defaults_array = re.sub(r"   ", r",", defaults_array)
            new_array = ast.literal_eval(defaults_array)           # This is a tuple
            return list(new_array)                                 # Now we can change it and stuff

    def get_log_config(self):
        """Returns array with values of self.logfile"""
        with open(self.logfile, mode="r+") as defaults_file:
            defaults_array = defaults_file.readline().rstrip()
            defaults_array = re.sub(r"   ", r",", defaults_array)
            new_array = ast.literal_eval(defaults_array)           # This is a tuple
            return list(new_array)                                 # Now we can change it and stuff

    def sync_config(self, which):
        """ If user has set any parameter as a cmd argument, update defaults to reflect that """
        if which == "real":
            config_array = self.get_real_config()
        else:
            config_array = self.get_log_config()

        for i in range(0,len(self.guile_params)):
            if self.guile_params[i] != "NaN":
                config_array[i] = self.guile_params[i]
        
        synced_string = "( "
        for i in config_array:
            synced_string = synced_string + str(i) + "   "
        synced_string = synced_string + ")"
            
        with open(".SimParams", mode="r+") as defaults_file:
            defaults_file.seek(0)
            defaults_file.write(synced_string)

        with open(self.logfile, mode="w") as logfile:
            logfile.write(synced_string)

    def run_sim(self):
        meep_run = subprocess.run(["meep", "./nano_holes.ctl"])
        #TODO error handling

    def sim_to_frames(self):
        all_dimensions = subprocess.run(["h5ls", "-l", "nano_holes-out/ez.h5"], capture_output=True, text=True)
        time_dimension = re.search(r"\d+, \d+, (\d+)", all_dimensions.stdout).group(1)
        frames = subprocess.run(
            ["h5topng",
             "-S3",
             "-t", "0:" + str(int(time_dimension)-1),
             "-R",
             "-Zc", "dkbluered",
             "-a", "gray",
             "-A", "./nano_holes-out/eps-000000.00.h5",
             "./nano_holes-out/ez.h5"])

    def frames_to_gif(self):
        gif = subprocess.run(["convert", "nano_holes-out/*.png", "./simulations/" +self.name + "/" + self.name + ".gif"])
    
    def clean(self):
        shutil.move("nano_holes-out/ez.h5", "simulations/" + self.name + "/")
        shutil.move("nano_holes-out/S-vec.h5", "simulations/" + self.name + "/")
        shutil.rmtree("nano_holes-out")

    def log(self, string):
        with open(self.logfile, mode="w") as file:
            file.write(string)

if not args.simulation_basename:
    print("A simulation name must be provided!"); exit
elif os.path.isdir("simulations/" + args.simulation_basename):
    sim = Simulation(args.simulation_basename)
    sim.sync_config("log")
else:
    os.mkdir("simulations/" + args.simulation_basename)
    sim = Simulation(args.simulation_basename)
    sim.sync_config("real")

sim.run_sim()
sim.sim_to_frames()
sim.frames_to_gif()
sim.clean()
