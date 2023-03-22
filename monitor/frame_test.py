#!/usr/bin/python
import cv2
import os
import numpy as np
from PIL import Image
import time
import glob
import sys
from openhmd import PyOpenHMD

import os
import subprocess
pyopenhmd = PyOpenHMD()

print('test start')
PATH = os.getcwd()
print('path', PATH)

# Clear the terminal
subprocess.run("clear", shell=True)

# Remove contents of the './result' directory
result_dir = "../simulator/openhmd_2/result"
subprocess.run(f"rm -rf {result_dir}/*", shell=True)

# Remove the 'monado_comp_ipc' file in the '/run/user/UID' directory
uid = os.getuid()
ipc_file = f"/run/user/{uid}/monado_comp_ipc"
subprocess.run(f"rm -rf {ipc_file}", shell=True)

# Run the 'monado-service' executable from the specified path
monado_service_path = f"/home/{os.environ['USER']}/bin/usr/local/bin/monado-service"
subprocess.run(monado_service_path, shell=True)


# while True:
#     pyopenhmd.poll()
#     time.sleep(1)
#     if cv2.waitKey(24) == 27:
#         break
