import tempfile
import unittest
from pathlib import Path

from field_vision.common import wilson, read_manifest
from field_vision.data import validate_label
from field_vision.evaluate import iou, correctly_localized, summarize
from field_vision.inference import Policy, uncertain


class Contracts(unittest.TestCase):
    def test_annotations_are_not_image_level_labels(self):
        with self.assertRaises(ValueError): validate_label('0', 'detect', 2)
        with self.assertRaises(ValueError): validate_label('0 .5 .5 1 1', 'segment', 2)
        with self.assertRaises(ValueError): validate_label('2 .5 .5 .2 .2', 'detect', 2)
        with self.assertRaises(ValueError): validate_label('0 .1 .1 1 1', 'detect', 2)
        validate_label('', 'detect', 2)
        validate_label('0 .5 .5 .2 .2', 'detect', 2)
        validate_label('0 0 0 1 0 1 1', 'segment', 2)

    def test_duplicate_predictions_not_counted_twice(self):
        pred={'class_id':0,'box':[0,0,10,10],'score':.9}
        self.assertTrue(correctly_localized([pred],[(0,[0,0,10,10])]))
        self.assertFalse(correctly_localized([pred,pred],[(0,[0,0,10,10])]))
        self.assertFalse(correctly_localized([pred],[(1,[0,0,10,10])]))
        self.assertFalse(correctly_localized([],[]))

    def test_no_predictions_never_implies_healthy(self):
        result=uncertain('no_reliable_lesion')
        self.assertEqual(result['status'],'uncertain')
        self.assertEqual(result['lesions'],[])

    def test_release_requires_samples_not_perfect_small_sample(self):
        good={'accepted':True,'correct':True,'negative':False}
        neg={'accepted':False,'correct':False,'negative':True}
        self.assertFalse(summarize([good,neg])['release_passed'])
        self.assertFalse(summarize([])['release_passed'])
        self.assertTrue(summarize([good]*100+[neg]*300)['release_passed'])
        bad={'accepted':True,'correct':False,'negative':True}
        self.assertFalse(summarize([good]*100+[bad]*300)['release_passed'])
        self.assertGreater(wilson(0,300)[1],0)

    def test_threshold_cannot_silently_drop_below_requested_minimum(self):
        with self.assertRaises(ValueError): Policy(confidence=.3)
        self.assertEqual(iou([0,0,10,10],[0,0,10,10]),1.)


if __name__ == '__main__': unittest.main()
