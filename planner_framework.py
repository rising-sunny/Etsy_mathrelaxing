import os
import fitz

class DigitalPlanner:
    def __init__(self, width=800, height=1000, theme=None):
        self.width = width
        self.height = height
        self.theme = theme or {
            "bg": (1, 1, 1),
            "tab_bg": (0.8, 0.8, 0.8),
            "tab_bg_alt": (0.9, 0.9, 0.9),
            "tab_text": (0, 0, 0),
            "home_bg": (0, 0, 0),
            "home_text": (1, 1, 1)
        }
        self.sections = []
        self.draw_background_callback = None
        self.draw_index_callback = None
        self.tab_width = 30
        self.tab_height = 25
        self.font = "helv"

    def set_background_renderer(self, renderer):
        """renderer(page, is_index)"""
        self.draw_background_callback = renderer

    def set_index_renderer(self, renderer):
        """renderer(page, section_targets_dict)"""
        self.draw_index_callback = renderer

    def add_section(self, kind, abbreviation, num_pages, renderer):
        """
        kind: internal identifier string
        abbreviation: 3 letter code for side tab
        num_pages: number of pages to generate for this section
        renderer: function(page, index_in_section)
        """
        self.sections.append({
            "kind": kind,
            "abbr": abbreviation,
            "num_pages": num_pages,
            "renderer": renderer
        })

    def build(self, output_path):
        doc = fitz.open()
        
        # Calculate total pages: 1 index + sum(sections)
        total_pages = 1 + sum(s["num_pages"] for s in self.sections)
        
        # 1. Create all pages
        for i in range(total_pages):
            doc.new_page(width=self.width, height=self.height)

        # 2. Map sections to starting pages
        section_first_page = {}
        current_page = 1
        
        for sec in self.sections:
            if sec["num_pages"] > 0:
                section_first_page[sec["kind"]] = current_page
                current_page += sec["num_pages"]

        # 3. Draw Backgrounds
        if self.draw_background_callback:
            self.draw_background_callback(doc[0], True)
            for i in range(1, total_pages):
                self.draw_background_callback(doc[i], False)

        # 4. Draw Index
        if self.draw_index_callback:
            self.draw_index_callback(doc[0], section_first_page)

        # 5. Render Sections
        current_page = 1
        for sec in self.sections:
            for j in range(sec["num_pages"]):
                if sec["renderer"]:
                    sec["renderer"](doc[current_page], j + 1)
                current_page += 1

        # 6. Draw side tabs on all content pages (pages 1..)
        for i in range(1, total_pages):
            page = doc[i]
            y = self.height - 40
            
            # Draw section tabs
            for j, sec in enumerate(self.sections):
                rect = fitz.Rect(0, y - j * (self.tab_height + 2), self.tab_width, y - j * (self.tab_height + 2) + self.tab_height)
                
                # alternating bg color
                fill = self.theme.get("tab_bg", (0.5, 0.5, 0.5))
                if j % 2 == 0 and "tab_bg_alt" in self.theme:
                    fill = self.theme["tab_bg_alt"]
                    
                page.draw_rect(rect, color=self.theme.get("tab_text", (0,0,0)), fill=fill)
                
                text_rect = fitz.Rect(0, rect.y0 + 3, self.tab_width, rect.y1)
                page.insert_textbox(text_rect, sec["abbr"][:3].upper(), fontsize=9, fontname=self.font, color=self.theme.get("tab_text", (0,0,0)), align=1)
                
                tp = section_first_page.get(sec["kind"], 1)
                page.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": tp, "to": fitz.Point(0, 0)})

            # Home / Index tab
            home = fitz.Rect(0, self.height - 28, self.tab_width, self.height - 8)
            page.draw_rect(home, color=self.theme.get("home_text", (1,1,1)), fill=self.theme.get("home_bg", (0,0,0)))
            page.insert_textbox(fitz.Rect(0, home.y0 + 3, self.tab_width, home.y1), "IDX", fontsize=9, fontname=self.font, color=self.theme.get("home_text", (1,1,1)), align=1)
            page.insert_link({"kind": fitz.LINK_GOTO, "from": home, "page": 0, "to": fitz.Point(0, 0)})

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc.save(output_path, deflate=True, garbage=4)
        doc.close()
        print(f"Generated framework planner: {output_path} with {total_pages} pages")
