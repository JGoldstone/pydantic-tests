#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Types for model types"""

import sys
import math
import unittest
import json
from typing import Any, Optional, Annotated
from fractions import Fraction
from uuid import uuid4

from pydantic import ValidationError, BaseModel, Field

from camdkit.model_types import (SynchronizationSource, SynchronizationOffsets,
                                 Synchronization, SynchronizationPTP, UUIDURN)


VALID_SAMPLE_ID_URN_0 = "urn:uuid:5ca5f233-11b5-4f43-8815-948d73e48a33"
VALID_SAMPLE_ID_URN_1 = "urn:uuid:5ca5f233-11b5-dead-beef-948d73e48a33"

class ModelTestCases(unittest.TestCase):

    def test_uuid_urn(self):
        with self.assertRaises(TypeError):
            UUIDURN()
        s = UUIDURN(VALID_SAMPLE_ID_URN_0)
        self.assertEqual(VALID_SAMPLE_ID_URN_0, s.sample_id)
        s.value = VALID_SAMPLE_ID_URN_1
        self.assertEqual(VALID_SAMPLE_ID_URN_1, s.sample_id)
        with self.assertRaises(ValidationError):
            UUIDURN('')
        with self.assertRaises(ValidationError):
            UUIDURN('fail')
        UUIDURN.validate(UUIDURN(VALID_SAMPLE_ID_URN_0))
        json_from_instance: dict[str, Any] = UUIDURN.to_json(s)
        self.assertDictEqual({'value': VALID_SAMPLE_ID_URN_1},
                             json_from_instance)
        instance_from_json: UUIDURN = UUIDURN.from_json(json_from_instance)
        self.assertEqual(s, instance_from_json)
        schema = UUIDURN.make_json_schema()
        print(json.dumps(schema, indent=2))


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
