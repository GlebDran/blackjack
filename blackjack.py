# Объединённый модуль: сначала оплата, затем игра Blackjack

import tkinter as tk
import requests
import json
import base64
import webbrowser
from tkinter import messagebox
from datetime import datetime
import random
import string
import smtplib
from email.mime.text import MIMEText
import re
import os
from PIL import Image, ImageTk

# EveryPay данные
API_URL = "https://igw-demo.every-pay.com/api/v4/payments/oneoff"
API_AUTH = "ZTM2ZWI0MGY1ZWM4N2ZhMjo3YjkxYTNiOWUxYjc0NTI0YzJlOWZjMjgyZjhhYzhjZA=="
API_USERNAME = "e36eb40f5ec87fa2"
ACCOUNT_NAME = "EUR3D1"
CUSTOMER_URL = "https://maksmine.web.app/makse"

payment_reference = ""
user_email = ""
user_balance = 0.0

# Карточные масти
SUITS = ["♥", "♦", "♣", "♠"]
CARD_VALUES = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "A"}

# Генерация nonce
def generate_nonce(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Отправка email
def saada_email(to_email, payment_reference):
    sender = "glebdranitsyn@gmail.com"
    password = "oeid ycrk uwit tnpk"
    content = f"Tere!\n\nTeie makse (ID: {payment_reference}) õnnestus edukalt.\n\nAitäh!"
    msg = MIMEText(content)
    msg["Subject"] = "Makse kinnitamine"
    msg["From"] = sender
    msg["To"] = to_email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("E-maili saatmise viga:", e)

# Лог платежей
def logi_makse(payment_reference, status):
    with open("maksete_logi.txt", "a", encoding="utf-8") as file:
        file.write(f"{datetime.now()} - {payment_reference} - {status}\n")

# Валидация e-mail
def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# Старт игры после успешной оплаты
def start_blackjack(balance):
    root = tk.Tk()
    game = BlackjackGame(root, balance)
    root.mainloop()

# Проверка платежа и запуск игры
def kontrolli_makset():
    global payment_reference, user_email
    if not payment_reference:
        messagebox.showerror("Ошибка", "Сначала нужно создать платёж.")
        return

    status_url = f"https://igw-demo.every-pay.com/api/v4/payments/{payment_reference}?api_username={API_USERNAME}"
    headers = {"Authorization": f"Basic {API_AUTH}"}
    response = requests.get(status_url, headers=headers)

    if response.status_code == 200:
        makse_info = response.json()
        seisund = makse_info.get("payment_state")
        amount = float(makse_info.get("initial_amount", 0))
        logi_makse(payment_reference, seisund)
        if seisund == "settled":
            saada_email("glebdranitsyn@gmail.com", payment_reference)
            saada_email(user_email, payment_reference)
            messagebox.showinfo("Makse kinnitatud", "Makse oli edukas. Avame mängu!")
            app.destroy()
            start_blackjack(amount)
        else:
            messagebox.showinfo("Статус платежа", f"Staatus: {seisund}")
    else:
        messagebox.showerror("Ошибка", f"Не удалось проверить платёж: {response.text}")

# Создание платежа
def create_payment():
    global payment_reference, user_email
    amount = amount_entry.get().strip()
    user_email = email_entry.get().strip()

    if not amount or not amount.replace(".", "", 1).isdigit():
        messagebox.showerror("Ошибка", "Введите корректную сумму")
        return

    if not validate_email(user_email):
        messagebox.showerror("Ошибка", "Введите корректный e-mail")
        return

    data = {
        "api_username": API_USERNAME,
        "account_name": ACCOUNT_NAME,
        "amount": amount,
        "order_reference": str(random.randint(100000, 999999)),
        "nonce": generate_nonce(),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "customer_url": CUSTOMER_URL
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {API_AUTH}"
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        payment_info = response.json()
        payment_reference = payment_info["payment_reference"]
        payment_link = payment_info["payment_link"]
        messagebox.showinfo("Оплата", f"Перенаправляем вас на оплату.\nСсылка: {payment_link}")
        webbrowser.open(payment_link)
    else:
        messagebox.showerror("Ошибка", f"Не удалось создать платёж: {response.status_code}\n{response.text}")

# GUI оплаты
app = tk.Tk()
app.title("Оплата через EveryPay")
app.geometry("400x300")

tk.Label(app, text="Введите сумму для оплаты:", font=("Arial", 12)).pack(pady=5)
amount_entry = tk.Entry(app, font=("Arial", 14))
amount_entry.pack(pady=5)

tk.Label(app, text="Введите ваш e-mail:", font=("Arial", 12)).pack(pady=5)
email_entry = tk.Entry(app, font=("Arial", 14))
email_entry.pack(pady=5)

tk.Button(app, text="Оплатить", font=("Arial", 14), command=create_payment, bg="green", fg="white").pack(pady=10)
tk.Button(app, text="Проверить статус", font=("Arial", 14), command=kontrolli_makset, bg="blue", fg="white").pack(pady=10)

# Класс игры (тот же, что и раньше, но встраивается внутрь)
class BlackjackGame:
    def __init__(self, root, initial_balance):
        global user_balance
        user_balance = initial_balance

        self.root = root
        self.root.title("Gleb Casino")
        self.root.geometry("500x700")
        self.root.configure(bg="green")

        self.name_label = tk.Label(root, text="Sisesta oma nimi:", bg="green", fg="black", font=("Times New Roman", 20, "bold"))
        self.name_label.pack()
        self.name_entry = tk.Entry(root, font=("Times New Roman", 20))
        self.name_entry.pack()

        self.balance_label = tk.Label(root, text=f"Sinu saldo: {user_balance:.2f} €", font=("Times New Roman", 16, "bold"), bg="green", fg="white")
        self.balance_label.pack(pady=5)

        self.label = tk.Label(root, text="Vajuta 'Alusta mängu'", font=("Times New Roman", 15, "bold"), bg="green", fg="yellow")
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Alusta mängu", command=self.start_game, font=("Times New Roman", 15), bg="white")
        self.start_button.pack(pady=5)

        self.hit_button = tk.Button(root, text="Võta kaart", command=self.hit, state=tk.DISABLED, font=("Times New Roman", 15), bg="white")
        self.hit_button.pack(pady=5)

        self.stand_button = tk.Button(root, text="Peatu", command=self.stand, state=tk.DISABLED, font=("Times New Roman", 15), bg="white")
        self.stand_button.pack(pady=5)

        self.history_button = tk.Button(root, text="Vaata ajalugu", command=self.show_history, font=("Times New Roman", 15), bg="white")
        self.history_button.pack(pady=5)

        self.result_label = tk.Label(root, text="", font=("Times New Roman", 15, "bold"), bg="green", fg="white")
        self.result_label.pack(pady=10)

        self.player_cards_label = tk.Label(root, text="", font=("Times New Roman", 20), bg="green", fg="black")
        self.player_cards_label.pack(pady=5)

        self.computer_cards_label = tk.Label(root, text="", font=("Times New Roman", 20), bg="green", fg="black")
        self.computer_cards_label.pack(pady=5)

        self.deck_label = tk.Label(root, text="", font=("Times New Roman", 15), bg="green", fg="white")
        self.deck_label.pack(pady=5)

        self.history_text = tk.Text(root, height=10, width=50, state=tk.DISABLED, font=("Times New Roman", 15))
        self.history_text.pack(pady=10)

        self.player_cards = []
        self.computer_cards = []

        if user_balance < 1:
            self.start_button.config(state=tk.DISABLED)
            self.label.config(text="Pole piisavalt saldo mängu alustamiseks.", fg="red")

    def start_game(self):
        global user_balance
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            self.label.config(text="Palun sisesta oma nimi!", fg="red")
            return

        if user_balance < 1:
            self.label.config(text="Pole piisavalt saldo mängimiseks.", fg="red")
            return

        user_balance -= 1
        self.balance_label.config(text=f"Sinu saldo: {user_balance:.2f} €")

        self.deck = [(value, suit) for value in CARD_VALUES for suit in SUITS]
        random.shuffle(self.deck)

        self.player_cards = [self.get_card(), self.get_card()]
        self.computer_cards = [self.get_card(), self.get_card()]
        self.update_cards()

        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

        if sum(self.get_card_values(self.player_cards)) == 21:
            self.end_game("Blackjack! Mängija võitis!", "Võit")

    def get_card(self):
        if self.deck:
            card = self.deck.pop()
            self.update_deck_label()
            return card
        else:
            return None

    def get_card_values(self, cards):
        return [card[0] for card in cards if card]

    def format_cards(self, cards):
        return "  ".join(f"[{CARD_VALUES[v]} {s}]" for v, s in cards if v and s)

    def update_cards(self):
        self.player_cards_label.config(text=f"Sinu kaardid: {self.format_cards(self.player_cards)}")
        self.label.config(text=f"Sinu summa: {sum(self.get_card_values(self.player_cards))}")
        self.update_deck_label()

    def update_deck_label(self):
        self.deck_label.config(text=f"Alles jäänud kaardid: {len(self.deck)}")

    def hit(self):
        card = self.get_card()
        if card:
            self.player_cards.append(card)
            self.update_cards()
            if sum(self.get_card_values(self.player_cards)) > 21:
                self.end_game("Mängija kaotas! Ületas 21.", "Kaotus")

    def stand(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        while sum(self.get_card_values(self.computer_cards)) < 17:
            card = self.get_card()
            if card:
                self.computer_cards.append(card)
            else:
                break
        self.determine_winner()

    def determine_winner(self):
        player_sum = sum(self.get_card_values(self.player_cards))
        computer_sum = sum(self.get_card_values(self.computer_cards))
        self.computer_cards_label.config(text=f"Arvuti kaardid: {self.format_cards(self.computer_cards)}")
        result_text = f"Mängija: {player_sum} | Arvuti: {computer_sum}\n"
        if computer_sum > 21 or player_sum > computer_sum:
            result_text += "Mängija võitis!"
            result = "Võit"
        elif player_sum < computer_sum:
            result_text += "Arvuti võitis!"
            result = "Kaotus"
        else:
            result_text += "Viik!"
            result = "Viik"
        self.end_game(result_text, result)

    def end_game(self, message, result):
        self.result_label.config(text=message)
        self.start_button.config(state=tk.NORMAL if user_balance >= 1 else tk.DISABLED)
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.save_result(result)

    def save_result(self, result):
        with open("tulemused.txt", "a", encoding="utf-8") as file:
            file.write(f"{self.player_name} - {result} (Punktid: {sum(self.get_card_values(self.player_cards))})\n")

    def show_history(self):
        if not os.path.exists("tulemused.txt"):
            history = "Ajalugu puudub."
        else:
            with open("tulemused.txt", "r", encoding="utf-8") as file:
                history = file.read()
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, history)
        self.history_text.config(state=tk.DISABLED)

app.mainloop()