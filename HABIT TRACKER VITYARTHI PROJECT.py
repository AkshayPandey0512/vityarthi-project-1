import json
import os
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

class HabitTracker:
    def __init__(self, data_file="habits.json"):
        self.data_file = data_file
        self.habits = self.load_data()
        self.categories = ["Health", "Productivity", "Learning", "Finance", "Social", "Other"]
    
    def load_data(self):
        """Load habit data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {"habits": {}, "completions": {}}
    
    def save_data(self):
        """Save habit data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.habits, f, indent=2)
    
    def add_habit(self, name, category, frequency="daily", goal=None):
        """Add a new habit to track"""
        habit_id = len(self.habits["habits"]) + 1
        
        self.habits["habits"][habit_id] = {
            "name": name,
            "category": category,
            "frequency": frequency,
            "goal": goal,
            "created_date": datetime.now().isoformat(),
            "current_streak": 0,
            "longest_streak": 0
        }
        
        if habit_id not in self.habits["completions"]:
            self.habits["completions"][habit_id] = []
        
        self.save_data()
        print(f"✅ Added habit: {name}")
        return habit_id
    
    def mark_complete(self, habit_id):
        """Mark a habit as completed for today"""
        today = datetime.now().date().isoformat()
        
        if habit_id not in self.habits["completions"]:
            self.habits["completions"][habit_id] = []
        
        # Check if already completed today
        if today in self.habits["completions"][habit_id]:
            print("❌ Already completed today!")
            return False
        
        self.habits["completions"][habit_id].append(today)
        
        # Update streaks
        self.update_streaks(habit_id)
        
        self.save_data()
        print(f"✅ Marked '{self.habits['habits'][habit_id]['name']}' as complete!")
        return True
    
    def update_streaks(self, habit_id):
        """Update current and longest streaks for a habit"""
        completions = sorted(self.habits["completions"][habit_id])
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        if completions:
            current_date = datetime.now().date()
            prev_date = current_date
            
            # Check current streak (consecutive days up to today)
            for i in range(len(completions)-1, -1, -1):
                comp_date = datetime.fromisoformat(completions[i]).date()
                if comp_date == prev_date or comp_date == prev_date - timedelta(days=1):
                    current_streak += 1
                    prev_date = comp_date
                else:
                    break
            
            # Calculate longest streak
            temp_streak = 1
            for i in range(1, len(completions)):
                current = datetime.fromisoformat(completions[i]).date()
                previous = datetime.fromisoformat(completions[i-1]).date()
                
                if (current - previous).days == 1:
                    temp_streak += 1
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
            
            longest_streak = max(longest_streak, temp_streak)
        
        self.habits["habits"][habit_id]["current_streak"] = current_streak
        self.habits["habits"][habit_id]["longest_streak"] = longest_streak
    
    def get_today_completions(self):
        """Get habits completed today"""
        today = datetime.now().date().isoformat()
        completed_today = []
        
        for habit_id, completions in self.habits["completions"].items():
            if today in completions:
                completed_today.append(habit_id)
        
        return completed_today
    
    def view_habits(self, filter_category=None):
        """View all habits with completion status"""
        today_completions = self.get_today_completions()
        
        print("\n" + "="*60)
        print("📊 YOUR HABITS")
        print("="*60)
        
        for habit_id, habit in self.habits["habits"].items():
            if filter_category and habit["category"] != filter_category:
                continue
            
            completed = "✅" if habit_id in today_completions else "❌"
            streak = habit["current_streak"]
            streak_emoji = "🔥" if streak >= 7 else "⚡" if streak >= 3 else "📈"
            
            print(f"\n{completed} {habit['name']}")
            print(f"   Category: {habit['category']} | Frequency: {habit['frequency']}")
            print(f"   Current Streak: {streak} days {streak_emoji}")
            print(f"   Longest Streak: {habit['longest_streak']} days")
            
            if habit['goal']:
                print(f"   Goal: {habit['goal']}")
    
    def view_weekly_report(self):
        """Show weekly completion statistics"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_dates = [week_start + timedelta(days=i) for i in range(7)]
        
        print("\n" + "="*60)
        print("📅 WEEKLY REPORT")
        print("="*60)
        
        # Calculate completion rates
        total_habits = len(self.habits["habits"])
        daily_completions = []
        
        for date in week_dates:
            date_str = date.isoformat()
            day_completions = 0
            
            for completions in self.habits["completions"].values():
                if date_str in completions:
                    day_completions += 1
            
            daily_completions.append(day_completions)
        
        # Display weekly calendar
        print("\n📆 This Week's Progress:")
        for i, date in enumerate(week_dates):
            completed = daily_completions[i]
            total = total_habits
            percentage = (completed / total) * 100 if total > 0 else 0
            
            day_name = date.strftime('%a')
            date_str = date.strftime('%m/%d')
            
            progress_bar = "█" * int(percentage / 20) + "░" * (5 - int(percentage / 20))
            print(f"{day_name} {date_str}: {progress_bar} {completed}/{total} ({percentage:.0f}%)")
        
        # Overall statistics
        week_completed = sum(daily_completions)
        week_possible = total_habits * 7
        week_percentage = (week_completed / week_possible) * 100 if week_possible > 0 else 0
        
        print(f"\n📈 Weekly Completion: {week_percentage:.1f}%")
        print(f"✅ Total Completions: {week_completed}/{week_possible}")
    
    def view_category_stats(self):
        """Show statistics by category"""
        category_stats = defaultdict(lambda: {"total": 0, "completed": 0, "streaks": []})
        
        for habit_id, habit in self.habits["habits"].items():
            category = habit["category"]
            category_stats[category]["total"] += 1
            category_stats[category]["streaks"].append(habit["current_streak"])
        
        # Calculate today's completions by category
        today_completions = self.get_today_completions()
        for habit_id in today_completions:
            category = self.habits["habits"][habit_id]["category"]
            category_stats[category]["completed"] += 1
        
        print("\n" + "="*60)
        print("📈 CATEGORY STATISTICS")
        print("="*60)
        
        for category, stats in category_stats.items():
            completion_rate = (stats["completed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            avg_streak = sum(stats["streaks"]) / len(stats["streaks"]) if stats["streaks"] else 0
            
            print(f"\n{category}:")
            print(f"  Today: {stats['completed']}/{stats['total']} ({completion_rate:.1f}%)")
            print(f"  Average Streak: {avg_streak:.1f} days")
            print(f"  Best Streak: {max(stats['streaks']) if stats['streaks'] else 0} days")
    
    def delete_habit(self, habit_id):
        """Delete a habit"""
        if habit_id in self.habits["habits"]:
            habit_name = self.habits["habits"][habit_id]["name"]
            del self.habits["habits"][habit_id]
            del self.habits["completions"][habit_id]
            self.save_data()
            print(f"🗑️ Deleted habit: {habit_name}")
        else:
            print("❌ Habit not found!")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🔥 HABIT TRACKER")
        print("="*60)
        print("1. 📝 Add New Habit")
        print("2. ✅ Mark Habit Complete")
        print("3. 📊 View All Habits")
        print("4. 📅 Weekly Report")
        print("5. 📈 Category Statistics")
        print("6. 🗑️ Delete Habit")
        print("7. 🚪 Exit")
        print("="*60)
    
    def run(self):
        """Main application loop"""
        print("🔥 Welcome to your Personal Habit Tracker!")
        
        while True:
            self.show_menu()
            choice = input("\nChoose option (1-7): ").strip()
            
            if choice == '1':
                print("\nAdd New Habit:")
                name = input("Habit name: ")
                print("Categories:", ", ".join(self.categories))
                category = input("Category: ")
                frequency = input("Frequency (daily/weekly): ") or "daily"
                goal = input("Goal (optional): ")
                self.add_habit(name, category, frequency, goal)
            
            elif choice == '2':
                self.view_habits()
                try:
                    habit_id = input("\nEnter habit ID to mark complete: ")
                    if habit_id:
                        self.mark_complete(habit_id)
                except:
                    print("❌ Invalid habit ID!")
            
            elif choice == '3':
                print("\nCategories:", ", ".join(self.categories))
                filter_cat = input("Filter by category (or press Enter for all): ")
                self.view_habits(filter_cat if filter_cat else None)
            
            elif choice == '4':
                self.view_weekly_report()
            
            elif choice == '5':
                self.view_category_stats()
            
            elif choice == '6':
                self.view_habits()
                try:
                    habit_id = input("\nEnter habit ID to delete: ")
                    if habit_id:
                        self.delete_habit(habit_id)
                except:
                    print("❌ Invalid habit ID!")
            
            elif choice == '7':
                print("👋 Keep building those habits! Goodbye!")
                break
            
            else:
                print("❌ Invalid choice!")

# Start the habit tracker
if __name__ == "__main__":
    tracker = HabitTracker()
    tracker.run()