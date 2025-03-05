import tkinter as tk
import random

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        
        # UI элементы
        self.label = tk.Label(root, text="Vajuta 'Alusta mängu'", font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.start_button = tk.Button(root, text="Alusta mängu", command=self.start_game)
        self.start_button.pack()

        self.hit_button = tk.Button(root, text="Võta kaart", command=self.hit, state=tk.DISABLED)
        self.hit_button.pack()

        self.stand_button = tk.Button(root, text="Peatu", command=self.stand, state=tk.DISABLED)
        self.stand_button.pack()

        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)
        
        self.player_cards = []
        self.computer_cards = []

    def start_game(self):
        """Начало новой игры"""
        self.player_cards = [self.get_card(), self.get_card()]
        self.computer_cards = [self.get_card(), self.get_card()]
        self.update_label()
        
        # Активируем кнопки
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        
        # Проверяем, нет ли у игрока сразу 21
        if sum(self.player_cards) == 21:
            self.end_game("Blackjack! Mängija võitis!")

    def get_card(self):
        """Возвращает случайную карту (2-11)"""
        return random.randint(2, 11)

    def update_label(self):
        """Обновляет текст с текущими картами игрока"""
        self.label.config(text=f"Sinu kaardid: {self.player_cards} (Summa: {sum(self.player_cards)})")

    def hit(self):
        """Игрок берет карту"""
        self.player_cards.append(self.get_card())
        self.update_label()

        # Проверяем, не проиграл ли игрок
        if sum(self.player_cards) > 21:
            self.end_game("Mängija kaotas! Ületas 21.")

    def stand(self):
        """Игрок останавливается, ход компьютера"""
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        # Логика компьютера
        while sum(self.computer_cards) < 17:
            self.computer_cards.append(self.get_card())

        self.determine_winner()

    def determine_winner(self):
        """Определяет победителя"""
        player_sum = sum(self.player_cards)
        computer_sum = sum(self.computer_cards)

        result_text = f"Mängija: {player_sum} | Arvuti: {computer_sum}\n"

        if computer_sum > 21 or player_sum > computer_sum:
            result_text += "Mängija võitis!"
        elif player_sum < computer_sum:
            result_text += "Arvuti võitis!"
        else:
            result_text += "Viik!"

        self.end_game(result_text)

    def end_game(self, message):
        """Завершает игру, выводит результат"""
        self.result_label.config(text=message)
        self.start_button.config(state=tk.NORMAL)
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

# Запуск приложения
root = tk.Tk()
game = BlackjackGame(root)
root.mainloop()

