import random

class AI_Agent:
    def __init__(self):
        self.goals = {
            'Hunger': 100,
            'Energy': 100,
            'Happiness': 100
        }

        self.actions = {
            'get raw food': {'Hunger': -30},
            'eat food': {'Hunger': -10, 'Energy': 10},
            'sleep': {'Energy': 50, 'Happiness': 30},
            'watch movie': {'Energy': -50, 'Happiness': 10},
            'hang out with friends': {'Energy': -50, 'Happiness': 10},
            'exercise': {'Energy': -50, 'Happiness': -50}
        }

        self.probability = {
            'get raw food': 0.7,
            'eat food': 0.8,
            'sleep': 0.6,
            'watch movie': 0.9,
            'hang out with friends': 0.7,
            'exercise': 0.95
        }

    def apply_action(self, action):
        for goal, change in self.actions[action].items():
            self.goals[goal] = max(self.goals[goal] + change, 0)

    def action_utility(self, action, goal):
        if goal in self.actions[action]:
            utility = -self.actions[action][goal]
        else:
            utility = 0

        for goal, change in self.actions[action].items():
            if goal in self.goals:
                self.goals[goal] += change
                if self.goals[goal] <= 0:
                    self.goals[goal] = 0

        successful = random.uniform(0.5, 0.8)
        if successful < self.probability[action]:
            utility = self.probability[action]

        if utility > 0 and goal in self.actions[action]:
            current_val = self.goals[goal]
            new_val = current_val + self.actions[action][goal]
            if new_val >= 0:
                utility *= 2
            if new_val > 100:
                utility = 0

        return utility

    def choose_action(self):
        assert len(self.goals) > 0, 'Need at least one goal'
        assert len(self.actions) > 0, 'Need at least one action'

        best_goal, best_goal_value = max(self.goals.items(), key=lambda item: item[1])

        best_action = None
        best_utility = None
        for key, value in self.actions.items():
            if best_goal in value:
                if best_action is None:
                    best_action = key
                    best_utility = self.action_utility(best_action, best_goal)
                else:
                    utility = self.action_utility(key, best_goal)
                    if utility > best_utility:
                        best_action = key
                        best_utility = utility

        return best_action

    def run_until_all_goals_zero(self):
        HR = '-' * 40
        print(">> Start <<")
        print(HR)
        running = True
        while running:
            print('GOALS:', self.goals)
            action = self.choose_action()
            print('BEST ACTION:', action)
            self.apply_action(action)
            print('NEW GOALS:', self.goals)
            if all(value == 0 for goal, value in self.goals.items()):
                running = False
            print(HR)
        print(">> Done! <<")


if __name__ == '__main__':
    agent = AI_Agent()
    agent.run_until_all_goals_zero()
