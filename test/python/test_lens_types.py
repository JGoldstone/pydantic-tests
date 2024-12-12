#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-3-Clause
# Copyright Contributors to the SMTPE RIS OSVP Metadata Project

"""Tests for lens types"""

import unittest

from pydantic import ValidationError, json

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
        expected_json: json = {
            "radial": (1.0,),
            "tangential": (1.0,),
            "model": "Brown-Conrady"
        }
        json_from_instance: json = valid.to_json()
        self.assertDictEqual(expected_json, json_from_instance)
        instance_from_json: Distortion = Distortion.from_json(json_from_instance)
        self.assertEqual(valid, instance_from_json)
        expected_schema: json = {
            "$defs": {
                "NonBlankUTF8String": {
                    "maxLength": 1023,
                    "minLength": 1,
                    "type": "string"
                }
            },
            "properties": {
                "radial": {
                    "items": {
                        "type": "number"
                    },
                    "type": "array"
                },
                "tangential": {
                    "anyOf": [
                        {
                            "items": {
                                "type": "number"
                            },
                            "type": "array"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": None
                },
                "model": {
                    "anyOf": [
                        {
                            "$ref": "#/$defs/NonBlankUTF8String"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": None
                }
            },
            "required": [
                "radial"
            ],
            "type": "object"
        }
        schema_from_model: json = Distortion.make_json_schema()
        self.assertDictEqual(expected_schema, schema_from_model)



if __name__ == '__main__':
    unittest.main()
