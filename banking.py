# Write your code here
import random, math, sqlite3


def round_up(x):
    return int(math.ceil(x / 10.0)) * 10


class CreditCard:
    def __init__(self, _id=None, cardn=None, pin=None, balance=None):
        if cardn is not None and len(cardn) == 16 and pin is not None and len(pin) == 4 and balance is not None:
            self.card_number = {"IIN": [4, 0, 0, 0, 0, 0], "CAN": []}
            self.PIN = [0, 0, 0, 0]
            self.Balance = balance
            for _e in range(6, 15):
                self.card_number["CAN"].append(int(cardn[_e]))
            for _e in range(4):
                self.PIN[_e] = int(pin[_e])
        else:
            self.card_number = {"IIN": [4, 0, 0, 0, 0, 0], "CAN": []}
            self.PIN = [0, 0, 0, 0]
            self.Balance = 0
            self.id = _id
            for _e in range(9):
                self.card_number["CAN"].append(random.randint(0, 9))
            for _e in range(4):
                self.PIN[_e] = random.randint(0, 9)

    def luhn_get_checksum(self):
        luhn = self.card_number["IIN"] + self.card_number["CAN"]
        i = 0
        j = 0
        _id = "IIN"
        flag = True
        while j < len(luhn):
            if (i+1) % 2 != 0:
                luhn[j] = self.card_number[_id][i] * 2
            if luhn[j] > 9:
                luhn[j] = luhn[j] - 9
            if flag and (i+1) == len(self.card_number[_id]):
                i = -1
                _id = "CAN"
                flag = False
            i += 1
            j += 1
        return round_up(sum(luhn)) - (sum(luhn))

    def add_income(self, income):
        self.Balance += income

    def apply_identifier(self, card_number, pin):
        number = self.card_number["IIN"] + self.card_number["CAN"]
        number.append(self.luhn_get_checksum())
        for _c, _n in zip(card_number, number):
            if int(_c) != _n:
                return False
        for _p, _P in zip(pin, self.PIN):
            if int(_p) != _P:
                return False
        return True

    def get_credit_card_number(self):
        number = self.card_number["IIN"] + self.card_number["CAN"]
        number.append(self.luhn_get_checksum())
        answer = ""
        for _e in number:
            answer += str(_e)
        return answer

    def get_pin(self):
        pin = ""
        for el in self.PIN:
            pin += str(el)
        return pin


class BankingSystem:
    def __init__(self):
        self.user_credit_cards = []
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='card' ''')
        if self.cur.fetchone()[0] != 1:
            self.cur.execute('CREATE TABLE card ( ID INTEGER, NUMBER TEXT, PIN TEXT, BALANCE INTEGER DEFAULT 0)')
            self.conn.commit()
        else:
            self.cur.execute(''' SELECT * FROM 'card' ''')
            # print(self.cur.fetchall())
            for row in self.cur.fetchall():
                self.user_credit_cards.append(CreditCard(row[0], row[1], row[2], row[3]))

    def create_account(self):
        self.user_credit_cards.append(CreditCard(len(self.user_credit_cards) + 1))
        print("Your card has been created")
        self.execute_command("INSERT INTO card VALUES "
                             "( {0}, {1}, {2}, {3} )".format(self.user_credit_cards[-1].id,
                                                             self.user_credit_cards[-1].get_credit_card_number(),
                                                             self.user_credit_cards[-1].get_pin(),
                                                             self.user_credit_cards[-1].Balance))

    def log_into_account(self, cardn, pin):
        for card in self.user_credit_cards:
            if card.apply_identifier(cardn, pin):
                return True
        return False

    def check_luhn(self, cardn):
        check = CreditCard(-1, cardn, "0000", 0)
        if int(cardn[-1]) != check.luhn_get_checksum():
            return False
        return True

    def card_menu(self, cardn):
        _input = -1
        while _input != 0:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            _input = int(input())
            print()
            if _input == 1:
                print("Balance: " + str(self.user_credit_cards[-1].Balance))
            elif _input == 2:
                print("Enter income:")
                income = int(input())
                self.find_credit_card(cardn).add_income(income)
                print("Income was added")
                self.execute_command("UPDATE card SET BALANCE = {0} WHERE id = {1}"
                                     .format(self.find_credit_card(cardn).Balance,
                                             self.find_credit_card(cardn).id))
            elif _input == 3:
                print("Transfer")
                print("Enter card number:")
                transfer_cardn = input()
                if transfer_cardn == cardn:
                    print("You can't transfer money to the same account!")
                elif transfer_cardn.startswith("4") and not self.check_luhn(transfer_cardn):
                    print("Probably you made mistake in the card number. Please try again!")
                elif not self.find_credit_card(transfer_cardn):
                    print("Such a card does not exist.")
                elif self.find_credit_card(transfer_cardn):
                    print("Enter how much money you want to transfer:")
                    transfer_money = input()
                    if self.find_credit_card(cardn).Balance < int(transfer_money):
                        print("Not enough money!")
                    else:
                        self.find_credit_card(cardn).add_income(-int(transfer_money))
                        self.find_credit_card(transfer_cardn).add_income(int(transfer_money))
                        self.execute_command("UPDATE card SET BALANCE = {0} WHERE id = {1}"
                                     .format(self.find_credit_card(cardn).Balance,
                                             self.find_credit_card(cardn).id))
                        self.execute_command("UPDATE card SET BALANCE = {0} WHERE id = {1}"
                                             .format(self.find_credit_card(transfer_cardn).Balance,
                                                     self.find_credit_card(transfer_cardn).id))
            elif _input == 4:
                self.execute_command("DELETE from card WHERE id = {0}".format(self.find_credit_card(cardn).id))
                print("The account has been closed!")
                break
            elif _input == 5:
                print("\nYou have successfully logged out\n")
                break
            elif _input == 0:
                return True
        return False

    def find_credit_card(self, cardn):
        for card in self.user_credit_cards:
            if (card.get_credit_card_number()) == cardn:
                return card
        return None

    def get_last_account_info(self):
        print("Your card number:")
        print(self.user_credit_cards[-1].get_credit_card_number())
        print("Your card PIN:")
        print(self.user_credit_cards[-1].get_pin())

    def execute_command(self, *command):
        self.cur.execute(command[0])
        self.conn.commit()

    def __del__(self):
        self.conn.close()


def menu():
    bank = BankingSystem()
    _input = -1
    while _input != 0:
        print()
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        _input = int(input())
        print()
        if _input == 1:
            bank.create_account()
            bank.get_last_account_info()
        elif _input == 2:
            print("Enter your card number:")
            card_number = input()
            print("Enter your PIN:")
            pin = input()
            if bank.log_into_account(card_number, pin):
                print("\nYou have successfully logged in!\n")
                if bank.card_menu(card_number):
                    break
            else:
                print("\nWrong card number or PIN!\n")
    print("Bye!")
    del bank


menu()
