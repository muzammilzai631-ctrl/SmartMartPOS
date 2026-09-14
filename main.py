import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime
from collections import defaultdict

DATA_FILE = "mart_app_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"items": {}, "sales": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class ModernMartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Mart POS")
        self.geometry("420x720")
        self.configure(bg="#F1F5F9")

        self.data = load_data()

        # Top Header Bar
        self.top_bar = tk.Frame(self, bg="#0F172A", height=60)
        self.top_bar.pack(fill="x", side="top")

        self.menu_btn = tk.Button(self.top_bar, text=" ☰ ", font=('Segoe UI', 15, 'bold'),
                                  bg="#0F172A", fg="#F8FAFC", bd=0, activebackground="#1E293B",
                                  activeforeground="#F8FAFC", command=self.toggle_drawer)
        self.menu_btn.pack(side="left", padx=12, pady=10)

        self.title_label = tk.Label(self.top_bar, text="POS Terminal", font=('Segoe UI', 13, 'bold'),
                                    bg="#0F172A", fg="#F8FAFC")
        self.title_label.pack(side="left", padx=5)

        # Main Container
        self.container = tk.Frame(self, bg="#F1F5F9")
        self.container.pack(fill="both", expand=True)

        # Side Navigation Drawer
        self.drawer_open = False
        self.drawer = tk.Frame(self, bg="#1E293B")

        nav_items = [
            ("[ POS ]   POS Terminal", self.show_sell),
            ("[ BOX ]   Inventory & Stock", self.show_stock),
            ("[ TODAY ] Analytics & Sales", self.show_reports),
            ("[ TOP ]   Top & Low Sales", self.show_top_low_sales),
            ("[ HIST ]  Monthly History", self.show_monthly_history),
            ("[ + ]     Add New Product", self.show_add_item),
            ("[ INFO ]  About App", self.show_about),
            ("[ RESET ] Reset Entire App", self.reset_entire_app)
        ]

        d_head = tk.Frame(self.drawer, bg="#0F172A", height=70)
        d_head.pack(fill="x")
        tk.Label(d_head, text="SMART MART", font=('Segoe UI', 12, 'bold'), bg="#0F172A", fg="#38BDF8").pack(anchor="w", padx=20, pady=20)

        for text, command in nav_items:
            bg_color = "#1E293B"
            fg_color = "#E2E8F0"
            if "[ RESET ]" in text:
                fg_color = "#EF4444"

            btn = tk.Button(self.drawer, text=text, font=('Segoe UI', 10, 'bold'), bg=bg_color, fg=fg_color,
                            bd=0, anchor="w", activebackground="#334155", activeforeground="#FFFFFF",
                            padx=20, pady=10, command=lambda c=command: self.navigate(c))
            btn.pack(fill="x")

        self.current_frame = None
        self.show_sell()

    def toggle_drawer(self):
        if self.drawer_open:
            self.drawer.place_forget()
            self.drawer_open = False
        else:
            self.drawer.place(x=0, y=60, relheight=1.0, relwidth=0.75)
            self.drawer.lift()
            self.drawer_open = True

    def navigate(self, command):
        self.toggle_drawer()
        command()

    def set_active_view(self, frame, title):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)
        self.title_label.config(text=title)

    # --- 1. POS TERMINAL ---
    def show_sell(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        canvas = tk.Canvas(view, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#F1F5F9")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        scroll_content.columnconfigure(0, weight=1, uniform="group1")
        scroll_content.columnconfigure(1, weight=1, uniform="group1")

        row_idx = 0
        col_idx = 0

        for name, info in self.data["items"].items():
            unit = info.get("unit", "kg")

            card = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#CBD5E1")
            card.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

            tk.Label(card, text=name.title(), font=('Segoe UI', 10, 'bold'), bg="#FFFFFF", fg="#0F172A", anchor="w").pack(fill="x", padx=6, pady=(6, 2))
            tk.Label(card, text=f"Rs. {info['sale_price']:.2f} /{unit}", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#2563EB", anchor="w").pack(fill="x", padx=6, pady=1)

            stock_color = "#16A34A" if info['stock'] >= 15 else ("#D97706" if info['stock'] > 0 else "#DC2626")
            tk.Label(card, text=f"Stock: {info['stock']} {unit}", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg=stock_color, anchor="w").pack(fill="x", padx=6, pady=(0, 4))

            act_frame = tk.Frame(card, bg="#FFFFFF")
            act_frame.pack(fill="x", padx=6, pady=(0, 6))

            tk.Label(act_frame, text="Qty:", font=('Segoe UI', 8), bg="#FFFFFF").pack(side="left")
            qty_ent = tk.Entry(act_frame, width=4, font=('Segoe UI', 8), justify="center", bd=1, relief="solid")
            qty_ent.pack(side="left", padx=2)
            qty_ent.insert(0, "1" if unit == "packet" else "1.0")

            btn = tk.Button(act_frame, text="Checkout", font=('Segoe UI', 8, 'bold'), bg="#2563EB", fg="white", bd=0, padx=4, pady=2,
                            command=lambda n=name, q=qty_ent: self.process_sale(n, q.get()))
            btn.pack(side="right")

            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.set_active_view(view, "POS Terminal")

    def process_sale(self, item_name, qty_str):
        try:
            item = self.data["items"][item_name]
            unit = item.get("unit", "kg")
            qty = float(qty_str) if unit == "kg" else int(qty_str)

            if qty <= 0:
                raise ValueError

            if item["stock"] < qty:
                messagebox.showwarning("Stock Low", f"Only {item['stock']} {unit} left.")
                return

            item["stock"] = round(item["stock"] - qty, 2)
            today = datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.now().strftime("%H:%M:%S")
            sale_amount = round(qty * item["sale_price"], 2)
            profit = round(qty * (item["sale_price"] - item["cost_price"]), 2)

            if today not in self.data["sales"]:
                self.data["sales"][today] = []

            self.data["sales"][today].append({
                "item": item_name, "qty": qty, "unit": unit,
                "amount": sale_amount, "profit": profit, "time": time_str
            })
            save_data(self.data)
            messagebox.showinfo("Success", f"Sold {qty} {unit} of {item_name}\nTotal: Rs. {sale_amount:.2f}")
            self.show_sell()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid quantity.")

    # --- 2. INVENTORY & STOCK ---
    def show_stock(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        canvas = tk.Canvas(view, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#F1F5F9")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        for name, info in self.data["items"].items():
            unit = info.get("unit", "kg")
            card = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
            card.pack(fill="x", padx=8, pady=6)

            header_frame = tk.Frame(card, bg="#FFFFFF")
            header_frame.pack(fill="x", padx=10, pady=(8, 2))

            tk.Label(header_frame, text=f"{name.title()} ({unit})", font=('Segoe UI', 10, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(side="left")
            
            if info["stock"] < 15:
                tk.Label(header_frame, text="[ LOW STOCK ]", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#DC2626").pack(side="right")

            stock_fg = "#DC2626" if info['stock'] < 15 else "#16A34A"
            tk.Label(card, text=f"Stock: {info['stock']} {unit}", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg=stock_fg).pack(anchor="w", padx=10, pady=(0, 4))

            f = tk.Frame(card, bg="#FFFFFF")
            f.pack(fill="x", padx=10, pady=4)

            tk.Label(f, text="Cost:", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(side="left")
            cost_e = tk.Entry(f, width=6, bd=1, relief="solid", font=('Segoe UI', 8))
            cost_e.insert(0, str(info["cost_price"]))
            cost_e.pack(side="left", padx=(2, 6))

            tk.Label(f, text="Sale:", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(side="left")
            sale_e = tk.Entry(f, width=6, bd=1, relief="solid", font=('Segoe UI', 8))
            sale_e.insert(0, str(info["sale_price"]))
            sale_e.pack(side="left", padx=(2, 6))

            tk.Label(f, text="+Add:", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(side="left")
            add_e = tk.Entry(f, width=4, bd=1, relief="solid", font=('Segoe UI', 8))
            add_e.insert(0, "0")
            add_e.pack(side="left", padx=2)

            bt_bar = tk.Frame(card, bg="#F8FAFC", padx=10, pady=4)
            bt_bar.pack(fill="x", pady=(4, 0))

            btn_del = tk.Button(bt_bar, text="Delete Item", font=('Segoe UI', 8, 'bold'), bg="#DC2626", fg="white", bd=0, padx=8, pady=3,
                                activebackground="#B91C1C", activeforeground="white", command=lambda n=name: self.delete_item(n))
            btn_del.pack(side="left")

            btn_save = tk.Button(bt_bar, text="Save Changes", font=('Segoe UI', 8, 'bold'), bg="#0284C7", fg="white", bd=0, padx=8, pady=3,
                                 command=lambda n=name, c=cost_e, s=sale_e, a=add_e: self.update_stock(n, c.get(), s.get(), a.get()))
            btn_save.pack(side="right")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.set_active_view(view, "Inventory & Stock")

    def update_stock(self, name, cost, sale, add_stock):
        try:
            item = self.data["items"][name]
            item["cost_price"] = float(cost)
            item["sale_price"] = float(sale)
            item["stock"] = round(item["stock"] + float(add_stock), 2)
            save_data(self.data)
            messagebox.showinfo("Success", f"'{name}' updated successfully.")
            self.show_stock()
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers.")

    def delete_item(self, item_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Kya aap '{item_name.title()}' ko delete karna chahte hain?")
        if confirm:
            if item_name in self.data["items"]:
                del self.data["items"][item_name]
                save_data(self.data)
                messagebox.showinfo("Deleted", f"'{item_name.title()}' delete ho chuka hai.")
                self.show_stock()

    # --- 3. ANALYTICS & SALES (TODAY) ---
    def show_reports(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        today_str = datetime.now().strftime("%Y-%m-%d")

        today_sales = self.data["sales"].get(today_str, [])
        today_rev = sum(s["amount"] for s in today_sales)
        today_prof = sum(s["profit"] for s in today_sales)

        metrics_f = tk.Frame(view, bg="#F1F5F9")
        metrics_f.pack(fill="x", padx=10, pady=10)

        card_rev = tk.Frame(metrics_f, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
        card_rev.pack(fill="x", pady=4)
        tk.Label(card_rev, text="TODAY'S REVENUE", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(card_rev, text=f"Rs. {today_rev:,.2f}", font=('Segoe UI', 14, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(anchor="w", padx=10, pady=(0, 8))

        card_prof = tk.Frame(metrics_f, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
        card_prof.pack(fill="x", pady=4)
        tk.Label(card_prof, text="TODAY'S PROFIT", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(card_prof, text=f"Rs. {today_prof:,.2f}", font=('Segoe UI', 14, 'bold'), bg="#FFFFFF", fg="#16A34A").pack(anchor="w", padx=10, pady=(0, 8))

        tk.Label(view, text="TODAY'S TRANSACTIONS", font=('Segoe UI', 9, 'bold'), bg="#F1F5F9", fg="#475569").pack(anchor="w", padx=12, pady=(10, 4))

        canvas = tk.Canvas(view, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#F1F5F9")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        for sale in reversed(today_sales):
            c = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
            c.pack(fill="x", padx=10, pady=3)

            t_info = f" ({sale['time']})" if "time" in sale else ""
            tk.Label(c, text=f"{sale['item'].title()} ({sale['qty']} {sale['unit']}){t_info}", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(side="left", padx=8, pady=6)
            tk.Label(c, text=f"Rs. {sale['amount']:.2f}", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#16A34A").pack(side="right", padx=8, pady=6)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.set_active_view(view, "Analytics & Sales")

    # --- 4. TOP (>10) & LOW (<5) SALES VIEW ---
    def show_top_low_sales(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        canvas = tk.Canvas(view, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#F1F5F9")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        item_sales_count = {name: 0.0 for name in self.data["items"].keys()}
        item_units = {name: info.get("unit", "kg") for name, info in self.data["items"].items()}

        for date_sales in self.data["sales"].values():
            for s in date_sales:
                item_name = s["item"]
                if item_name in item_sales_count:
                    item_sales_count[item_name] += s["qty"]
                else:
                    item_sales_count[item_name] = s["qty"]
                    item_units[item_name] = s.get("unit", "kg")

        high_sold = [(name, qty) for name, qty in item_sales_count.items() if qty > 10]
        high_sold = sorted(high_sold, key=lambda x: x[1], reverse=True)

        low_sold = [(name, qty) for name, qty in item_sales_count.items() if qty < 5]
        low_sold = sorted(low_sold, key=lambda x: x[1])

        tk.Label(scroll_content, text="[TOP] HIGH SALES ITEMS ( > 10 Sold )", font=('Segoe UI', 10, 'bold'), bg="#F1F5F9", fg="#16A34A").pack(anchor="w", padx=12, pady=(12, 4))
        
        if high_sold:
            for rank, (name, qty) in enumerate(high_sold, 1):
                c = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
                c.pack(fill="x", padx=10, pady=3)
                unit = item_units.get(name, "")
                tk.Label(c, text=f"#{rank} {name.title()}", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(side="left", padx=8, pady=6)
                tk.Label(c, text=f"{qty} {unit} Sold", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#16A34A").pack(side="right", padx=8, pady=6)
        else:
            tk.Label(scroll_content, text="No items with > 10 sales", font=('Segoe UI', 8, 'italic'), bg="#F1F5F9", fg="#64748B").pack(anchor="w", padx=16, pady=2)

        tk.Label(scroll_content, text="[LOW] LOW SALES ITEMS ( < 5 Sold )", font=('Segoe UI', 10, 'bold'), bg="#F1F5F9", fg="#DC2626").pack(anchor="w", padx=12, pady=(16, 4))

        if low_sold:
            for rank, (name, qty) in enumerate(low_sold, 1):
                c = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
                c.pack(fill="x", padx=10, pady=3)
                unit = item_units.get(name, "")
                tk.Label(c, text=f"#{rank} {name.title()}", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(side="left", padx=8, pady=6)
                tk.Label(c, text=f"{qty} {unit} Sold", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#DC2626").pack(side="right", padx=8, pady=6)
        else:
            tk.Label(scroll_content, text="No items with < 5 sales", font=('Segoe UI', 8, 'italic'), bg="#F1F5F9", fg="#64748B").pack(anchor="w", padx=16, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.set_active_view(view, "Top & Low Sales")

    # --- 5. MONTHLY HISTORY & RESET ---
    def show_monthly_history(self):
        view = tk.Frame(self.container, bg="#F1F5F9")

        current_month = datetime.now().strftime("%Y-%m")
        month_rev = 0
        month_prof = 0

        for date_str, sales_list in self.data["sales"].items():
            if date_str.startswith(current_month):
                month_rev += sum(s["amount"] for s in sales_list)
                month_prof += sum(s["profit"] for s in sales_list)

        top_h = tk.Frame(view, bg="#F1F5F9")
        top_h.pack(fill="x", padx=10, pady=8)

        card_m = tk.Frame(top_h, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
        card_m.pack(fill="x", pady=4)

        f_data = tk.Frame(card_m, bg="#FFFFFF")
        f_data.pack(fill="x", padx=10, pady=8)

        tk.Label(f_data, text="THIS MONTH TOTAL", font=('Segoe UI', 8, 'bold'), bg="#FFFFFF", fg="#64748B").pack(anchor="w")
        tk.Label(f_data, text=f"Revenue: Rs. {month_rev:,.2f}  |  Profit: Rs. {month_prof:,.2f}", font=('Segoe UI', 10, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(anchor="w", pady=(2, 0))

        btn_reset = tk.Button(top_h, text="Reset Month History", font=('Segoe UI', 9, 'bold'), bg="#DC2626", fg="white", bd=0, pady=6,
                              activebackground="#B91C1C", activeforeground="white", command=self.reset_history)
        btn_reset.pack(fill="x", pady=(4, 8))

        tk.Label(view, text="PAST DAYS RECORD", font=('Segoe UI', 9, 'bold'), bg="#F1F5F9", fg="#475569").pack(anchor="w", padx=12, pady=(0, 4))

        canvas = tk.Canvas(view, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(view, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#F1F5F9")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        sorted_dates = sorted(self.data["sales"].keys(), reverse=True)
        for date_str in sorted_dates:
            day_sales = self.data["sales"][date_str]
            day_tot = sum(s["amount"] for s in day_sales)
            day_pr = sum(s["profit"] for s in day_sales)

            hist_card = tk.Frame(scroll_content, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#E2E8F0")
            hist_card.pack(fill="x", padx=10, pady=3)

            h_head = tk.Frame(hist_card, bg="#F8FAFC")
            h_head.pack(fill="x", padx=8, pady=6)
            tk.Label(h_head, text=date_str, font=('Segoe UI', 9, 'bold'), bg="#F8FAFC", fg="#0F172A").pack(side="left")
            tk.Label(h_head, text=f"Total: Rs. {day_tot:,.2f} | Profit: Rs. {day_pr:,.2f}", font=('Segoe UI', 8, 'bold'), bg="#F8FAFC", fg="#16A34A").pack(side="right")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.set_active_view(view, "Monthly History")

    def reset_history(self):
        confirm = messagebox.askyesno("Confirm Reset", "Kya aap purani tamam Sales History delete karke record reset karna chahte hain?")
        if confirm:
            self.data["sales"] = {}
            save_data(self.data)
            messagebox.showinfo("Reset Successful", "Tamam Sales record clear ho gaya hai!")
            self.show_monthly_history()

    # --- 6. ADD ITEM VIEW ---
    def show_add_item(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        f = tk.Frame(view, bg="#FFFFFF", padx=15, pady=15, bd=1, relief="solid", highlightbackground="#E2E8F0")
        f.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(f, text="Product Name", bg="#FFFFFF", fg="#334155", font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 2))
        name_e = tk.Entry(f, font=('Segoe UI', 10), bd=1, relief="solid")
        name_e.pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Unit Measurement", bg="#FFFFFF", fg="#334155", font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 2))
        unit_cb = ttk.Combobox(f, values=["kg", "packet"], state="readonly", font=('Segoe UI', 9))
        unit_cb.set("kg")
        unit_cb.pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Cost Price (Rs)", bg="#FFFFFF", fg="#334155", font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 2))
        cost_e = tk.Entry(f, font=('Segoe UI', 10), bd=1, relief="solid")
        cost_e.pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Selling Price (Rs)", bg="#FFFFFF", fg="#334155", font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 2))
        sale_e = tk.Entry(f, font=('Segoe UI', 10), bd=1, relief="solid")
        sale_e.pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Initial Stock", bg="#FFFFFF", fg="#334155", font=('Segoe UI', 9, 'bold')).pack(anchor="w", pady=(0, 2))
        stock_e = tk.Entry(f, font=('Segoe UI', 10), bd=1, relief="solid")
        stock_e.pack(fill="x", pady=(0, 15))

        def save_item():
            name = name_e.get().strip().lower()
            if not name:
                messagebox.showerror("Error", "Product name required.")
                return
            try:
                self.data["items"][name] = {
                    "unit": unit_cb.get(),
                    "cost_price": float(cost_e.get() or 0),
                    "sale_price": float(sale_e.get() or 0),
                    "stock": float(stock_e.get() or 0)
                }
                save_data(self.data)
                messagebox.showinfo("Success", f"'{name.title()}' added.")
                self.show_sell()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.")

        btn_save = tk.Button(f, text="Add Product", font=('Segoe UI', 10, 'bold'), bg="#16A34A", fg="white", bd=0, pady=8,
                             activebackground="#15803D", activeforeground="white", command=save_item)
        btn_save.pack(fill="x", pady=10)

        self.set_active_view(view, "Add New Product")

    # --- 7. ABOUT SECTION ---
    def show_about(self):
        view = tk.Frame(self.container, bg="#F1F5F9")
        
        main_card = tk.Frame(view, bg="#FFFFFF", padx=15, pady=15, bd=1, relief="solid", highlightbackground="#CBD5E1")
        main_card.pack(fill="both", expand=True, padx=14, pady=14)

        # Header Title
        tk.Label(main_card, text="Smart Mart POS", font=('Segoe UI', 16, 'bold'), bg="#FFFFFF", fg="#0F172A").pack(anchor="w", pady=(0, 2))
        tk.Label(main_card, text="Version 2.0", font=('Segoe UI', 9, 'bold'), bg="#FFFFFF", fg="#0284C7").pack(anchor="w", pady=(0, 12))

        # Developer Section
        dev_frame = tk.Frame(main_card, bg="#F8FAFC", bd=1, relief="solid", highlightbackground="#E2E8F0", padx=10, pady=10)
        dev_frame.pack(fill="x", pady=(0, 10))

        tk.Label(dev_frame, text="DEVELOPMENT TEAM", font=('Segoe UI', 8, 'bold'), bg="#F8FAFC", fg="#64748B").pack(anchor="w")
        tk.Label(dev_frame, text="Muzammil-IoT & Gemini", font=('Segoe UI', 11, 'bold'), bg="#F8FAFC", fg="#0F172A").pack(anchor="w", pady=(2, 0))

        # Purpose Section
        purp_frame = tk.Frame(main_card, bg="#F8FAFC", bd=1, relief="solid", highlightbackground="#E2E8F0", padx=10, pady=10)
        purp_frame.pack(fill="x", pady=(0, 10))

        tk.Label(purp_frame, text="APP PURPOSE", font=('Segoe UI', 8, 'bold'), bg="#F8FAFC", fg="#64748B").pack(anchor="w")
        purp_text = (
            "Smart POS system for quick billing checkout, real-time inventory "
            "tracking, and daily/monthly sales analytics."
        )
        tk.Label(purp_frame, text=purp_text, font=('Segoe UI', 9), bg="#F8FAFC", fg="#334155", justify="left", wraplength=320).pack(anchor="w", pady=(4, 0))

        # Key Features Section
        feat_frame = tk.Frame(main_card, bg="#F8FAFC", bd=1, relief="solid", highlightbackground="#E2E8F0", padx=10, pady=10)
        feat_frame.pack(fill="x")

        tk.Label(feat_frame, text="KEY FEATURES", font=('Segoe UI', 8, 'bold'), bg="#F8FAFC", fg="#64748B").pack(anchor="w", pady=(0, 4))
        
        features = [
            "• POS Terminal with multi-unit support (kg / pkt)",
            "• Top & Low Sales Analytics",
            "• Real-time stock alerts & updates",
            "• Daily revenue and profit tracking",
            "• Monthly sales history"
        ]
        for f in features:
            tk.Label(feat_frame, text=f, font=('Segoe UI', 8), bg="#F8FAFC", fg="#334155", anchor="w").pack(fill="x", pady=1)

        self.set_active_view(view, "About App")

    # --- 8. RESET ENTIRE APP ---
    def reset_entire_app(self):
        confirm = messagebox.askyesno(
            "⚠️ FACTORY RESET APP",
            "Kya aap poori app ko reset karna chahte hain?\n\n"
            "Is se saare products, stock, sales history clear ho jayenge aur app bilkul new ho jayegi!"
        )
        if confirm:
            self.data = {"items": {}, "sales": {}}
            save_data(self.data)
            messagebox.showinfo("Reset Complete", "App completely reset ho chuki hai!")
            self.show_sell()

if __name__ == "__main__":
    app = ModernMartApp()
    app.mainloop()
