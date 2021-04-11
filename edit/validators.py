from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class RequiredCharactersValidator:
    def __init__(self,
                 min_numbers=1,
                 min_special=0,
                 min_lowercase=1,
                 min_uppercase=1,
                 special_characters="!@#$%^&*",
                 allow_other_characters=True):
        self.min_numbers = min_numbers
        self.min_special = min_special
        self.min_lowercase = min_lowercase
        self.min_uppercase = min_uppercase
        self.special_characters = special_characters
        self.allow_other_characters = allow_other_characters

    def validate(self, password, user=None):

        number_of_characters = {
            'numbers': 0,
            'special': 0,
            'lower': 0,
            'upper': 0
        }

        for character in password:
            if character in "1234567890":
                number_of_characters['numbers'] += 1
            elif character in self.special_characters:
                number_of_characters['special'] += 1
            elif str.lower(character) in "abcdefghijklmnopqrstuvwxyz":
                if str.upper(character) == character:
                    number_of_characters['upper'] += 1
                else:
                    number_of_characters['lower'] += 1
            else:
                if not self.allow_other_characters:
                    raise ValidationError(_(f"{character} is not allowed"))

        errors = []

        if self.min_numbers != 0 and number_of_characters[
            'numbers'] < self.min_numbers:
            errors += [
                f"{self.min_numbers} numbe{self.determine_plural(self.min_numbers)}"
            ]

        if self.min_special != 0 and number_of_characters[
            'special'] < self.min_special:
            errors += [
                f"{self.min_special} special characte{self.determine_plural(self.min_special)}"
            ]

        if self.min_uppercase != 0 and number_of_characters[
            'upper'] < self.min_uppercase:
            errors += [
                f"{self.min_uppercase} uppercase lette{self.determine_plural(self.min_uppercase)}"
            ]

        if self.min_lowercase != 0 and number_of_characters[
            'lower'] < self.min_lowercase:
            errors += [
                f"{self.min_lowercase} lowercase lette{self.determine_plural(self.min_lowercase)}"
            ]

        if len(errors) > 0:
            raise ValidationError(
                _("This password doesn't contain at least " +
                  self.print_list_as_sentence(errors)))

    def get_requirements(self):
        needed_characters = []

        if self.min_numbers != 0:
            needed_characters += [
                f"{self.min_numbers} numbe{self.determine_plural(self.min_numbers)}"
            ]

        if self.min_special != 0:
            needed_characters += [
                f"{self.min_special} special characte{self.determine_plural(self.min_special)}"
            ]

        if self.min_uppercase != 0:
            needed_characters += [
                f"{self.min_uppercase} uppercase lette{self.determine_plural(self.min_uppercase)}"
            ]

        if self.min_lowercase != 0:
            needed_characters += [
                f"{self.min_lowercase} lowercase lette{self.determine_plural(self.min_lowercase)}"
            ]

        result = self.print_list_as_sentence(needed_characters)

        return result

    @staticmethod
    def determine_plural(test, single='r', plural='rs'):
        if test == 1:
            return single
        else:
            return plural

    @staticmethod
    def print_list_as_sentence(in_list):
        result = ""
        for item in in_list:
            if in_list[-1] == item:
                if len(in_list) == 1:
                    result += item + "."
                else:
                    result += "and " + item + "."
            else:
                if len(in_list) == 2:
                    result += item + " "
                else:
                    result += item + ", "
        return result

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.get_requirements()}")
