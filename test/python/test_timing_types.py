#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types to model time, timing and synchronization"""

import unittest

from pydantic import ValidationError

from camdkit.timing_types import SynchronizationSource, SynchronizationOffsets

class TimingTestCases(unittest.TestCase):

    def test_synchronization_source_validation(self) -> None:
        # not perfect but better than nothing
        # TODO use changes in snake case to insert underscores
        self.assertListEqual([m.name.lower().replace('_','')
                              for m in SynchronizationSource],
                             [m.value.lower().replace('_','')
                              for m in SynchronizationSource])

    def test_synchronization_offsets_validation(self) -> None:
        with self.assertRaises(ValidationError):
            SynchronizationOffsets(translation='a', rotation=2.0, lens_encoders=3.0)


if __name__ == '__main__':
    unittest.main()
