#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for lens types"""

import unittest
import json

from typing import Any

from pydantic import ValidationError

from camdkit.lens_types import Distortion

class LensTypesTestCases(unittest.TestCase):

    # example of testing a struct:
    #   verify no-arg instantiation fails
    #   verify trying to instantiate with arguments of invalid type raises a validation error
    #   verify correct instantiation returns an object the attributes of which meet expectations
    #   verify one can set the object's attributes to new values
    #   when applicable, verify that trying to instantiate with arguments of the correct type
    #     but out-of-range or otherwise invalid values fail

    def test_distortion(self):
        with self.assertRaises(TypeError):
            Distortion()
        with self.assertRaises(ValidationError):
            Distortion(1)  # invalid: simple scalar of wrong type
        with self.assertRaises(ValueError):
            Distortion(tuple())  # invalid: empty radial tuple
        with self.assertRaises(ValidationError):
            Distortion((1+1j,))  # invalid: radial tuple containing wrong type
        Distortion((1.0,))  # valid: radial, no tangential, no model
        with self.assertRaises(ValueError):
            Distortion((1.0,), tuple())  # invalid: empty tangential tuple
        Distortion((1.0,), (1.0,))  # valid: radial, tangential, no model
        with self.assertRaises(ValueError):
            Distortion((1.0,), (1.0,), "")  # invalid: blank model
        valid = Distortion((1.0,), (1.0,), "Brown-Conrady")
        Distortion.validate(valid)
        expected_json: dict[str, Any] = {
            "radial": (1.0,),
            "tangential": (1.0,),
            "model": "Brown-Conrady"
        }
        json_from_instance: dict[str, Any] = Distortion.to_json(valid)
        self.assertDictEqual(expected_json, json_from_instance)
        instance_from_json: Distortion = Distortion.from_json(json_from_instance)
        self.assertEqual(valid, instance_from_json)
        expected_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "radial": { "type": "array", "items": { "type": "number" } },
                "tangential": {
                    "anyOf": [ { "type": "array", "items": { "type": "number" } },
                               { "type": "null" } ],
                    "default": None
                },
                "model": {
                    "anyOf": [ { "type": "string", "minLength": 1, "maxLength": 1023 },
                               { "type": "null" } ],
                    "default": None
                }
            },
            "required": [ "radial" ],
            "additionalProperties": False
        }
        schema_from_model: dict[str, Any] = Distortion.make_json_schema()
        self.assertDictEqual(expected_schema, schema_from_model)


if __name__ == '__main__':
    unittest.main()
