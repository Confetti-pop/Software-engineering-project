from datetime import date

# === User Classes ===

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class Patient(User):
    def __init__(self, username, password, name, dob, address):
        super().__init__(username, password, "patient")
        self.name = name
        self.dob = dob
        self.address = address
        self.medical_history = []
        self.treatment_plan = None
        self.appointments = []

    def view_info(self):
        print(f"\nName: {self.name}")
        print(f"DOB: {self.dob}")
        print(f"Address: {self.address}")

    def update_info(self):
        new_address = input("Enter new address: ")
        self.address = new_address
        print("Address updated successfully.")

    def view_appointments(self):
        if not self.appointments:
            print("No appointments scheduled.")
        else:
            for appt in self.appointments:
                print(f"{appt['date']} with Dr. {appt['doctor']} at {appt['time']}")

    def view_treatment_plan(self):
        if self.treatment_plan:
            print("\n--- Treatment Plan ---")
            print("Medications:", self.treatment_plan['medications'])
            print("Instructions:", self.treatment_plan['instructions'])
            print("Follow-up Date:", self.treatment_plan['follow_up_date'])
        else:
            print("No treatment plan available.")

    def view_medical_history(self):
        if not self.medical_history:
            print("No medical history recorded.")
        else:
            print("\n--- Medical History ---")
            for entry in self.medical_history:
                print(f"{entry['date']}: {entry['condition']} - {entry['notes']}")


class Doctor(User):
    def __init__(self, username, password, name, specialization):
        super().__init__(username, password, "doctor")
        self.name = name
        self.specialization = specialization
        self.patients = []
        self.appointments = []

    def view_patients(self):
        for i, p in enumerate(self.patients):
            print(f"{i+1}. {p.name} - DOB: {p.dob}")

    def view_patient_history(self):
        self.view_patients()
        choice = int(input("Select a patient to view history: ")) - 1
        patient = self.patients[choice]
        patient.view_medical_history()

    def create_treatment_plan(self):
        self.view_patients()
        choice = int(input("Select a patient to assign treatment: ")) - 1
        patient = self.patients[choice]
        medications = input("Enter medications (comma-separated): ")
        instructions = input("Enter instructions: ")
        follow_up = input("Enter follow-up date (YYYY-MM-DD): ")
        patient.treatment_plan = {
            "medications": medications,
            "instructions": instructions,
            "follow_up_date": follow_up
        }
        print("Treatment plan assigned.")

    def view_treatment_plans(self):
        for patient in self.patients:
            print(f"\nPatient: {patient.name}")
            patient.view_treatment_plan()

    def view_appointments(self):
        for appt in self.appointments:
            print(f"{appt['date']} with {appt['patient']} at {appt['time']}")


# === Sample Data ===

patients = [
    Patient("patient1", "pass1", "Alice Smith", "1990-05-12", "123 Main St"),
    Patient("patient2", "pass2", "Bob Jones", "1985-11-23", "456 Elm St")
]

doctor = Doctor("doctor1", "docpass", "Dr. Grey", "General Medicine")

patients[0].appointments.append({"date": "2025-04-06", "doctor": doctor.name, "time": "10:00 AM"})
patients[1].appointments.append({"date": "2025-04-07", "doctor": doctor.name, "time": "2:00 PM"})
doctor.appointments.extend([
    {"date": "2025-04-06", "patient": "Alice Smith", "time": "10:00 AM"},
    {"date": "2025-04-07", "patient": "Bob Jones", "time": "2:00 PM"}
])
doctor.patients = patients

users = {u.username: u for u in [*patients, doctor]}

# === Login System ===

def login():
    print("Welcome to the Medical Record System")
    username = input("Username: ")
    password = input("Password: ")
    user = users.get(username)
    if user and user.password == password:
        print(f"\nLogin successful! Welcome, {username}.\n")
        if user.role == "doctor":
            doctor_dashboard(user)
        else:
            patient_dashboard(user)
    else:
        print("Invalid username or password.")


def doctor_dashboard(user):
    while True:
        print("\n--- Doctor Dashboard ---")
        print("1. View Patients")
        print("2. View Patient Medical History")
        print("3. Create Treatment Plan")
        print("4. View Treatment Plans")
        print("5. View Appointments")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            user.view_patients()
        elif choice == "2":
            user.view_patient_history()
        elif choice == "3":
            user.create_treatment_plan()
        elif choice == "4":
            user.view_treatment_plans()
        elif choice == "5":
            user.view_appointments()
        elif choice == "6":
            print("Logging out...\n")
            break
        else:
            print("Invalid choice.")


def patient_dashboard(user):
    while True:
        print("\n--- Patient Dashboard ---")
        print("1. View Personal Info")
        print("2. View Appointments")
        print("3. View Treatment Plan")
        print("4. View Medical History")
        print("5. Update Address")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            user.view_info()
        elif choice == "2":
            user.view_appointments()
        elif choice == "3":
            user.view_treatment_plan()
        elif choice == "4":
            user.view_medical_history()
        elif choice == "5":
            user.update_info()
        elif choice == "6":
            print("Logging out...\n")
            break
        else:
            print("Invalid choice.")


# === Run the program ===
if __name__ == "__main__":
    login()
