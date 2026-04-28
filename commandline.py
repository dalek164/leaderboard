import csv
import os

#octopus king

class Participant:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.events_participated = set()

class Team(Participant):
    def __init__(self, name, members):
        super().__init__(name)
        self.members = members

class Individual(Participant):
    pass

class Event:
    def __init__(self, name, event_type):
        self.name = name
        self.event_type = event_type  # 'team' or 'individual'
        self.results = []  # list of (participant_name, rank)

class Tournament:
    def __init__(self):
        self.teams = []
        self.individuals = []
        self.events = []
        self.points_system = {1: 10, 2: 8, 3: 6, 4: 4, 5: 2}

    def add_team(self, name, members):
        if len(self.teams) >= 4:
            print("Maximum 4 teams allowed.")
            return
        if len(members) != 5:
            print("Each team must have exactly 5 members.")
            return
        team = Team(name, members)
        self.teams.append(team)
        print(f"Team '{name}' added successfully.")

    def add_individual(self, name):
        if len(self.individuals) >= 20:
            print("Maximum 20 individuals allowed.")
            return
        individual = Individual(name)
        self.individuals.append(individual)
        print(f"Individual '{name}' added successfully.")

    def add_event(self, name, event_type):
        if event_type not in ['team', 'individual']:
            print("Event type must be 'team' or 'individual'.")
            return
        event = Event(name, event_type)
        self.events.append(event)
        print(f"Event '{name}' ({event_type}) added successfully.")

    def record_results(self, event_name, results):
        event = next((e for e in self.events if e.name == event_name), None)
        if not event:
            print(f"Event '{event_name}' not found.")
            return

        event.results = results
        for participant_name, rank in results:
            points = self.points_system.get(rank, 1)  # 1 point for ranks below 5

            if event.event_type == 'team':
                team = next((t for t in self.teams if t.name == participant_name), None)
                if team:
                    team.points += points
                    team.events_participated.add(event_name)
            else:  # individual
                individual = next((i for i in self.individuals if i.name == participant_name), None)
                if individual:
                    individual.points += points
                    individual.events_participated.add(event_name)

        print(f"Results recorded for event '{event_name}'.")

    def show_leaderboard(self):
        print("\n=== TEAM LEADERBOARD ===")
        sorted_teams = sorted(self.teams, key=lambda x: x.points, reverse=True)
        for i, team in enumerate(sorted_teams, 1):
            print(f"{i}. {team.name}: {team.points} points (Events: {len(team.events_participated)})")

        print("\n=== INDIVIDUAL LEADERBOARD ===")
        sorted_individuals = sorted(self.individuals, key=lambda x: x.points, reverse=True)
        for i, individual in enumerate(sorted_individuals, 1):
            print(f"{i}. {individual.name}: {individual.points} points (Events: {len(individual.events_participated)})")

    def show_overall_winners(self):
        print("\n=== OVERALL WINNERS ===")

        if self.teams:
            team_winner = max(self.teams, key=lambda x: x.points)
            print(f"Winning Team: {team_winner.name} with {team_winner.points} points")

        if self.individuals:
            individual_winner = max(self.individuals, key=lambda x: x.points)
            print(f"Winning Individual: {individual_winner.name} with {individual_winner.points} points")

    def save_data(self, filename='tournament_data'):
        teams_file = f"{filename}_teams.csv"
        individuals_file = f"{filename}_individuals.csv"
        events_file = f"{filename}_events.csv"

        with open(teams_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'members', 'points', 'events'])
            writer.writeheader()
            for t in self.teams:
                writer.writerow({
                    'name': t.name,
                    'members': ';'.join(t.members),
                    'points': t.points,
                    'events': ';'.join(sorted(t.events_participated))
                })

        with open(individuals_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'points', 'events'])
            writer.writeheader()
            for i in self.individuals:
                writer.writerow({
                    'name': i.name,
                    'points': i.points,
                    'events': ';'.join(sorted(i.events_participated))
                })

        with open(events_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'type', 'results'])
            writer.writeheader()
            for e in self.events:
                results_serialized = ';'.join(f"{name}|{rank}" for name, rank in e.results)
                writer.writerow({
                    'name': e.name,
                    'type': e.event_type,
                    'results': results_serialized
                })

        print(f"Data saved to {teams_file}, {individuals_file}, {events_file}")

    def load_data(self, filename='tournament_data'):
        teams_file = f"{filename}_teams.csv"
        individuals_file = f"{filename}_individuals.csv"
        events_file = f"{filename}_events.csv"

        if not (os.path.exists(teams_file) or os.path.exists(individuals_file) or os.path.exists(events_file)):
            print(f"CSV files not found. Starting with empty tournament.")
            return

        if os.path.exists(teams_file):
            with open(teams_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.teams = []
                for row in reader:
                    team = Team(row['name'], row['members'].split(';') if row['members'] else [])
                    team.points = int(row['points']) if row['points'] else 0
                    team.events_participated = set(row['events'].split(';')) if row['events'] else set()
                    self.teams.append(team)

        if os.path.exists(individuals_file):
            with open(individuals_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.individuals = []
                for row in reader:
                    individual = Individual(row['name'])
                    individual.points = int(row['points']) if row['points'] else 0
                    individual.events_participated = set(row['events'].split(';')) if row['events'] else set()
                    self.individuals.append(individual)

        if os.path.exists(events_file):
            with open(events_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.events = []
                for row in reader:
                    event = Event(row['name'], row['type'])
                    if row['results']:
                        event.results = [
                            (item.rsplit('|', 1)[0], int(item.rsplit('|', 1)[1]))
                            for item in row['results'].split(';') if item
                        ]
                    self.events.append(event)

        print(f"Data loaded from CSV files")

def main():
    tournament = Tournament()
    tournament.load_data()

    while True:
        print("\n=== TOURNAMENT SCORING SYSTEM ===")
        print("1. Add Team")
        print("2. Add Individual")
        print("3. Add Event")
        print("4. Record Results")
        print("5. Show Leaderboards")
        print("6. Show Overall Winners")
        print("7. Save Data")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':
            name = input("Enter team name: ").strip()
            members = []
            for i in range(5):
                member = input(f"Enter member {i+1}: ").strip()
                members.append(member)
            tournament.add_team(name, members)

        elif choice == '2':
            name = input("Enter individual name: ").strip()
            tournament.add_individual(name)

        elif choice == '3':
            name = input("Enter event name: ").strip()
            event_type = input("Enter event type (team/individual): ").strip().lower()
            tournament.add_event(name, event_type)

        elif choice == '4':
            if not tournament.events:
                print("No events added yet.")
                continue
            print("Available events:")
            for i, event in enumerate(tournament.events, 1):
                print(f"{i}. {event.name} ({event.event_type})")
            event_choice = int(input("Choose event number: ")) - 1
            if 0 <= event_choice < len(tournament.events):
                event = tournament.events[event_choice]
                results = []
                num_participants = int(input("Enter number of participants in results: "))
                for i in range(num_participants):
                    participant = input(f"Enter participant {i+1} name: ").strip()
                    rank = int(input(f"Enter rank for {participant}: "))
                    results.append((participant, rank))
                tournament.record_results(event.name, results)
            else:
                print("Invalid event choice.")

        elif choice == '5':
            tournament.show_leaderboard()

        elif choice == '6':
            tournament.show_overall_winners()

        elif choice == '7':
            tournament.save_data()

        elif choice == '8':
            tournament.save_data()
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
