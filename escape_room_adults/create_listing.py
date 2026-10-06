"""Create The Mathematician's Vault (printable escape room for adults) as a DRAFT digital
Etsy listing (taxonomy 1350 Party Games, section Puzzles)."""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(REPO); sys.path.insert(0, REPO)
from etsy_manager import EtsyManager
import brand

TITLE = ("Printable Escape Room for Adults, The Mathematician's Vault, Logic Puzzle Game for Game Night, "
         "Date Night or Math Club, Brain Teasers")
PRICE = 9.99
TAXONOMY = 1350
SECTION = 60521322  # Puzzles
TAGS = ["escape room adults", "printable escape", "escape room game", "game night", "date night game",
        "logic puzzles", "brain teasers", "puzzle game adults", "math puzzles", "party game adults",
        "cipher puzzle", "escape room kit", "mystery game"]

DESC = f"""The Mathematician's Vault: a printable escape room for adults. Professor Elias Hartmann has left everything he owned in a vault behind his desk, and the password is hidden, one letter at a time, in nine exhibits around his study. Can your team open it?

INSTANT DOWNLOAD
This is a digital file; nothing is shipped. Print at home and play tonight.

HOW IT WORKS
- Read the professor's letter and solve the nine exhibits, in any order.
- Each answer is a number from 1 to 26; the decoder turns it into a letter.
- The nine letters spell the password that opens the vault. If they make a real word, your team got everything right.

THE NINE EXHIBITS (real, classic puzzles)
1. The Locked Drawer: a Caesar cipher
2. The Engraver's Square: Dürer's 1514 magic square
3. The Faculty Corridor: a logic puzzle
4. The Symbol Ledger: equations written in symbols
5. The Pencil Jar: a geometry question
6. The Desk Lamps: a binary code
7. The Chalkboard: Roman numerals
8. The Famous Telegram: SEND + MORE = MONEY
9. The Rabbit Problem: Fibonacci's puzzle from 1202

WHAT'S INCLUDED (17 pages, US Letter and A4)
- Cover and host guide with setup tips
- The professor's letter (with a start-time box)
- 9 exhibit pages, each with its own lock box
- The vault page with the decoder and password boxes
- 9 cut-out hint cards
- Answer key with a short explanation for every puzzle
- "The Vault Is Open" certificate
- Terms of use

DETAILS
- For 2 to 6 adults or teens; takes about 60-90 minutes
- No special math knowledge needed, just curiosity and teamwork
- Every answer has been checked by computer to be unique
- Great for game night, date night, birthday parties, team building and math clubs

For personal, family and single-classroom use. Please do not resell or share the file.

{brand.COPYRIGHT}"""


def main():
    assert len(TITLE) <= 140 and len(TAGS) == 13 and all(len(t) <= 20 for t in TAGS)
    m = EtsyManager()
    lid = m.create_draft_listing(TITLE, DESC, PRICE, TAXONOMY, is_digital=True, tags=TAGS)
    for rank, p in enumerate(sorted(glob.glob(os.path.join(HERE, "out", "previews", "*.jpg"))), 1):
        m.upload_listing_image(lid, p, rank=rank)
    for name in ("Letter", "A4"):
        m.upload_listing_file(lid, os.path.join(HERE, "out", f"Mathematicians_Vault_Escape_Room_{name}.pdf"))
    m.update_listing(lid, shop_section_id=SECTION)
    r = m.make_request('GET', f'/listings/{lid}?includes=Images')
    print(f"\nlisting {lid} state={r['state']} images={len(r['images'])} section={r['shop_section_id']}")


if __name__ == "__main__":
    main()
