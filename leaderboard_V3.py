import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os
# Octopus King
# File to store data


CSV_FILE = "tournament_data.csv"

class TournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Tournament Scoring System")
        self.root.geometry("800x500")

        #Data Dictionaries
        self.teams = {}        #Format: {"Team Name": score}
        self.individuals = {}  #Format: {"Indiv Name": score}
        self.team_members = {} #Format: {"Team Name": ["Indiv Name", ...]}
        self.events = []       #Format: ["100m Sprint", "football", etc.]
        # Rank matrix: points awarded for finishing positions (index 0 -> 1st place)
        # Modify this list to change how many points each rank receives.
        self.rank_matrix = [10, 8, 6, 5, 4, 3, 2, 1]

        self.load_from_csv()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.setup_admin_screen()
        self.setup_leaderboard_screen()

        self.refresh_admin_lists()
        self.refresh_leaderboards()


    #ADMIN SCREEN

    def setup_admin_screen(self):
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="Admin Screen (Manage)")

        view_frame = tk.Frame(self.admin_frame)
        view_frame.pack(fill="both", expand=True, pady=10, padx=10)

        team_frame = tk.Frame(view_frame)
        team_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(team_frame, text="Teams (Max 4)", font=("Arial", 12, "bold")).pack()
        self.list_teams = tk.Listbox(team_frame)
        self.list_teams.pack(fill="both", expand=True)

        indiv_frame = tk.Frame(view_frame)
        indiv_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(indiv_frame, text="Individuals (Max 20)", font=("Arial", 12, "bold")).pack()
        self.list_indiv = tk.Listbox(indiv_frame)
        self.list_indiv.pack(fill="both", expand=True)

        event_frame = tk.Frame(view_frame)
        event_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(event_frame, text="Events (Max 5)", font=("Arial", 12, "bold")).pack()
        self.list_events = tk.Listbox(event_frame)
        self.list_events.pack(fill="both", expand=True)

        bottom_frame = tk.Frame(self.admin_frame)
        bottom_frame.pack(fill="x", side="bottom", pady=10, padx=20)

        btn_add = tk.Button(bottom_frame, text="Add New Entry", width=15, command=self.add_entry)
        btn_add.pack(side="left")

        btn_assign = tk.Button(bottom_frame, text="Assign Individual to Team", width=22, command=self.add_individual_to_team)
        btn_assign.pack(side="left", pady=10, padx=5)

        btn_add = tk.Button(bottom_frame, text="Remove Entry", width=15, command=self.remove_entry)
        btn_add.pack(side="left", pady=10 , padx=15)

        btn_save = tk.Button(bottom_frame, text="Save to CSV", width=15, bg="lightgreen", command=self.save_to_csv)
        btn_save.pack(side="right")
        
        btn_edit_rank = tk.Button(bottom_frame, text="Edit Rank Matrix", width=15, bg="lightyellow", command=self.edit_rank_matrix)
        btn_edit_rank.pack(side="right", padx=8)


    #LB screen

    def setup_leaderboard_screen(self):
        self.board_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.board_frame, text="Leaderboards (Scores)")
        

        #the 2 LBs 
        boards_frame = tk.Frame(self.board_frame)
        boards_frame.pack(fill="both", expand=True, pady=10, padx=10)

        #Team LB
        team_board_frame = tk.Frame(boards_frame)
        team_board_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(team_board_frame, text="Team Leaderboard", font=("Arial", 12, "bold")).pack()
        
        self.tree_team = ttk.Treeview(team_board_frame, columns=("rank", "name", "score"), show="headings")
        self.tree_team.heading("rank", text="Rank")
        self.tree_team.heading("name", text="Team Name")
        self.tree_team.heading("score", text="Points")
        self.tree_team.column("rank", width=50, anchor="center")
        self.tree_team.column("score", width=80, anchor="center")
        self.tree_team.pack(fill="both", expand=True)

        #Individual LB
        indiv_board_frame = tk.Frame(boards_frame)
        indiv_board_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(indiv_board_frame, text="Individual Leaderboard", font=("Arial", 12, "bold")).pack()
        
        self.tree_indiv = ttk.Treeview(indiv_board_frame, columns=("rank", "name", "score"), show="headings")
        self.tree_indiv.heading("rank", text="Rank")
        self.tree_indiv.heading("name", text="Competitor Name")
        self.tree_indiv.heading("score", text="Points")
        self.tree_indiv.column("rank", width=50, anchor="center")
        self.tree_indiv.column("score", width=80, anchor="center")
        self.tree_indiv.pack(fill="both", expand=True)

        controls_frame = tk.Frame(self.board_frame)
        controls_frame.pack(fill="x", side="bottom", pady=10)

        btn_add_pts = tk.Button(controls_frame, text="+ Add 5 Points", width=15, bg="lightgreen", command=lambda: self.modify_points(5))
        btn_add_pts.pack(side="left", padx=20)

        btn_rem_pts = tk.Button(controls_frame, text="- Remove 5 Points", width=15, bg="lightcoral", command=lambda: self.modify_points(-5))
        btn_rem_pts.pack(side="left")

        btn_record = tk.Button(controls_frame, text="Record Event Result", width=18, bg="lightblue", command=self.record_event_result)
        btn_record.pack(side="left", padx=10)


    
    
    
    
    
    #logic
    
    def add_entry(self):
        choice = simpledialog.askstring("Add Entry", "What do you want to add?\n(Type: 'team' (T), 'individual' (I), or 'event' (E))")
        if not choice:
            return
            
        choice = str(choice.lower().strip())
        name = simpledialog.askstring("Name", f"Enter the name for the new {choice}:")
        
        if not name:
            return

        if choice in ('team', 't'):
            if len(self.teams) >= 4:
                messagebox.showerror("Limit Reached", "You cannot have more than 4 teams.")
                return
            self.teams[name] = 0
            self.team_members[name] = []
        elif choice in ('individual', 'i'):
            if len(self.individuals) >= 20:
                messagebox.showerror("Limit Reached", "You cannot have more than 20 individuals.")
                return
            self.individuals[name] = 0
        elif choice in ('event', 'e'):
            if len(self.events) >= 5:
                messagebox.showerror("Limit Reached", "You cannot have more than 5 events.")
                return
            self.events.append(name)
        else:
            messagebox.showerror("Error", "Invalid category. Must be team, individual, or event.")

        self.refresh_admin_lists()
        self.refresh_leaderboards()

    def remove_entry(self):
        choice = simpledialog.askstring("Remove Entry", "What do you want to delete?\n(Type: 'team', 'individual', or 'event')")
        if not choice:
            return
            
        choice = choice.lower().strip()
        remove_name = simpledialog.askstring("Name", f"Enter the name of what you want to remove. {choice}:")
        
        if not remove_name:
            return

        if choice == 'team':
            self.teams.pop(remove_name, None)
            self.team_members.pop(remove_name, None)
        elif choice == 'individual':
            self.individuals.pop(remove_name, None)
            for members in self.team_members.values():
                if remove_name in members:
                    members.remove(remove_name)
        elif choice == 'event':
            if remove_name in self.events:
                self.events.remove(remove_name)
        else:
            messagebox.showerror("Error", "Invalid category. Must be team, individual, or event.")

        self.refresh_admin_lists()
        self.refresh_leaderboards()

    def modify_points(self, amount):
        #check selected team/indiv
        selected_team = self.tree_team.selection()
        if selected_team:
            item = self.tree_team.item(selected_team)
            name = item['values'][1]
            self.teams[name] += amount
        

        selected_indiv = self.tree_indiv.selection()
        if selected_indiv:
            item = self.tree_indiv.item(selected_indiv)
            name = item['values'][1]
            self.individuals[name] += amount

        self.refresh_leaderboards()


    def add_individual_to_team(self):
        if not self.teams:
            messagebox.showerror("No Teams", "No teams available. Add a team first.")
            return
        if not self.individuals:
            messagebox.showerror("No Individuals", "No individuals available. Add an individual first.")
            return

        team = simpledialog.askstring("Assign Individual", f"Enter a team name from the list:\n{', '.join(self.teams.keys())}")
        if not team:
            return
        team = team.strip()
        if team not in self.teams:
            messagebox.showerror("Invalid Team", "Team not found. Please enter a valid team name.")
            return

        indiv = simpledialog.askstring("Assign Individual", f"Enter an individual name from the list:\n{', '.join(self.individuals.keys())}")
        if not indiv:
            return
        indiv = indiv.strip()
        if indiv not in self.individuals:
            messagebox.showerror("Invalid Individual", "Individual not found. Please enter a valid individual name.")
            return

        self.team_members.setdefault(team, [])
        current_team = next((t for t, members in self.team_members.items() if indiv in members), None)
        if current_team == team:
            messagebox.showinfo("Already Assigned", f"{indiv} is already assigned to {team}.")
            return
        if current_team:
            confirm = messagebox.askyesno("Reassign Individual", f"{indiv} is already assigned to {current_team}.\nMove them to {team}?")
            if not confirm:
                return
            self.team_members[current_team].remove(indiv)

        self.team_members[team].append(indiv)
        messagebox.showinfo("Assigned", f"{indiv} has been assigned to {team}.")

    def record_event_result(self):
        # Let the user pick an event and enter finish order; apply points from rank_matrix
        if not self.events:
            messagebox.showerror("No Events", "No events available. Add an event first.")
            return

        event = simpledialog.askstring("Record Event", f"Enter event name from list:\n{', '.join(self.events)}")
        if not event:
            return
        if event not in self.events:
            messagebox.showerror("Invalid Event", "Event not found. Please enter a valid event name from the list.")
            return

        kind = simpledialog.askstring("Type", "Is this a 'team' or 'individual' event?")
        if not kind:
            return
        kind = kind.lower().strip()
        if kind not in ('team', 'individual'):
            messagebox.showerror("Invalid Type", "Type must be 'team' or 'individual'.")
            return

        candidates = list(self.teams.keys()) if kind == 'team' else list(self.individuals.keys())
        if not candidates:
            messagebox.showerror("No Competitors", f"No {kind}s available to score. Add entries first.")
            return

        ranking_string = simpledialog.askstring("Results", f"Enter competitors in finishing order, comma-separated.\nAvailable: {', '.join(candidates)}")
        if not ranking_string:
            return

        names = [n.strip() for n in ranking_string.split(',') if n.strip()]
        if not names:
            return

        # validate names
        for name in names:
            if name not in candidates:
                messagebox.showerror("Invalid Name", f"{name} not found among {kind}s. Aborting.")
                return

        # check for duplicate names
        if len(names) != len(set(names)):
            messagebox.showerror("Duplicate Names", "Duplicate competitors found in the results. Aborting.")
            return

        # build preview of assigned points
        preview_lines = []
        for i, name in enumerate(names):
            pts = self.rank_matrix[i] if i < len(self.rank_matrix) else 0
            preview_lines.append(f"{i+1}. {name} -> {pts} pts")
        if len(names) > len(self.rank_matrix):
            preview_lines.append(f"(Ranks beyond {len(self.rank_matrix)} receive 0 points)")

        preview = "\n".join(preview_lines)
        confirm = messagebox.askyesno("Confirm Results", f"Event: {event}\nType: {kind}\nApply points as:\n\n{preview}\n\nApply these results?")
        if not confirm:
            return

        # apply points from rank matrix
        for i, name in enumerate(names):
            points = self.rank_matrix[i] if i < len(self.rank_matrix) else 0
            if kind == 'team':
                self.teams[name] = self.teams.get(name, 0) + points
            else:
                self.individuals[name] = self.individuals.get(name, 0) + points

        messagebox.showinfo("Results Recorded", f"Applied points for event: {event}")
        self.refresh_leaderboards()


    def edit_rank_matrix(self):
        # Prompt user to edit the rank matrix
        current = ", ".join(str(x) for x in self.rank_matrix)
        prompt = f"Current rank matrix (1st->...): {current}\nEnter comma-separated integer points for ranks (e.g. 10,8,6):"
        s = simpledialog.askstring("Edit Rank Matrix", prompt)
        if s is None:
            return
        s = s.strip()
        if not s:
            messagebox.showerror("Invalid Input", "No values entered.")
            return
        try:
            vals = [int(x.strip()) for x in s.split(',') if x.strip()]
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter only integers separated by commas.")
            return

        if not vals:
            messagebox.showerror("Invalid Input", "No valid integers provided.")
            return

        self.rank_matrix = vals
        messagebox.showinfo("Rank Matrix Updated", f"New rank matrix: {', '.join(str(x) for x in self.rank_matrix)}")


    def refresh_admin_lists(self):
        self.list_teams.delete(0, tk.END)
        for t in self.teams.keys(): self.list_teams.insert(tk.END, t)

        self.list_indiv.delete(0, tk.END)
        for i in self.individuals.keys(): self.list_indiv.insert(tk.END, i)

        self.list_events.delete(0, tk.END)
        for e in self.events: self.list_events.insert(tk.END, e)

        #update leaderboards
    def refresh_leaderboards(self):
        
        for item in self.tree_team.get_children(): self.tree_team.delete(item)
        sorted_teams = sorted(self.teams.items(), key=lambda x: x[1], reverse=True)
        for rank, (name, score) in enumerate(sorted_teams, 1):
            self.tree_team.insert("", "end", values=(rank, name, score))

        
        for item in self.tree_indiv.get_children(): self.tree_indiv.delete(item)
        sorted_indivs = sorted(self.individuals.items(), key=lambda x: x[1], reverse=True)
        for rank, (name, score) in enumerate(sorted_indivs, 1):
            self.tree_indiv.insert("", "end", values=(rank, name, score))

    def save_to_csv(self):
        #Saves data into a CSV file
        try:
            with open(CSV_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Name", "Score", "Secondary"])
                
                for team, score in self.teams.items():
                    writer.writerow(["TEAM", team, score, ""])
                for indiv, score in self.individuals.items():
                    writer.writerow(["INDIVIDUAL", indiv, score, ""])
                for event in self.events:
                    writer.writerow(["EVENT", event, "", ""])
                for team, members in self.team_members.items():
                    for member in members:
                        writer.writerow(["TEAM_MEMBER", team, "", member])
            
            messagebox.showinfo("Success", "Data saved to CSV successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

    def load_from_csv(self):
        #Loads data from the CSV
        if not os.path.exists(CSV_FILE):
            return

        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) < 2: continue
                
                item_type = row[0]
                name = row[1]
                score = int(row[2]) if len(row) > 2 and row[2] else 0

                if item_type == "TEAM":
                    self.teams[name] = score
                    self.team_members.setdefault(name, [])
                elif item_type == "INDIVIDUAL":
                    self.individuals[name] = score
                elif item_type == "EVENT":
                    self.events.append(name)
                elif item_type == "TEAM_MEMBER" and len(row) > 3:
                    team_name = name
                    member_name = row[3]
                    if team_name in self.teams and member_name in self.individuals:
                        self.team_members.setdefault(team_name, []).append(member_name)

if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()
