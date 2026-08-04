# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

        self.toxic_traps = set()
        while len(self.toxic_traps) < 3:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap = (tx, ty)

            if trap != (0, 0) and trap not in self.walls and trap not in self.food_positions:
                self.toxic_traps.add(trap)

    # ✅ PARTIAL OBSERVABILITY
    def get_percept(self) -> dict:
        x, y = self.agent_pos

        front = (x, y + 1)

        wall_ahead = (
            front[0] < 0 or front[0] >= self.width or
            front[1] < 0 or front[1] >= self.height or
            front in self.walls
        )

        return {
            'wall_ahead': wall_ahead,
            'food_here': (x, y) in self.food_positions,
            'toxin_here': (x, y) in self.toxic_traps
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == 'Stay':
            pass

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


# ✅ SIMPLE REFLEX AGENT
class SimpleReflexAgent:
    def sense_and_act(self, percept):
        if percept['food_here']:
            return 'Stay'
        elif percept['toxin_here']:
            return random.choice(['Left', 'Right'])
        elif percept['wall_ahead']:
            return random.choice(['Left', 'Right'])
        else:
            return 'Up'


# ✅ MODEL-BASED AGENT
class ModelBasedAgent:
    def __init__(self):
        self.visited_states = set()

    def sense_and_act(self, percept):
        state = (percept['wall_ahead'], percept['food_here'])

        if state in self.visited_states:
            return random.choice(['Left', 'Right'])

        self.visited_states.add(state)

        if percept['food_here']:
            return 'Stay'
        elif percept['toxin_here']:
            return random.choice(['Left', 'Right'])
        elif percept['wall_ahead']:
            return random.choice(['Left', 'Right'])
        else:
            return 'Up'


class GridGameGUI:
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("Grid Hunt - Reflex vs Model Agent")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food,
                                      num_opponents=num_opponents, custom_walls=walls)

        # 🔁 SWITCH HERE
        # self.agent = SimpleReflexAgent()
        self.agent = ModelBasedAgent()

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop,
                             font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        for fx, fy in self.env.food_positions:
            self.canvas.create_oval(
                fx * self.cell_size + 5,
                (self.env.height - 1 - fy) * self.cell_size + 5,
                fx * self.cell_size + 15,
                (self.env.height - 1 - fy) * self.cell_size + 15,
                fill="orange"
            )

        ax, ay = self.env.agent_pos
        self.canvas.create_oval(
            ax * self.cell_size + 5,
            (self.env.height - 1 - ay) * self.cell_size + 5,
            ax * self.cell_size + 20,
            (self.env.height - 1 - ay) * self.cell_size + 20,
            fill="blue"
        )

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)

                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                self.label.config(text=f"Finished! Score: {self.env.score}")
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()