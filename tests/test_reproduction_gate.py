"""A baseline must detect changed scientific cells and changed rendered pixels."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.internal.verify_regenerated_artifacts import compare_artifact, verify_against


class ReproductionGateTests(unittest.TestCase):
    def test_changed_compatibility_value_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a.csv',Path(d)/'b.csv'
            a.write_text('object_id,required_log_mseed,compatible\nexample,4.5,True\n')
            b.write_text('object_id,required_log_mseed,compatible\nexample,4.6,True\n')
            with self.assertRaises(AssertionError):compare_artifact(a,b)

    def test_pixels_checked_independently_of_png_encoding(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a.png',Path(d)/'b.png'
            im=Image.new('RGB',(12,12),'white');im.save(a,compress_level=0);im.save(b,compress_level=9)
            compare_artifact(a,b)
            im.putpixel((3,3),(0,0,0));im.save(b)
            with self.assertRaises(AssertionError):compare_artifact(a,b)

    def test_missing_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'baseline',Path(d)/'generated'
            p=a/'results/v3/test.csv';p.parent.mkdir(parents=True);p.write_text('x\n1\n')
            with self.assertRaises(AssertionError):verify_against(a,b)
