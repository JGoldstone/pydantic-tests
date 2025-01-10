#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

'''CLI tool to generate and validate JSON for an example OpenTrackIO recommended static metadata sample'''

import json
import sys

from camdkit.examples import get_recommended_static_example

if __name__ == "__main__":
  json_as_text = json.dumps(get_recommended_static_example(),
                            sort_keys=True,
                            indent=2)
  if len(sys.argv) == 2:
    with open(sys.argv[1], "w") as fp:
      print(json_as_text, file=fp)
  else:
    print(json_as_text)
