from datetime import datetime, date, timedelta
from collections import UserDict
import re
from typing import Callable

def find_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)


def adjust_for_weekend(birthday):
    if birthday.weekday() >= 5:
        return find_next_weekday(birthday, 0)
    return birthday

def date_to_string(dt):
    return dt.strftime("%d.%m.%Y")


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not str(value).strip() :
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if value and len(str(value))!=10 or not str(value).isdigit():
            raise ValueError("Phone number is not correct")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format or date does not exist. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def find_phone(self, phone):
        phone_obj = Phone(phone)  # для перевірки коректності введеного номеру
        for i in self.phones:
            if i.value == phone:
                return i
        return None

    def add_phone(self, phone):
        if self.find_phone(phone) is None:
            self.phones.append(Phone(phone))
        return self

    def remove_phone(self, phone):
        found_phone = self.find_phone(phone)
        if found_phone:
            self.phones.remove(found_phone)
        return self

    def edit_phone(self, old_phone, new_phone):
        new_phone_obj = Phone(new_phone)
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj is not None:
            old_phone_obj.value = new_phone_obj.value
        else:
            raise ValueError("Phone not found")
        return self

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    def find(self, name):
        if name in self.data:
            return self.data[name]
        return None

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for user in self.data.values():
            if user.birthday and user.birthday.value:
                birthday_date = datetime.strptime(user.birthday.value,"%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year =birthday_date.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    birthday_this_year = adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = date_to_string(birthday_this_year)
                    upcoming_birthdays.append({"name": user.name.value, "congratulation_date": congratulation_date_str})
        return upcoming_birthdays






def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # Якщо помилка викликана валідацією всередині класів (Phone або Birthday)
            if "Phone number" in str(e) or "Invalid date format" in str(e):
                return str(e)
            return "Give me name and parameters please."
        except IndexError:
            return "Enter username or correct arguments. Format depends on command."
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Contact not found."
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return f"Phones for {name}: {'; '.join(p.value for p in record.phones)}"

@input_error
def all_contacts(args, book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record.birthday:
        return "Birthday not set for this contact."
    return f"{name}'s birthday: {record.birthday.value}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(f"{item['name']}: {item['congratulation_date']}" for item in upcoming)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(all_contacts(args,book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
