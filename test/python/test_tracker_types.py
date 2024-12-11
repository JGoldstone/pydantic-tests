import unittest

from pydantic import ValidationError

from camdkit.string_types import NonBlankUTF8String

from camdkit.tracker_types import StaticTracker, Tracker


class TrackerTestCases(unittest.TestCase):

    def test_tracker_make(self):
        st = StaticTracker()
        self.assertIsNone(st.make)
        with self.assertRaises(ValidationError):
            st.make = 0+0.1j
        with self.assertRaises(ValidationError):
            st.make = ""
        smallest_valid_make: str = "x"
        st.make = "x"
        self.assertEqual(smallest_valid_make, st.make)
        largest_valid_make: str = "x" * 1023
        st.make = largest_valid_make
        self.assertEqual(largest_valid_make, st.make)
        with self.assertRaises(ValidationError):
            st.make = "x" * 1024

    def test_tracker_model_name(self):
        st = StaticTracker()
        self.assertIsNone(st.model_name)
        with self.assertRaises(ValidationError):
            st.model_name = 0+0.1j
        with self.assertRaises(ValidationError):
            st.model_name = ""
        smallest_valid_model_name: str = "x"
        st.model_name = "x"
        self.assertEqual(smallest_valid_model_name, st.model_name)
        largest_valid_model_name: str = "x" * 1023
        st.model_name = largest_valid_model_name
        self.assertEqual(largest_valid_model_name, st.model_name)
        with self.assertRaises(ValidationError):
            st.model_name = "x" * 1024

    def test_tracker_serial_number(self):
        st = StaticTracker()
        self.assertIsNone(st.serial_number)
        with self.assertRaises(ValidationError):
            st.serial_number = 0+0.1j
        with self.assertRaises(ValidationError):
            st.serial_number = ""
        smallest_valid_serial_number: str = "x"
        st.serial_number = "x"
        self.assertEqual(smallest_valid_serial_number, st.serial_number)
        largest_valid_serial_number: str = "x" * 1023
        st.serial_number = largest_valid_serial_number
        self.assertEqual(largest_valid_serial_number, st.serial_number)
        with self.assertRaises(ValidationError):
            st.serial_number = "x" * 1024

    def test_tracker_firmware_version(self):
        st = StaticTracker()
        self.assertIsNone(st.firmware_version)
        with self.assertRaises(ValidationError):
            st.firmware_version = 0+0.1j
        with self.assertRaises(ValidationError):
            st.firmware_version = ""
        smallest_valid_firmware_version: str = "x"
        st.firmware_version = "x"
        self.assertEqual(smallest_valid_firmware_version, st.firmware_version)
        largest_valid_firmware_version: str = "x" * 1023
        st.firmware_version = largest_valid_firmware_version
        self.assertEqual(largest_valid_firmware_version, st.firmware_version)
        with self.assertRaises(ValidationError):
            st.firmware_version = "x" * 1024

    def test_tracker_notes(self):
        t = Tracker()
        self.assertIsNone(t.notes)
        with self.assertRaises(ValidationError):
            t.notes = 0 + 0.1j
        empty_tuple: tuple[NonBlankUTF8String, ...] = ()
        t.notes = empty_tuple
        self.assertEqual(empty_tuple, t.notes)
        with self.assertRaises(ValidationError):
            t.notes = (1,)
        valid_single_note: tuple[NonBlankUTF8String, ...] = ('foo',)
        t.notes = valid_single_note
        self.assertEqual(valid_single_note, t.notes)
        invalid_heterogenous_notes: tuple[NonBlankUTF8String, ...] = ('foo', 0 + 1j)
        with self.assertRaises(ValidationError):
            t.notes = invalid_heterogenous_notes
        valid_two_notes: tuple[NonBlankUTF8String, ...] = ('foo', 'bar')
        t.notes = valid_two_notes
        self.assertEqual(valid_two_notes, t.notes)

    def test_tracker_recording(self):
        t = Tracker()
        self.assertIsNone(t.recording)
        with self.assertRaises(ValidationError):
            t.recording = 0 + 0.1j
        empty_tuple: tuple[bool, ...] = tuple()
        t.recording = empty_tuple
        self.assertEqual(empty_tuple, t.recording)
        with self.assertRaises(ValidationError):
            t.recording = (1,)
        valid_single_recording: tuple[bool, ...] = (True,)
        t.recording = valid_single_recording
        self.assertEqual(valid_single_recording, t.recording)
        invalid_heterogenous_recording: tuple[bool, ...] = (True, 0 + 1j)
        with self.assertRaises(ValidationError):
            t.recording = invalid_heterogenous_recording
        valid_two_recording: tuple[bool, ...] = (True, False)
        t.recording = valid_two_recording
        self.assertEqual(valid_two_recording, t.recording)

    def test_tracker_slate(self):
        t = Tracker()
        self.assertIsNone(t.slate)
        with self.assertRaises(ValidationError):
            t.slate = 0 + 0.1j
        empty_tuple: tuple[NonBlankUTF8String, ...] = ()
        t.slate = empty_tuple
        self.assertEqual(empty_tuple, t.slate)
        with self.assertRaises(ValidationError):
            t.slate = (1,)
        valid_single_note: tuple[NonBlankUTF8String, ...] = ('foo',)
        t.slate = valid_single_note
        self.assertEqual(valid_single_note, t.slate)
        invalid_heterogenous_slate: tuple[NonBlankUTF8String, ...] = ('foo', 0 + 1j)
        with self.assertRaises(ValidationError):
            t.slate = invalid_heterogenous_slate
        valid_two_slate: tuple[NonBlankUTF8String, ...] = ('foo', 'bar')
        t.slate = valid_two_slate
        self.assertEqual(valid_two_slate, t.slate)

    def test_tracker_status(self):
        t = Tracker()
        self.assertIsNone(t.status)
        with self.assertRaises(ValidationError):
            t.status = 0 + 0.1j
        empty_tuple: tuple[NonBlankUTF8String, ...] = ()
        t.status = empty_tuple
        self.assertEqual(empty_tuple, t.status)
        with self.assertRaises(ValidationError):
            t.status = (1,)
        valid_single_note: tuple[NonBlankUTF8String, ...] = ('foo',)
        t.status = valid_single_note
        self.assertEqual(valid_single_note, t.status)
        invalid_heterogenous_status: tuple[NonBlankUTF8String, ...] = ('foo', 0 + 1j)
        with self.assertRaises(ValidationError):
            t.status = invalid_heterogenous_status
        valid_two_status: tuple[NonBlankUTF8String, ...] = ('foo', 'bar')
        t.status = valid_two_status
        self.assertEqual(valid_two_status, t.status)

        
if __name__ == '__main__':
    unittest.main()
