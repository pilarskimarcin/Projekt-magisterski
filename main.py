from enum import IntEnum


class State(IntEnum):
    GREEN = 1
    YELLOW = 2
    RED = 3
    BLACK = 4

    def __add__(self, other):
        if self.value != State.BLACK:
            return State(self.value + other)
        else:
            return self

    def __str__(self):
        return str(self.name).capitalize()


class Injured:
    state: State

    def __init__(self, state: State):
        self.state = state

    def change_state(self):
        self.state += 1

    def __repr__(self):
        return f"Injured(state={self.state})"


if __name__ == '__main__':
    injured = Injured(State.GREEN)
    for _ in range(4):
        print(injured)
        injured.change_state()
    print(injured)
