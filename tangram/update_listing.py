"""Refresh the existing Tangram listing (4589729409) after the classic-figure redesign:
new title/description, replace all images and both PDF files."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from etsy_manager import EtsyManager
from create_listing import TITLE, DESC, TAGS

LID = 4589729409


def main():
    m = EtsyManager(); sid = m.get_shop_id()
    m.update_listing(LID, title=TITLE, description=DESC, tags=TAGS)
    old = [im['listing_image_id'] for im in m.make_request('GET', f'/listings/{LID}/images')['results']]
    new = [m.upload_listing_image(LID, p, rank=10 + i)['listing_image_id']
           for i, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))))]
    for i in old:
        m.make_request('DELETE', f'/shops/{sid}/listings/{LID}/images/{i}')
    for rank, i in enumerate(new, 1):
        m.make_request('POST', f'/shops/{sid}/listings/{LID}/images', is_multipart=True,
                       multipart_data=({'listing_image_id': str(i), 'rank': str(rank)}, {}))
    for f in m.make_request('GET', f'/shops/{sid}/listings/{LID}/files')['results']:
        m.make_request('DELETE', f'/shops/{sid}/listings/{LID}/files/{f["listing_file_id"]}')
    for name in ("Letter", "A4"):
        m.upload_listing_file(LID, os.path.join(HERE, "out", f"Tangram_Puzzles_{name}.pdf"))
    r = m.make_request('GET', f'/listings/{LID}?includes=Images')
    files = m.make_request('GET', f'/shops/{sid}/listings/{LID}/files')['results']
    print(f"\n{LID} state={r['state']} title={r['title'][:60]!r} images={len(r['images'])} "
          f"ranks={[im['rank'] for im in r['images']]} files={[f['filename'] for f in files]}")


if __name__ == "__main__":
    main()
