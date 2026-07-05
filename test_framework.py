import os
import fitz
from planner_framework import DigitalPlanner

def draw_bg(page, is_index):
    # Just draw a solid background
    page.draw_rect(page.rect, color=(0,0,0), fill=(0.95, 0.95, 0.95))
    page.insert_textbox(fitz.Rect(100, 50, 400, 100), "Index Page" if is_index else "Content Page", fontsize=20, fontname="helv", color=(0.2, 0.2, 0.2))

def draw_index(page, targets):
    # Draw simple buttons to targets
    y = 150
    for kind, start_page in targets.items():
        rect = fitz.Rect(100, y, 300, y + 40)
        page.draw_rect(rect, color=(0,0,0), fill=(0.8, 0.8, 0.9))
        page.insert_textbox(fitz.Rect(100, y+10, 300, y+40), f"Go to {kind}", fontsize=14, align=1)
        page.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": start_page, "to": fitz.Point(0,0)})
        y += 60

def draw_notes(page, idx):
    page.insert_textbox(fitz.Rect(100, 150, 500, 250), f"Notes Section - Page {idx}", fontsize=18)

def draw_tasks(page, idx):
    page.insert_textbox(fitz.Rect(100, 150, 500, 250), f"Tasks Section - Page {idx}", fontsize=18)

def draw_goals(page, idx):
    page.insert_textbox(fitz.Rect(100, 150, 500, 250), f"Goals Section - Page {idx}", fontsize=18)

def main():
    theme = {
        "bg": (0.95, 0.95, 0.95),
        "tab_bg": (0.2, 0.2, 0.4),
        "tab_bg_alt": (0.3, 0.3, 0.5),
        "tab_text": (1, 1, 1),
        "home_bg": (0.1, 0.1, 0.1),
        "home_text": (0.9, 0.8, 0.2)
    }

    planner = DigitalPlanner(width=600, height=800, theme=theme)
    planner.set_background_renderer(draw_bg)
    planner.set_index_renderer(draw_index)
    
    planner.add_section("notes", "NOT", 2, draw_notes)
    planner.add_section("tasks", "TSK", 3, draw_tasks)
    planner.add_section("goals", "GOL", 1, draw_goals)
    
    out_path = os.path.join(os.path.dirname(__file__), "test_framework_output.pdf")
    planner.build(out_path)

if __name__ == "__main__":
    main()
