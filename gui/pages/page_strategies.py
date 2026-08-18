"""
page_strategies.py — Halaman 8: Library Strategi (Markdown Viewer).
"""

import customtkinter as ctk
import os
from pathlib import Path
from gui.theme import COLORS, FONTS, button_secondary


STRATEGIES_DIR = Path(__file__).parent.parent.parent / "src" / "strategies"


class PageStrategies(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self._files = []
        self._current_file = None
        self._build()
        self._load_file_list()

    def _build(self):
        ctk.CTkLabel(self, text="📚  Library Strategi",
                     font=FONTS["title_xl"], text_color=COLORS["text_primary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(20, 4))
        ctk.CTkLabel(self, text="7 strategi trading terdokumentasi. Read-only — panduan untuk memahami kondisi optimal setiap strategi.",
                     font=FONTS["body_md"], text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", padx=20, pady=(0, 16))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # ── File List (left sidebar) ──────────────────────────────────────────
        sidebar = ctk.CTkFrame(main, fg_color=COLORS["bg_secondary"], corner_radius=10,
                                border_width=1, border_color=COLORS["border"], width=220)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="STRATEGI", font=FONTS["nav_header"],
                     text_color=COLORS["text_muted"]).pack(padx=12, pady=(12, 8), anchor="w")

        self._file_list_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                                        scrollbar_button_color=COLORS["bg_hover"])
        self._file_list_frame.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        # ── Content viewer (right) ────────────────────────────────────────────
        content_frame = ctk.CTkFrame(main, fg_color=COLORS["bg_card"], corner_radius=10,
                                      border_width=1, border_color=COLORS["border"])
        content_frame.grid(row=0, column=1, sticky="nsew")

        # Content header
        self._content_title = ctk.CTkLabel(content_frame, text="Pilih strategi di sebelah kiri",
                                            font=FONTS["title_md"], text_color=COLORS["accent_blue"], anchor="w")
        self._content_title.pack(padx=16, pady=(16, 4), anchor="w")

        sep = ctk.CTkFrame(content_frame, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=16, pady=(0, 8))

        # Textbox for markdown content
        self._content_box = ctk.CTkTextbox(
            content_frame,
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_md"],
            wrap="word",
        )
        self._content_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _load_file_list(self):
        if not STRATEGIES_DIR.exists():
            return

        md_files = sorted(STRATEGIES_DIR.glob("*.md"))
        self._files = md_files

        for f in md_files:
            btn = ctk.CTkButton(
                self._file_list_frame,
                text=f"📋  {f.stem}",
                command=lambda file=f: self._show_file(file),
                height=38, anchor="w",
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_secondary"],
                corner_radius=6,
                font=FONTS["nav_item"],
            )
            btn.pack(fill="x", pady=2)

        # Auto-select first
        if md_files:
            self._show_file(md_files[0])

    def _show_file(self, file: Path):
        self._current_file = file
        self._content_title.configure(text=f"📋  {file.stem}")

        try:
            content = file.read_text(encoding="utf-8")
        except Exception as e:
            content = f"❌ Gagal membaca file: {e}"

        # Render sebagai plain text (markdown tidak di-render visual, tapi tetap terbaca)
        self._content_box.configure(state="normal")
        self._content_box.delete("1.0", "end")

        # Simple formatting: header lines
        for line in content.splitlines(keepends=True):
            if line.startswith("# "):
                self._content_box.insert("end", line.lstrip("# "), "h1")
            elif line.startswith("## "):
                self._content_box.insert("end", line.lstrip("# "), "h2")
            elif line.startswith("### "):
                self._content_box.insert("end", line.lstrip("# "), "h3")
            elif line.startswith("- ") or line.startswith("* "):
                self._content_box.insert("end", "  • " + line[2:])
            elif line.startswith("```"):
                self._content_box.insert("end", line)
            else:
                self._content_box.insert("end", line)

        self._content_box.configure(state="disabled")
