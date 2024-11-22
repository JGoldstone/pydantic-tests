import unittest
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from camdkit.model_types import SampleId, FrameRate

class ModelTestCases(unittest.TestCase):

    def test_sample_id_validation(self) -> None:
        with self.assertRaises(ValidationError):
            SampleId(value=None)
        with self.assertRaises(ValidationError):
            SampleId(value=0)
        with self.assertRaises(ValidationError):
            SampleId(value='')
        with self.assertRaises(ValidationError):
            SampleId(value='foo')
        valid_urn = uuid4().urn
        sample_id = SampleId(value=valid_urn)
        self.assertEqual(valid_urn, sample_id.value)
        defaulted = SampleId()
        SampleId(value=defaulted.value)

    def test_to_json(self) -> None:
        valid_urn = uuid4().urn
        expected = {'sampleId': valid_urn}
        actual = SampleId(sampleId=valid_urn).to_json()
        self.assertDictEqual(expected, actual)

    def test_from_json(self) -> None:
        valid_urn = uuid4().urn
        expected = SampleId(value=valid_urn)
        json_dict: dict[str, Any] = expected.to_json()
        actual = SampleId(**json_dict)
        self.assertEqual(expected, actual)

    def test_json_schema(self) -> None:
        expected = {}
        actual = SampleId.model_json_schema()
        self.assertDictEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
    SampleId()