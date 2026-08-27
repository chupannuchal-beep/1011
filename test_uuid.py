import sales_validation

class FakeTextWidget:

    def __init__(self):
        self.messages = []

    def insert(self, position, message):
        self.messages.append(message)

    def see(self, position):
        pass

    def delete(self, start, end):
        self.messages.clear()


def test_generate_uuid():
    widget = FakeTextWidget()

    logger = sales_validation.LoggerManager(widget)

    result = logger.generate_uuid()

    assert result is not None
    assert isinstance(result, str)