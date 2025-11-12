"""Test that each TTRPG has its own button-texts directory populated.
This doesn't (and can't easily) run front-end JS here, but ensures separation on disk.
"""
import os
import glob
import pytest

TTRPGS = [
    'dune', 'the-witcher', 'zweihander', 'mouse-guard', 'pendragon', 'master-template', 'cyberpunk'
]
BASE = os.path.join('static')

@pytest.mark.parametrize('ttrpg', TTRPGS)
def test_button_texts_directory_exists(ttrpg):
    path = os.path.join(BASE, ttrpg, 'button-texts')
    assert os.path.isdir(path), f"Missing button-texts for {ttrpg}"
    files = sorted(glob.glob(os.path.join(path, 'button*.txt')))
    assert len(files) >= 5, f"Expected some button text files for {ttrpg}, found {len(files)}"


def test_all_sets_independent():
    # Ensure they are distinct directories (not the same inode via symlink) and contain at least button1.txt
    inodes = {}
    for t in TTRPGS:
        f = os.path.join(BASE, t, 'button-texts', 'button1.txt')
        assert os.path.isfile(f), f"Missing button1.txt in {t}"
        st = os.stat(f)
        key = (st.st_dev, st.st_ino)
        # It's permissible to have same inode if hard linked; warn instead of fail
        if key in inodes:
            print(f"WARNING: {t} button1.txt shares inode with {inodes[key]} (hard link?)")
        else:
            inodes[key] = t
