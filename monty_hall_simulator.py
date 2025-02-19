import tkinter as tk
from tkinter import ttk
import random
from PIL import Image, ImageTk
import os

class MontyHallSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Monty Hall Problem Simulator")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2C3E50')  # Dark blue background
        
        # Statistics
        self.stats_switch = {'wins': 0, 'games': 0}
        self.stats_stay = {'wins': 0, 'games': 0}
        
        # Load images
        self.load_images()
        self.setup_ui()
        self.reset_game()
    
    def load_images(self):
        # Create images if they don't exist
        if not os.path.exists('images/door_closed.png'):
            from create_images import save_images
            save_images()
        
        # Load the images
        self.door_closed_img = ImageTk.PhotoImage(Image.open('images/door_closed.png'))
        self.car_img = ImageTk.PhotoImage(Image.open('images/car.png'))
        self.goat_img = ImageTk.PhotoImage(Image.open('images/goat.png'))
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = tk.Label(main_frame, text="Monty Hall Problem Simulator",
                             font=('Helvetica', 24, 'bold'),
                             fg='#ECF0F1', bg='#2C3E50')
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Door frames with animation canvases
        self.door_frame = ttk.Frame(main_frame)
        self.door_frame.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Create doors using canvases
        self.doors = []
        self.door_canvases = []
        for i in range(3):
            canvas = tk.Canvas(self.door_frame, width=200, height=300,
                             bg='#34495E', highlightthickness=0)
            canvas.grid(row=0, column=i, padx=20)
            
            # Draw door
            canvas.create_image(100, 150, image=self.door_closed_img, tags=f'door{i}')
            canvas.create_text(100, 280, text=f"Door {i+1}",
                             fill='white', font=('Helvetica', 16))
            
            canvas.bind('<Button-1>', lambda e, x=i: self.choose_door(x))
            self.door_canvases.append(canvas)
        
        # Strategy selection
        strategy_frame = ttk.LabelFrame(main_frame, text="Strategy", padding="10")
        strategy_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.strategy_var = tk.StringVar(value="choose")
        ttk.Radiobutton(strategy_frame, text="Choose manually",
                       variable=self.strategy_var, value="choose").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(strategy_frame, text="Always stay",
                       variable=self.strategy_var, value="stay").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(strategy_frame, text="Always switch",
                       variable=self.strategy_var, value="switch").grid(row=0, column=2, padx=10)
        
        # Status label with better styling
        self.status_var = tk.StringVar()
        self.status_var.set("Choose a door!")
        status_label = tk.Label(main_frame, textvariable=self.status_var,
                              font=('Helvetica', 14), fg='#ECF0F1', bg='#2C3E50',
                              wraplength=600)
        status_label.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Statistics frame with improved styling
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="15")
        stats_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Stay strategy stats
        ttk.Label(stats_frame, text="Stay Strategy:", 
                 font=('Helvetica', 12)).grid(row=0, column=0, padx=10)
        self.stay_stats_var = tk.StringVar()
        self.stay_stats_var.set("Wins: 0/0 (0%)")
        ttk.Label(stats_frame, textvariable=self.stay_stats_var,
                 font=('Helvetica', 12)).grid(row=0, column=1, padx=10)
        
        # Switch strategy stats
        ttk.Label(stats_frame, text="Switch Strategy:",
                 font=('Helvetica', 12)).grid(row=1, column=0, padx=10)
        self.switch_stats_var = tk.StringVar()
        self.switch_stats_var.set("Wins: 0/0 (0%)")
        ttk.Label(stats_frame, textvariable=self.switch_stats_var,
                 font=('Helvetica', 12)).grid(row=1, column=1, padx=10)
        
        # Control buttons with styling
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        style = ttk.Style()
        style.configure('Action.TButton', font=('Helvetica', 12))
        
        ttk.Button(control_frame, text="New Game", command=self.reset_game,
                  style='Action.TButton').grid(row=0, column=0, padx=10)
        ttk.Button(control_frame, text="Auto Simulate (100)", command=self.auto_simulate,
                  style='Action.TButton').grid(row=0, column=1, padx=10)
    
    def animate_door(self, canvas_index, reveal_type):
        canvas = self.door_canvases[canvas_index]
        
        # Clear existing door
        canvas.delete(f'door{canvas_index}')
        
        # Show what's behind the door
        image = self.car_img if reveal_type == "Car!" else self.goat_img
        canvas.create_image(100, 150, image=image, tags=f'content{canvas_index}')
        canvas.create_text(100, 280, text=reveal_type,
                         fill='white', font=('Helvetica', 16))
    
    def choose_door(self, door_num):
        if self.game_state == "choosing":
            self.chosen_door = door_num
            
            # Update door appearance
            for i, canvas in enumerate(self.door_canvases):
                if i == door_num:
                    canvas.configure(bg='#27AE60')  # Green for selected
                else:
                    canvas.configure(bg='#34495E')  # Default color
            
            # Handle automatic strategies
            if self.strategy_var.get() != "choose":
                self.process_automatic_choice()
            else:
                # Reveal a goat
                self.reveal_goat_door()
                
        elif self.game_state == "deciding":
            self.make_final_choice(door_num)
    
    def reveal_goat_door(self):
        possible_reveals = [i for i in range(3) 
                          if i != self.car_position and i != self.chosen_door]
        self.revealed_door = random.choice(possible_reveals)
        
        # Animate the goat reveal
        self.animate_door(self.revealed_door, "Goat")
        
        self.game_state = "deciding"
        self.status_var.set("Would you like to switch doors? Click another door to switch, or your chosen door to stay.")
    
    def process_automatic_choice(self):
        self.reveal_goat_door()
        
        if self.strategy_var.get() == "stay":
            self.make_final_choice(self.chosen_door)
        else:  # switch
            final_door = [i for i in range(3) 
                         if i != self.chosen_door and i != self.revealed_door][0]
            self.make_final_choice(final_door)
    
    def make_final_choice(self, final_choice):
        if final_choice == self.revealed_door:
            return
            
        # Update statistics
        if final_choice == self.chosen_door:
            self.stats_stay['games'] += 1
            if final_choice == self.car_position:
                self.stats_stay['wins'] += 1
        else:
            self.stats_switch['games'] += 1
            if final_choice == self.car_position:
                self.stats_switch['wins'] += 1
        
        # Reveal all doors with animation
        for i in range(3):
            text = "Car!" if i == self.car_position else "Goat"
            self.animate_door(i, text)
        
        self.update_statistics()
        self.game_state = "finished"
        
        result = "Won!" if final_choice == self.car_position else "Lost!"
        self.status_var.set(f"Game Over - You {result} Click 'New Game' to play again.")
    
    def reset_game(self):
        self.car_position = random.randint(0, 2)
        self.chosen_door = None
        self.revealed_door = None
        self.game_state = "choosing"
        
        # Reset all door canvases
        for i, canvas in enumerate(self.door_canvases):
            canvas.delete("all")  # Clear canvas
            canvas.configure(bg='#34495E')  # Reset background
            # Redraw door
            canvas.create_image(100, 150, image=self.door_closed_img, tags=f'door{i}')
            canvas.create_text(100, 280, text=f"Door {i+1}",
                             fill='white', font=('Helvetica', 16))
        
        self.status_var.set("Choose a door!")
    
    def update_statistics(self):
        # Update stay statistics
        stay_pct = (self.stats_stay['wins'] / self.stats_stay['games'] * 100) if self.stats_stay['games'] > 0 else 0
        self.stay_stats_var.set(f"Wins: {self.stats_stay['wins']}/{self.stats_stay['games']} ({stay_pct:.1f}%)")
        
        # Update switch statistics
        switch_pct = (self.stats_switch['wins'] / self.stats_switch['games'] * 100) if self.stats_switch['games'] > 0 else 0
        self.switch_stats_var.set(f"Wins: {self.stats_switch['wins']}/{self.stats_switch['games']} ({switch_pct:.1f}%)")
    
    def auto_simulate(self):
        for _ in range(100):
            # Simulate staying
            car_pos = random.randint(0, 2)
            choice = random.randint(0, 2)
            self.stats_stay['games'] += 1
            if choice == car_pos:
                self.stats_stay['wins'] += 1
            
            # Simulate switching
            car_pos = random.randint(0, 2)
            first_choice = random.randint(0, 2)
            available_doors = [i for i in range(3) if i != first_choice and i != car_pos]
            revealed_door = random.choice(available_doors)
            final_choice = [i for i in range(3) if i != first_choice and i != revealed_door][0]
            
            self.stats_switch['games'] += 1
            if final_choice == car_pos:
                self.stats_switch['wins'] += 1
        
        self.update_statistics()

if __name__ == "__main__":
    root = tk.Tk()
    app = MontyHallSimulator(root)
    root.mainloop() 