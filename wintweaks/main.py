import tkinter as tk
from tkinter import ttk, messagebox

from . import win_api as api
from .tweaks import TWEAKS


# === Цветовая палитра ===
BG          = "#1a1a1a"   # основной фон
BG_SIDEBAR  = "#141414"   # сайдбар чуть темнее
BG_HEADER   = "#1f1f1f"
BG_FOOTER   = "#1f1f1f"
BG_CARD     = "#262626"   # карточка твика
BG_CARD_HOV = "#2f2f2f"   # карточка под курсором
FG          = "#e8e8e8"   # основной текст
FG_DIM      = "#9a9a9a"   # второстепенный текст
FG_TITLE    = "#ffffff"
ACCENT      = "#4a9eff"   # акцент (кнопка, выделение, подсветка)
ACCENT_HOV  = "#6ab0ff"
BORDER      = "#333333"
WARNING     = "#ffb84d"


# === Иконки категорий и твиков ===
CAT_ICONS = {
    "Проводник":    "📁",
    "Панель задач": "📌",
    "Внешний вид":  "🎨",
    "Приватность":  "🔒",
}

TWEAK_ICONS = {
    "hidden_files":      "👁️",
    "file_ext":          "📄",
    "this_pc":           "💻",
    "compact_mode":      "📦",
    "classic_menu":      "☰",
    "clock_seconds":     "⏱️",
    "hide_search":       "🔍",
    "hide_widgets":      "📊",
    "hide_copilot":      "🤖",
    "taskbar_left":      "⬅️",
    "dark_apps":         "🌙",
    "dark_system":       "🖤",
    "transparency":      "💧",
    "clipboard_history": "📋",
    "disable_adid":      "🚫",
    "disable_bing":      "🌐",
}


class WinTweaksApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinTweaks")
        self.root.geometry("900x660")
        self.root.minsize(780, 540)
        self.root.configure(bg=BG)

        self.vars = {}
        self._desc_labels = []
        self._setup_style()
        self._build_ui()
        self._load_state()

    # ------------------------------------------------------------------ style
    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')   # самый гибкий встроенный на Windows
        except tk.TclError:
            pass

        # Сайдбар-дерево
        style.configure("Sidebar.Treeview",
                        background=BG_SIDEBAR,
                        fieldbackground=BG_SIDEBAR,
                        foreground=FG,
                        rowheight=40,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.map("Sidebar.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#ffffff")])

        # Скроллбар
        style.configure("Dark.Vertical.TScrollbar",
                        background=BG_CARD,
                        troughcolor=BG,
                        bordercolor=BG,
                        arrowcolor=FG_DIM,
                        gripcount=0)
        style.map("Dark.Vertical.TScrollbar",
                  background=[("active", BG_CARD_HOV), ("pressed", ACCENT)])

    # --------------------------------------------------------------------- ui
    def _build_ui(self):
        # === Шапка ===
        header = tk.Frame(self.root, bg=BG_HEADER, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x", side="top")

        tk.Label(header, text="⚙   WinTweaks",
                 fg=FG_TITLE, bg=BG_HEADER,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)

        if not api.is_admin():
            tk.Label(header, text="⚠  не админ — часть твиков будет недоступна",
                     fg=WARNING, bg=BG_HEADER,
                     font=("Segoe UI", 9)).pack(side="right", padx=20)

        # === Тело ===
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # --- Сайдбар ---
        side = tk.Frame(body, bg=BG_SIDEBAR, width=220)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text="КАТЕГОРИИ",
                 fg=FG_DIM, bg=BG_SIDEBAR,
                 font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(20, 8))

        self.cats = ttk.Treeview(side, show="tree",
                                 style="Sidebar.Treeview",
                                 selectmode="browse")
        self.cats.pack(fill="both", expand=True, padx=8, pady=(0, 16))
        self.cats.bind("<<TreeviewSelect>>", self._on_cat)

        # --- Разделитель ---
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")

        # --- Правая панель ---
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(right, bg=BG,
                                highlightthickness=0, borderwidth=0)
        scroll = ttk.Scrollbar(right, orient="vertical",
                               style="Dark.Vertical.TScrollbar",
                               command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG)

        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True,
                         padx=(20, 0), pady=20)
        scroll.pack(side="right", fill="y", pady=20)

        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(
                                 int(-e.delta / 120), "units"))
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # === Подвал ===
        footer = tk.Frame(self.root, bg=BG_FOOTER, height=64)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", side="top")

        tk.Button(footer, text="Сбросить к дефолту",
                  bg=BG_FOOTER, fg=FG,
                  activebackground=BG_CARD, activeforeground=FG_TITLE,
                  font=("Segoe UI", 10),
                  relief="solid", bd=1,
                  padx=20, pady=10,
                  cursor="hand2",
                  command=self._reset).pack(side="right", padx=(0, 12), pady=14)

        tk.Button(footer, text="✓   Применить",
                  bg=ACCENT, fg="#ffffff",
                  activebackground=ACCENT_HOV, activeforeground="#ffffff",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", bd=0,
                  padx=24, pady=10,
                  cursor="hand2",
                  command=self._apply).pack(side="right", padx=(0, 12), pady=14)

        tk.Label(footer, text="Изменения применяются после нажатия «Применить»",
                 fg=FG_DIM, bg=BG_FOOTER,
                 font=("Segoe UI", 9)).pack(side="left", padx=20)

    # --------------------------------------------------------------- resize
    def _on_canvas_resize(self, event):
        wrap = max(300, event.width - 80)
        for lbl in self._desc_labels:
            try:
                lbl.configure(wraplength=wrap)
            except tk.TclError:
                pass

    # --------------------------------------------------------------- state
    def _load_state(self):
        for tw in TWEAKS:
            current = api.read_value(tw["hive"], tw["path"], tw["value"])
            is_on = False
            if current is not None and tw["on"] is not None:
                is_on = (current == tw["on"][0])
            self.vars[tw["id"]] = tk.BooleanVar(value=is_on)

        cats = ["Все"]
        for tw in TWEAKS:
            if tw["category"] not in cats:
                cats.append(tw["category"])
        for c in cats:
            icon = CAT_ICONS.get(c, "")
            display = f"  {icon}   {c}" if c != "Все" else f"  ✨   {c}"
            self.cats.insert("", "end", iid=c, text=display)

        self.cats.selection_set("Все")
        self._render("Все")

    def _on_cat(self, _event):
        sel = self.cats.selection()
        if sel:
            self._render(sel[0])

    # --------------------------------------------------------------- render
    def _render(self, category):
        for w in self.inner.winfo_children():
            w.destroy()
        self._desc_labels = []

        last_cat = None
        for tw in TWEAKS:
            if category != "Все" and tw["category"] != category:
                continue
            if category == "Все" and tw["category"] != last_cat:
                cat_icon = CAT_ICONS.get(tw["category"], "")
                tk.Label(self.inner,
                         text=f"{cat_icon}   {tw['category']}",
                         bg=BG, fg=FG,
                         font=("Segoe UI", 12, "bold"),
                         anchor="w").pack(fill="x", padx=4, pady=(18, 8))
                last_cat = tw["category"]

            card = self._make_card(self.inner, tw)
            card.pack(fill="x", pady=6)

    def _make_card(self, parent, tw):
        card = tk.Frame(parent, bg=BG_CARD,
                        highlightbackground=BORDER,
                        highlightthickness=1)

        widgets = [card]

        # верхняя строка: чекбокс справа, заголовок слева
        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x", padx=16, pady=(14, 4))
        widgets.append(top)

        icon = TWEAK_ICONS.get(tw["id"], "")
        title_text = f"{icon}   {tw['name']}" if icon else tw["name"]

        title = tk.Label(top, text=title_text, bg=BG_CARD, fg=FG,
                         font=("Segoe UI", 10, "bold"),
                         anchor="w")
        title.pack(side="left", fill="x", expand=True)
        widgets.append(title)

        ttk.Checkbutton(top, variable=self.vars[tw["id"]]).pack(
            side="right", padx=(8, 0))

        desc = tk.Label(card, text=tw["desc"], bg=BG_CARD, fg=FG_DIM,
                        font=("Segoe UI", 9), anchor="w",
                        wraplength=600, justify="left")
        desc.pack(fill="x", padx=16, pady=(0, 14))
        widgets.append(desc)
        self._desc_labels.append(desc)

        # hover — привязка только к карточке, проверяем, что курсор реально вышел
        def set_hover(state):
            color = BG_CARD_HOV if state else BG_CARD
            for w in widgets:
                try:
                    w.configure(bg=color)
                except tk.TclError:
                    pass

        def on_enter(_e):
            set_hover(True)

        def on_leave(e):
            x1 = card.winfo_rootx()
            y1 = card.winfo_rooty()
            x2 = x1 + card.winfo_width()
            y2 = y1 + card.winfo_height()
            if x1 <= e.x_root < x2 and y1 <= e.y_root < y2:
                return  # курсор ушёл на дочерний виджет внутри карточки
            set_hover(False)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        return card

    # --------------------------------------------------------------- actions
    def _apply(self):
        changed = 0
        need_explorer = False
        for tw in TWEAKS:
            want_on = self.vars[tw["id"]].get()
            current = api.read_value(tw["hive"], tw["path"], tw["value"])

            target = tw["on"] if want_on else tw["off"]
            if target is None:
                if current is not None:
                    api.delete_value(tw["hive"], tw["path"], tw["value"])
                    changed += 1
                    if tw.get("restart") == "explorer":
                        need_explorer = True
                continue

            value, vtype = target
            if current != value:
                try:
                    api.write_value(tw["hive"], tw["path"], tw["value"], value, vtype)
                    changed += 1
                    if tw.get("restart") == "explorer":
                        need_explorer = True
                except PermissionError:
                    messagebox.showwarning(
                        "Нет прав",
                        f"«{tw['name']}» требует прав администратора.")
        if need_explorer:
            try:
                api.restart_explorer()
            except Exception:
                pass
        messagebox.showinfo("Готово", f"Применено изменений: {changed}")

    def _reset(self):
        if not messagebox.askyesno("Сброс", "Сбросить все твики к дефолту?"):
            return
        for tw in TWEAKS:
            try:
                if tw["off"] is not None:
                    value, vtype = tw["off"]
                    api.write_value(tw["hive"], tw["path"], tw["value"], value, vtype)
                else:
                    api.delete_value(tw["hive"], tw["path"], tw["value"])
            except PermissionError:
                pass
        self._load_state()
        try:
            api.restart_explorer()
        except Exception:
            pass


def main():
    root = tk.Tk()
    WinTweaksApp(root)
    root.mainloop()