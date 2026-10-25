"""Unit test of the verification rule (no simulation needed, ROS 2 installed).

    cd ~/hcw_ws && source scripts/env.sh && python3 -m unittest src/hcw_perception/test/test_verifier_rule.py -v

Rule: the expected tag, alone, in 5 consecutive detection messages = VERIFIED.
"""
import json
import unittest

import rclpy
from apriltag_msgs.msg import AprilTagDetection, AprilTagDetectionArray
from std_msgs.msg import Int32

from hcw_perception.verifier import Verifier


def detections(*ids):
    msg = AprilTagDetectionArray()
    for i in ids:
        d = AprilTagDetection()
        d.id = i
        msg.detections.append(d)
    return msg


class VerifierRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.v = Verifier()
        self.v.on_expected(Int32(data=11))

    def tearDown(self):
        self.v.destroy_node()

    def feed(self, *frames):
        for ids in frames:
            self.v.on_detections(detections(*ids))

    def test_five_consecutive_frames_verify(self):
        self.feed(*[[11]] * 4)
        self.assertFalse(self.v.consecutive >= self.v.required)
        self.feed([11])
        self.assertGreaterEqual(self.v.consecutive, 5)

    def test_flicker_never_verifies(self):
        """Tag visible for 4 frames, gone for 1, repeatedly: never 5 in a row."""
        for _ in range(10):
            self.feed([11], [11], [11], [11], [])
            self.assertLess(self.v.consecutive, self.v.required)

    def test_other_tag_in_view_blocks_verification(self):
        self.feed(*[[11, 14]] * 10)
        self.assertEqual(self.v.consecutive, 0)

    def test_wrong_tag_alone_does_not_verify(self):
        self.feed(*[[12]] * 10)
        self.assertEqual(self.v.consecutive, 0)

    def test_nothing_in_view_does_not_verify(self):
        self.feed(*[[]] * 10)
        self.assertEqual(self.v.consecutive, 0)

    def test_changing_the_expected_tag_resets_the_count(self):
        self.feed(*[[11]] * 4)
        self.v.on_expected(Int32(data=12))
        self.assertEqual(self.v.consecutive, 0)

    def test_not_looking_never_verifies(self):
        self.v.on_expected(Int32(data=0))
        self.feed(*[[11]] * 10)
        self.assertEqual(self.v.consecutive, 0)

    def test_status_json_matches(self):
        sent = []
        self.v.pub.publish = lambda m: sent.append(json.loads(m.data))
        self.feed(*[[11]] * 5)
        self.assertTrue(sent[-1]['verified'])
        self.assertEqual(sent[-1]['detected_ids'], [11])
        self.feed([11, 12])
        self.assertFalse(sent[-1]['verified'])


if __name__ == '__main__':
    unittest.main()
