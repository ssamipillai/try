import tempfile
import os
from manager_notes.notes import NotesManager, _slugify


def test_slugify():
    assert _slugify('Weekly Sync: Product') == 'weekly-sync-product'
    assert _slugify('  Multiple   Spaces  ') == 'multiple-spaces'


def test_create_and_search():
    with tempfile.TemporaryDirectory() as td:
        nm = NotesManager(td)
        p1 = nm.create_note('Weekly Sync Product', tags=['product'], open_in_editor=False)
        p2 = nm.create_note('Hiring sync', tags=['people'], open_in_editor=False)

        results = nm.search('sync')
        names = [r['name'] for r in results]
        assert any('weekly-sync-product' in n for n in names)
        assert any('hiring-sync' in n for n in names)
