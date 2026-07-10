with open("products_catalog.py", "r", encoding="utf-8") as f:
    c = f.read()
    
# Replace the files array for spiral_tilings_ipad
old_files = '''        "files": [
            p("ipad_spiral_cbn", "SpiralTilings_CBN_iPad_GoodNotes.pdf"),
            p("ipad_spiral_cbn", "SpiralTilings_CBN_Procreate_PNG_part1.zip"),
            p("ipad_spiral_cbn", "SpiralTilings_CBN_Procreate_PNG_part2.zip"),
            p("ipad_spiral_cbn", "SpiralTilings_CBN.swatches"),
            p("ipad_spiral_cbn", "How_to_use_on_iPad.pdf"),
        ],'''
new_files = '''        "files": [
            p("ipad_spiral_cbn_svg", "SpiralTilings_CBN_Interactive.zip"),
        ],'''
c = c.replace(old_files, new_files)

with open("products_catalog.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Updated products_catalog.py successfully")
