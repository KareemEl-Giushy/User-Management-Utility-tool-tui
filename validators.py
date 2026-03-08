from textual.validation import Validator


class InputValidator(Validator):
    def __init__(self, less_count=3, failure_description = None):
        super().__init__(failure_description)
        self.less_count = less_count

    def validate(self, value):
        if self.empty(value):
            return self.failure("This Field Can't Be Empty!")
        elif self.lessThan(value):
            return self.failure("Field Can't Be Less Than 3 Characters!")
        else:
            return self.success()

    def empty(self, value: str):
        return value == ""
    
    def lessThan(self, value: str):
        return len(value) < self.less_count