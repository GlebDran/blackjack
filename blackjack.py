import tkinter as tk
import random
import os

# Карточные масти
SUITS = ["♥", "♦", "♣", "♠"]

# Карты и их символы
CARD_VALUES = {
    2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
    7: "7", 8: "8", 9: "9", 10: "10",
    11: "A"
}

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.root.geometry("500x600")
        self.root.configure(bg="green")

        # UI Элементы
        self.name_label = tk.Label(root, text="Sisesta oma nimi:", bg="green", fg="white", font=("Arial", 12))
        self.name_label.pack()
        self.name_entry = tk.Entry(root, font=("Arial", 12))
        self.name_entry.pack()

        self.label = tk.Label(root, text="Vajuta 'Alusta mängu'", font=("Arial", 14, "bold"), bg="green", fg="yellow")
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Alusta mängu", command=self.start_game, font=("Arial", 12), bg="white")
        self.start_button.pack()

        self.hit_button = tk.Button(root, text="Võta kaart", command=self.hit, state=tk.DISABLED, font=("Arial", 12), bg="white")
        self.hit_button.pack()

        self.stand_button = tk.Button(root, text="Peatu", command=self.stand, state=tk.DISABLED, font=("Arial", 12), bg="white")
        self.stand_button.pack()

        self.history_button = tk.Button(root, text="Vaata ajalugu", command=self.show_history, font=("Arial", 12), bg="white")
        self.history_button.pack()

        self.result_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="green", fg="white")
        self.result_label.pack(pady=10)

        # Отображение карт игрока и компьютера
        self.player_cards_label = tk.Label(root, text="", font=("Arial", 18), bg="green", fg="white")
        self.player_cards_label.pack(pady=5)

        self.computer_cards_label = tk.Label(root, text="", font=("Arial", 18), bg="green", fg="white")
        self.computer_cards_label.pack(pady=5)

        self.history_text = tk.Text(root, height=10, width=50, state=tk.DISABLED, font=("Arial", 10))
        self.history_text.pack(pady=10)

        self.player_cards = []
        self.computer_cards = []

    def start_game(self):
        """Начало новой игры"""
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            self.label.config(text="Palun sisesta oma nimi!", fg="red")
            return

        self.player_cards = [self.get_card(), self.get_card()]
        self.computer_cards = [self.get_card(), self.get_card()]
        self.update_cards()

        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

        if sum(self.get_card_values(self.player_cards)) == 21:
            self.end_game("Blackjack! Mängija võitis!", "Võit")

    def get_card(self):
        """Создает карту в виде (номинал, масть)"""
        value = random.choice(list(CARD_VALUES.keys()))
        suit = random.choice(SUITS)
        return (value, suit)

    def get_card_values(self, cards):
        """Возвращает числовые значения карт"""
        return [card[0] for card in cards]

    def format_cards(self, cards):
        """Форматирует карты в виде строки"""
        return "  ".join(f"[{CARD_VALUES[v]} {s}]" for v, s in cards)

    def update_cards(self):
        """Обновляет отображение карт"""
        self.player_cards_label.config(text=f"Sinu kaardid: {self.format_cards(self.player_cards)}")
        self.label.config(text=f"Sinu summa: {sum(self.get_card_values(self.player_cards))}")

    def hit(self):
        """Игрок берет карту"""
        self.player_cards.append(self.get_card())
        self.update_cards()

        if sum(self.get_card_values(self.player_cards)) > 21:
            self.end_game("Mängija kaotas! Ületas 21.", "Kaotus")

    def stand(self):
        """Игрок останавливается, ход компьютера"""
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        while sum(self.get_card_values(self.computer_cards)) < 17:
            self.computer_cards.append(self.get_card())

        self.determine_winner()

    def determine_winner(self):
        """Определяет победителя"""
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
        """Завершает игру, выводит результат и сохраняет в файл"""
        self.result_label.config(text=message)
        self.start_button.config(state=tk.NORMAL)
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        self.save_result(result)

    def save_result(self, result):
        """Сохраняет результат в файл tulemused.txt"""
        with open("tulemused.txt", "a", encoding="utf-8") as file:
            file.write(f"{self.player_name} - {result} (Punktid: {sum(self.get_card_values(self.player_cards))})\n")

    def show_history(self):
        """Отображает историю игр в текстовом поле"""
        if not os.path.exists("tulemused.txt"):
            history = "Ajalugu puudub."
        else:
            with open("tulemused.txt", "r", encoding="utf-8") as file:
                history = file.read()

        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, history)
        self.history_text.config(state=tk.DISABLED)

# Запуск приложения
root = tk.Tk()
game = BlackjackGame(root)
root.mainloop()
