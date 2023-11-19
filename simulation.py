import random
from typing import List, Set

from classes import Injured, State


class Simulation:
    injured: Set[Injured]

    def __init__(self):
        state_seq: List[State] = sorted(State)
        self.injured = {Injured(random.choice(state_seq)) for _ in range(random.randint(10, 15))}

    def step(self):
        """
        Simulation step
        """
        for injured in self.injured:
            injured.change_state()

    def run(self, n_iterations: int = 10):
        """
        Run the simulation for a specified amount of iterations or until all injured people have died (because there is
        no point to continue, something clearly went wrong)
        :param n_iterations: (int) number of iterations
        """
        i: int = 0
        print(self)
        while i < n_iterations or \
                sum(self.injured) != State.BLACK * len(self.injured):
            print(f"Simulation step {i + 1}")  # TODO: logging to file?
            print(sum(self.injured))  # TODO: ??????
            self.step()
            print(self)
            i += 1

    def __repr__(self):
        n_green: int = len({injured for injured in self.injured if injured.state == State.GREEN})
        n_yellow: int = len({injured for injured in self.injured if injured.state == State.YELLOW})
        n_red: int = len({injured for injured in self.injured if injured.state == State.RED})
        n_black: int = len({injured for injured in self.injured if injured.state == State.BLACK})
        return f"{n_black} Black injured, {n_red} Red injured, {n_yellow} Yellow injured, {n_green} Green injured"


if __name__ == '__main__':
    sim: Simulation = Simulation()
    sim.run()
