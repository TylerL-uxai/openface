# Copyright 2015 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import binascii
from subprocess import Popen, PIPE
import os
import os.path
import time

import numpy as np
import cv2

myDir = os.path.dirname(os.path.realpath(__file__))


class TorchWrap:
    # Warning: This is very unstable!
    # Please join us in improving it at:
    #   https://github.com/cmusatyalab/openface/issues/1
    #   https://github.com/cmusatyalab/openface/issues/4

    def __init__(self, model=os.path.join(myDir, '..', 'models', 'openface', 'nn4.v1.t7'),
                 imgDim=96, cuda=False):
        cmd = ['/usr/bin/env', 'th', os.path.join(myDir, 'openface_server.lua'),
               '-model', model, '-imgDim', str(imgDim)]
        if cuda:
            cmd.append('-cuda')
        self.p = Popen(cmd, stdin=PIPE, stdout=PIPE,
                       stderr=PIPE, bufsize=0)

        def exitHandler():
            if self.p.poll() is None:
                p.kill()
        atexit.register(exitHandler)
        time.sleep(0.5)
        rc = self.p.poll()
        if rc is not None and rc != 0:
            raise Exception("""


OpenFace: Unable to initialize the `openface_server.lua` subprocess.
Is the Torch command `th` on your PATH? Check with `which th`.

Diagnostic information:

cmd: {}

============

stdout: {}

============

stderr: {}
""".format(cmd, self.p.stdout.read(), self.p.stderr.read()))

    def forwardPath(self, imgPath):
        self.p.stdin.write(imgPath + "\n")
        return [float(x) for x in self.p.stdout.readline().strip().split(',')]

    def forwardImage(self, rgb):
        t = '/tmp/openface-torchwrap-{}.png'.format(
            binascii.b2a_hex(os.urandom(8)))
        cv2.imwrite(t, rgb)
        rep = np.array(self.forwardPath(t))
        os.remove(t)
        return rep
