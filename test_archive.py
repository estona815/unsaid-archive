import unittest
from archive import passages

class SourceIntegrity(unittest.TestCase):
    def test_unicode_exact_offsets(self):
        text = '첫 기억.\n\n  A lamp — still lit.  \n'
        for row in passages([{'id':'a','text':text}]):
            self.assertEqual(text[row['start']:row['end']], row['quote'])
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            passages([{'id':'a','text':'one'},{'id':'a','text':'two'}])
    def test_empty_archive_rejected(self):
        with self.assertRaises(ValueError): passages([])
    def test_edit_changes_provenance(self):
        a=passages([{'id':'a','text':'left'}])[0]
        b=passages([{'id':'a','text':'stayed'}])[0]
        self.assertNotEqual(a['source_sha256'],b['source_sha256'])

if __name__ == '__main__': unittest.main()
