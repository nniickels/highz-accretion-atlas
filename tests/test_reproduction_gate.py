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

    def test_only_bounded_channel_roundoff_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'a.png', Path(d)/'b.png'
            im = Image.new('RGB', (512, 512), (100, 100, 100))
            im.save(a)
            im.putpixel((300, 300), (103, 97, 100))
            im.save(b)
            compare_artifact(a, b)
            with self.assertRaises(AssertionError):
                compare_artifact(a, b, exact_pixels=True)
            # A large unchanged background must not dilute a local mismatch.
            im.putpixel((300, 300), (104, 100, 100))
            im.save(b)
            with self.assertRaisesRegex(AssertionError, 'difference=4, allowed=3'):
                compare_artifact(a, b)

    def test_dimensions_and_alpha_remain_exact(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'a.png', Path(d)/'b.png'
            im = Image.new('RGBA', (12, 12), (100, 100, 100, 255))
            im.save(a)
            im.putpixel((3, 3), (100, 100, 100, 254))
            im.save(b)
            with self.assertRaisesRegex(AssertionError, 'transparency'):
                compare_artifact(a, b)
            im.resize((13, 12)).save(b)
            with self.assertRaisesRegex(AssertionError, 'dimensions'):
                compare_artifact(a, b)

    def test_missing_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'baseline',Path(d)/'generated'
            p=a/'results/v3/test.csv';p.parent.mkdir(parents=True);p.write_text('x\n1\n')
            with self.assertRaises(AssertionError):verify_against(a,b)

    def test_regenerated_manuscript_cannot_bless_its_own_changes(self):
        # Both workspaces can be internally consistent while disagreeing with
        # the reviewed baseline. The independent gate must still reject drift.
        for relative, original, changed in [
            ('paper/analysis/target_robustness.csv', 'object_id,required_fedd\na,1.2\n',
             'object_id,required_fedd\na,1.3\n'),
            ('paper/analysis/target_rows.tex', 'a & 1.200 \\\\\n', 'a & 1.300 \\\\\n'),
            ('paper/figures/early_start_comparison.tex', 'track=1.2\n', 'track=1.3\n'),
        ]:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as d:
                a, b = Path(d)/'baseline', Path(d)/'generated'
                for root in (a,b):
                    path = root/relative
                    path.parent.mkdir(parents=True)
                    path.write_text(original)
                self.assertEqual(verify_against(a,b), 1)
                (b/relative).write_text(changed)
                with self.assertRaises(AssertionError):verify_against(a,b)

    def test_manuscript_figure_and_membership_are_checked(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'baseline',Path(d)/'generated'
            for root in (a,b):
                (root/'paper/figures').mkdir(parents=True)
                Image.new('RGB',(12,12),'white').save(root/'paper/figures/uncertainty.png')
                (root/'paper/figures/README.md').write_text(str(root))
            self.assertEqual(verify_against(a,b), 1)  # Source docs are not outputs.
            im=Image.new('RGB',(12,12),'white');im.putpixel((3,3),(0,0,0))
            im.save(b/'paper/figures/uncertainty.png')
            with self.assertRaises(AssertionError):verify_against(a,b)
            (b/'paper/figures/uncertainty.png').unlink()
            with self.assertRaisesRegex(AssertionError,'membership'):verify_against(a,b)

    def test_self_comparison_is_rejected_even_through_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'generated';root.mkdir()
            alias=Path(d)/'alias';alias.symlink_to(root,target_is_directory=True)
            for baseline in (root,alias):
                with self.assertRaisesRegex(ValueError,'independent'):
                    verify_against(baseline,root)
