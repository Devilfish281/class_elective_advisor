# ui/gui.py
import json
import logging
import tkinter as tk
from tkinter import PhotoImage, messagebox, ttk

from ai_integration.ai_module import get_recommendations_ai
from database import db_operations  # Importing db_operations for authenticatio

logger = logging.getLogger(__name__)  # Reuse the global logger


# Global variable to track login status and current user
login_status = False
current_user = None  # Will hold user details after login

# Dictionary to store navigation button references
nav_buttons = {}


def main_int_ui():
    """Initializes and runs the main interface of the Smart Elective Advisor."""

    logger.info("Initializing the Smart Elective Advisor GUI.")

    # Initialize the main window
    root = tk.Tk()
    root.title("Smart Elective Advisor")
    root.geometry("1200x800")
    root.resizable(False, False)  # Fixed window size for consistency

    # Set the window icon (ensure the icon file exists)
    try:
        root.iconphoto(False, PhotoImage(file="icons/university_logo.png"))
    except Exception as e:
        logger.error(f"Icon file not found or invalid: {e}")

    # Configure grid layout
    root.columnconfigure(0, weight=1)  # Navigation Menu
    root.columnconfigure(1, weight=4)  # Content Display Area
    root.rowconfigure(0, weight=1)

    # Create Navigation Menu Frame
    nav_frame = ttk.Frame(root, width=200, relief="raised")
    nav_frame.grid(row=0, column=0, sticky="ns")
    nav_frame.grid_propagate(False)  # Prevent frame from resizing based on its content
    nav_frame.columnconfigure(0, weight=1)

    # Create Content Display Area Frame
    content_frame = ttk.Frame(root, relief="sunken")
    content_frame.grid(row=0, column=1, sticky="nsew")
    content_frame.columnconfigure(0, weight=1)
    content_frame.rowconfigure(0, weight=1)

    # Define menu items with their respective icons and commands
    menu_items = [
        ("Home Dashboard", "icons/home.png", show_home),
        ("Login", "icons/login.png", show_login),
        ("Logout", "icons/logout.png", show_logout),
        # ("User Registration", "icons/register.png", show_registration),  # Removed
        ("Preferences", "icons/preferences.png", show_preferences),
        ("Recommendations", "icons/recommendations.png", show_recommendations),
        ("Profile", "icons/profile.png", show_profile),
        ("Help", "icons/help.png", show_help),
    ]

    # Load and create buttons for the Navigation Menu
    for idx, (text, icon_path, command) in enumerate(menu_items):
        try:
            icon = PhotoImage(file=icon_path)
        except Exception as e:
            logger.warning(f"Icon '{icon_path}' not found. Using text only. Error: {e}")
            icon = None

        btn = ttk.Button(
            nav_frame,
            text=text,
            image=icon,
            compound="left",
            command=lambda cmd=command: cmd(content_frame),
        )
        btn.image = icon  # Keep a reference to prevent garbage collection
        btn.grid(row=idx, column=0, padx=10, pady=10, sticky="ew")

        # Store the button reference in the nav_buttons dictionary
        nav_buttons[text] = btn

    # Initialize button states based on the default login_status
    update_nav_buttons()

    # Initialize with the Home Dashboard
    show_home(content_frame)

    # Start the Tkinter event loop
    logger.info("Starting the Tkinter main loop.")
    root.mainloop()


def clear_content(frame):
    """Clears all widgets from the content display area."""
    for widget in frame.winfo_children():
        widget.destroy()


def update_nav_buttons():
    """Updates the state of navigation buttons based on login_status."""
    global login_status, current_user
    if login_status and current_user:
        # Show Logout button, hide Login button
        nav_buttons["Logout"].grid()
        nav_buttons["Login"].grid_remove()

        # Enable other buttons
        nav_buttons["Home Dashboard"].config(state="normal")
        nav_buttons["Preferences"].config(state="normal")
        nav_buttons["Recommendations"].config(state="normal")
        nav_buttons["Profile"].config(state="normal")
        nav_buttons["Help"].config(state="normal")
    else:
        # Show Login button, hide Logout button
        nav_buttons["Login"].grid()
        nav_buttons["Logout"].grid_remove()

        # Disable other buttons
        nav_buttons["Home Dashboard"].config(state="normal")
        nav_buttons["Preferences"].config(state="disabled")
        nav_buttons["Recommendations"].config(state="disabled")
        nav_buttons["Profile"].config(state="disabled")
        nav_buttons["Help"].config(state="normal")


def show_home(frame):
    """Displays the Home Dashboard in the content area."""
    logger.info("Displaying Home Dashboard.")
    clear_content(frame)

    header_font = ("Helvetica", 16, "bold")
    header_label = ttk.Label(
        frame, text="Welcome to Smart Elective Advisor", font=header_font
    )
    header_label.pack(pady=20)

    # Placeholder for additional home content
    overview_text = (
        "The Smart Elective Advisor helps CS students select the best elective courses based on their "
        "interests, career aspirations, and academic performance. Navigate through the menu to get started."
    )
    overview_label = ttk.Label(
        frame, text=overview_text, wraplength=800, justify="center"
    )
    overview_label.pack(pady=10)


# ui/gui.py


def show_login(frame):
    """Displays the Login Page in the content area."""
    global login_status, current_user
    logger.info("Displaying Login Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Login", font=header_font)
    header_label.pack(pady=20)

    # Login Form Frame
    login_frame = ttk.Frame(frame)
    login_frame.pack(pady=10)

    # Email
    email_label = ttk.Label(login_frame, text="Email:")
    email_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    email_entry = ttk.Entry(login_frame, width=30)
    email_entry.grid(row=0, column=1, padx=5, pady=5)

    # Password
    password_label = ttk.Label(login_frame, text="Password:")
    password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    password_entry = ttk.Entry(login_frame, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Login Button
    def perform_login():
        global login_status, current_user
        email = email_entry.get()
        password = password_entry.get()
        logger.debug(f"Attempting login with Email: {email}")
        if email and password:
            # Authenticate user using db_operations
            user = db_operations.authenticate_user(email, password)
            if user:
                login_status = True  # Update login status
                current_user = user  # Store current user details
                messagebox.showinfo(
                    "Login Successful", f"Welcome back, {user['full_name']}!"
                )
                logger.info(f"User '{email}' logged in successfully.")
                # Redirect to Home Dashboard after successful login
                # show_home(frame)
                show_preferences(frame)  # Redirects to Preferences Page
                update_nav_buttons()  # Refresh button states
            else:
                messagebox.showerror("Login Failed", "Invalid email or password.")
                logger.warning(f"Authentication failed for user: {email}")
        else:
            messagebox.showerror(
                "Login Failed", "Please enter both email and password."
            )
            logger.warning("Login failed due to incomplete credentials.")

    login_button = ttk.Button(frame, text="Login", command=perform_login)
    login_button.pack(pady=10)

    # Register Link
    register_label = ttk.Label(
        frame,
        text="Don't have an account? Register here.",
        foreground="blue",
        cursor="hand2",
    )
    register_label.pack(pady=5)
    register_label.bind("<Button-1>", lambda e: show_registration(frame))


def show_logout(frame):
    """Handles user logout."""
    global login_status, current_user
    logger.info("User initiated logout.")

    # Implement logout logic (e.g., clear session, tokens)
    login_status = False  # Reset login status
    current_user = None  # Clear current user details

    messagebox.showinfo("Logout", "You have been logged out successfully.")
    show_home(frame)  # Redirect to Home Dashboard after logout
    update_nav_buttons()  # Refresh button states


def show_registration(frame):
    """Displays the User Registration Form in the content area."""
    global login_status, current_user
    logger.info("Displaying User Registration Form.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="User Registration", font=header_font)
    header_label.pack(pady=20)

    # Registration Form Frame
    reg_frame = ttk.Frame(frame)
    reg_frame.pack(pady=10)

    # Full Name
    name_label = ttk.Label(reg_frame, text="Full Name:")
    name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    name_entry = ttk.Entry(reg_frame, width=30)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Email
    email_label = ttk.Label(reg_frame, text="Email:")
    email_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    email_entry = ttk.Entry(reg_frame, width=30)
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    # Password
    password_label = ttk.Label(reg_frame, text="Password:")
    password_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    password_entry = ttk.Entry(reg_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    # Confirm Password
    confirm_label = ttk.Label(reg_frame, text="Confirm Password:")
    confirm_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
    confirm_entry = ttk.Entry(reg_frame, width=30, show="*")
    confirm_entry.grid(row=3, column=1, padx=5, pady=5)

    # Registration Button
    def perform_registration():
        full_name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        confirm_password = confirm_entry.get()
        logger.debug(f"Attempting registration for Email: {email}")

        # Input Validations
        if not full_name:
            messagebox.showerror("Input Error", "Please enter your full name.")
            logger.warning("Registration failed: Full name not provided.")
            return
        if not email or "@" not in email:
            messagebox.showerror("Input Error", "Please enter a valid email address.")
            logger.warning("Registration failed: Invalid email format.")
            return

        # Define special characters using a raw string
        password_special_chars = r"!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~"
        if (
            len(password) < 8
            or not any(char.isdigit() for char in password)
            or not any(char in password_special_chars for char in password)
        ):
            messagebox.showerror(
                "Input Error",
                "Password must be at least 8 characters long and include numbers and special characters.",
            )
            logger.warning("Registration failed: Weak password.")
            return
        if password != confirm_password:
            messagebox.showerror("Input Error", "Passwords do not match.")
            logger.warning("Registration failed: Passwords do not match.")
            return

        # Register user using db_operations
        success = db_operations.register_user(
            full_name=full_name, email=email, password=password
        )

        if success:
            messagebox.showinfo(
                "Registration Successful", "Your account has been created successfully!"
            )
            logger.info(f"User '{email}' registered successfully.")
            show_login(frame)  # Redirect to Login after successful registration
        else:
            messagebox.showerror(
                "Registration Failed", "An account with this email already exists."
            )
            logger.warning(f"Registration failed: Email '{email}' already exists.")

    register_button = ttk.Button(frame, text="Register", command=perform_registration)
    register_button.pack(pady=10)

    # Back to Login Link
    back_label = ttk.Label(
        frame,
        text="Already have an account? Login here.",
        foreground="blue",
        cursor="hand2",
    )
    back_label.pack(pady=5)
    back_label.bind("<Button-1>", lambda e: show_login(frame))


"""
Cascading Dropdowns:

College Dropdown:
Populated with data from the Colleges table.
On selection, triggers fetching and populating the Department dropdown.
Department Dropdown:
Populated based on the selected college.
On selection, triggers fetching and populating the Degree Level dropdown.
Degree Level Dropdown:
Populated based on the selected department.
On selection, triggers fetching and populating the Degree dropdown.
Degree Dropdown:
Populated based on the selected degree level.
Handling Existing Preferences:

When a user accesses the Preferences page, their existing preferences are fetched and used to pre-populate the dropdowns.
Functions like get_college_name, get_department_name, etc., help in translating IDs back to names for display.
Saving Preferences:

Collects the selected IDs from the dropdowns.
Validates that all selections are made before saving.
Uses the save_user_preferences function from db_operations.py to store the preferences.
Resetting Preferences:

Clears all selections and disables dependent dropdowns to allow the user to start fresh.
Mapping Names to IDs:

Mappings (college_id_map, department_id_map, etc.) are maintained to translate selected names back to their corresponding IDs for database storage.
Error Handling:

Provides error messages if any dropdown selection is missing during the save operation.
Logs all significant actions and warnings for easier debugging.
"""
# ui/gui.py


def show_preferences(frame):
    """Displays the Preferences Form in the content area."""
    if not login_status:
        messagebox.showerror("Access Denied", "Please log in to access Preferences.")
        logger.warning("Unauthorized access attempt to Preferences page.")
        return  # Exit the function without displaying the page

    logger.info("Displaying Preferences Form.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="User Preferences", font=header_font)
    header_label.pack(pady=20)

    # Preferences Form Frame
    pref_frame = ttk.Frame(frame)
    pref_frame.pack(pady=10)

    # Fetch existing preferences
    existing_prefs = db_operations.get_user_preferences(current_user["user_id"])

    # Initialize mapping dictionaries
    college_id_map = {}
    department_id_map = {}
    degree_level_id_map = {}
    degree_id_map = {}
    job_id_map = {}  # Maps job_name to job_description
    job_id_to_name_map = {}  # Maps job_id to job_name

    # Fetch mapping from ID to name for each category
    def get_college_name(college_id):
        colleges = db_operations.get_colleges()
        for college in colleges:
            if college["college_id"] == college_id:
                return college["name"]
        return "Select your college"

    def get_department_name(department_id):
        if not existing_prefs.get("college_id"):
            return "Select your department"
        departments = db_operations.get_departments(existing_prefs["college_id"])
        for dept in departments:
            if dept["department_id"] == department_id:
                return dept["name"]
        return "Select your department"

    def get_degree_level_name(degree_level_id):
        if not existing_prefs.get("department_id"):
            return "Select your degree level"
        degree_levels = db_operations.get_degree_levels(existing_prefs["department_id"])
        for dl in degree_levels:
            if dl["degree_level_id"] == degree_level_id:
                return dl["name"]
        return "Select your degree level"

    def get_degree_name(degree_id):
        if not existing_prefs.get("degree_level_id"):
            return "Select your degree"
        degrees = db_operations.get_degrees(existing_prefs["degree_level_id"])
        for deg in degrees:
            if deg["degree_id"] == degree_id:
                return deg["name"]
        return "Select your degree"

    # College Selection
    college_label = ttk.Label(pref_frame, text="College of:")
    college_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    college_var = tk.StringVar()
    college_combo = ttk.Combobox(
        pref_frame,
        textvariable=college_var,
        state="readonly",
        width=45,  # Increased width
    )
    college_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Populate Colleges
    colleges = db_operations.get_colleges()
    college_combo["values"] = [college["name"] for college in colleges]
    college_id_map = {college["name"]: college["college_id"] for college in colleges}

    # Set existing preference if available
    if existing_prefs.get("college_id"):
        college_name = get_college_name(existing_prefs["college_id"])
        if college_name in college_id_map:
            college_combo.set(college_name)
    else:
        college_combo.set("Select your college")

    # Department Selection
    department_label = ttk.Label(pref_frame, text="Department:")
    department_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    department_var = tk.StringVar()
    department_combo = ttk.Combobox(
        pref_frame,
        textvariable=department_var,
        state="disabled",
        width=45,  # Updated width
    )
    department_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Degree Level Selection
    degree_level_label = ttk.Label(pref_frame, text="Degree Level:")
    degree_level_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    degree_level_var = tk.StringVar()
    degree_level_combo = ttk.Combobox(
        pref_frame,
        textvariable=degree_level_var,
        state="disabled",
        width=45,  # Updated width
    )
    degree_level_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Degree Selection
    degree_label = ttk.Label(pref_frame, text="Degree:")
    degree_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
    degree_var = tk.StringVar()
    degree_combo = ttk.Combobox(
        pref_frame, textvariable=degree_var, state="disabled", width=45  # Updated width
    )
    degree_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    # Job Selection (New)
    job_label = ttk.Label(pref_frame, text="Preferred Job:")
    job_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
    job_var = tk.StringVar()
    job_combo = ttk.Combobox(
        pref_frame,
        textvariable=job_var,
        state="disabled",
        width=45,  # Updated width
    )
    job_combo.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    # Job Description Display
    job_desc_label = ttk.Label(frame, text="Job Description:")
    job_desc_label.pack(pady=(10, 0), anchor="w", padx=20)
    job_desc_text = tk.Text(frame, height=5, wrap="word", state="disabled", width=100)
    job_desc_text.pack(pady=5, padx=20, fill="x")

    # Functions to handle dropdown changes
    def on_college_select(event):
        selected_college = college_var.get()
        if selected_college != "Select your college":
            college_id = college_id_map.get(selected_college)
            departments = db_operations.get_departments(college_id)
            if departments:
                department_combo["values"] = [dept["name"] for dept in departments]
                department_id_map.clear()
                department_id_map.update(
                    {dept["name"]: dept["department_id"] for dept in departments}
                )
                department_combo["state"] = "readonly"
                department_combo.set("Select your department")
                degree_level_combo.set("")
                degree_level_combo["values"] = []
                degree_level_combo["state"] = "disabled"
                degree_combo.set("")
                degree_combo["values"] = []
                degree_combo["state"] = "disabled"
                job_combo.set("")
                job_combo["values"] = []
                job_combo["state"] = "disabled"
                job_desc_text.config(state="normal")
                job_desc_text.delete("1.0", tk.END)
                job_desc_text.config(state="disabled")

                # If existing preference exists, set it
                if existing_prefs.get("department_id"):
                    department_name = get_department_name(
                        existing_prefs["department_id"]
                    )
                    if department_name in department_id_map:
                        department_combo.set(department_name)
                        on_department_select(None)
        else:
            department_combo.set("")
            department_combo["values"] = []
            department_combo["state"] = "disabled"
            degree_level_combo.set("")
            degree_level_combo["values"] = []
            degree_level_combo["state"] = "disabled"
            degree_combo.set("")
            degree_combo["values"] = []
            degree_combo["state"] = "disabled"
            job_combo.set("")
            job_combo["values"] = []
            job_combo["state"] = "disabled"
            job_desc_text.config(state="normal")
            job_desc_text.delete("1.0", tk.END)
            job_desc_text.config(state="disabled")

    def on_department_select(event):
        selected_department = department_var.get()
        if selected_department != "Select your department":
            department_id = department_id_map.get(selected_department)
            degree_levels = db_operations.get_degree_levels(department_id)
            if degree_levels:
                degree_level_combo["values"] = [dl["name"] for dl in degree_levels]
                degree_level_id_map.clear()
                degree_level_id_map.update(
                    {dl["name"]: dl["degree_level_id"] for dl in degree_levels}
                )
                degree_level_combo["state"] = "readonly"
                degree_level_combo.set("Select your degree level")
                degree_combo.set("")
                degree_combo["values"] = []
                degree_combo["state"] = "disabled"
                job_combo.set("")
                job_combo["values"] = []
                job_combo["state"] = "disabled"
                job_desc_text.config(state="normal")
                job_desc_text.delete("1.0", tk.END)
                job_desc_text.config(state="disabled")

                # If existing preference exists, set it
                if existing_prefs.get("degree_level_id"):
                    degree_level_name = get_degree_level_name(
                        existing_prefs["degree_level_id"]
                    )
                    if degree_level_name in degree_level_id_map:
                        degree_level_combo.set(degree_level_name)
                        on_degree_level_select(None)
        else:
            degree_level_combo.set("")
            degree_level_combo["values"] = []
            degree_level_combo["state"] = "disabled"
            degree_combo.set("")
            degree_combo["values"] = []
            degree_combo["state"] = "disabled"
            job_combo.set("")
            job_combo["values"] = []
            job_combo["state"] = "disabled"
            job_desc_text.config(state="normal")
            job_desc_text.delete("1.0", tk.END)
            job_desc_text.config(state="disabled")

    def on_degree_level_select(event):
        selected_degree_level = degree_level_var.get()
        if selected_degree_level != "Select your degree level":
            degree_level_id = degree_level_id_map.get(selected_degree_level)
            degrees = db_operations.get_degrees(degree_level_id)
            if degrees:
                degree_combo["values"] = [deg["name"] for deg in degrees]
                degree_id_map.clear()
                degree_id_map.update({deg["name"]: deg["degree_id"] for deg in degrees})
                degree_combo["state"] = "readonly"
                degree_combo.set("Select your degree")
                job_combo.set("")
                job_combo["values"] = []
                job_combo["state"] = "disabled"
                job_desc_text.config(state="normal")
                job_desc_text.delete("1.0", tk.END)
                job_desc_text.config(state="disabled")

                # If existing preference exists, set it
                if existing_prefs.get("degree_id"):
                    degree_name = get_degree_name(existing_prefs["degree_id"])
                    if degree_name in degree_id_map:
                        degree_combo.set(degree_name)
                        on_degree_select_degree(None)
        else:
            degree_combo.set("")
            degree_combo["values"] = []
            degree_combo["state"] = "disabled"
            job_combo.set("")
            job_combo["values"] = []
            job_combo["state"] = "disabled"
            job_desc_text.config(state="normal")
            job_desc_text.delete("1.0", tk.END)
            job_desc_text.config(state="disabled")

    def on_degree_select_degree(event):
        selected_degree = degree_var.get()
        if selected_degree != "Select your degree":
            degree_id = degree_id_map.get(selected_degree)
            jobs = db_operations.get_jobs_by_degree(degree_id)
            if jobs:
                job_combo["values"] = [job["name"] for job in jobs]
                job_id_map.clear()
                job_id_to_name_map.clear()
                for job in jobs:
                    job_id_map[job["name"]] = job["description"]
                    job_id_to_name_map[job["job_id"]] = job["name"]
                job_combo["state"] = "readonly"
                job_combo.set("Select your job")
                job_desc_text.config(state="normal")
                job_desc_text.delete("1.0", tk.END)
                job_desc_text.config(state="disabled")

                # If existing preference exists, set it
                if existing_prefs.get("job_id"):
                    job_name = job_id_to_name_map.get(
                        existing_prefs["job_id"], "Select your job"
                    )
                    if job_name in job_id_map:
                        job_combo.set(job_name)
                        display_job_description(job_name)
            else:
                # No jobs available for the selected degree
                job_combo.set("No jobs available for this degree.")
                job_combo["values"] = []
                job_combo["state"] = "disabled"
                job_desc_text.config(state="normal")
                job_desc_text.delete("1.0", tk.END)
                job_desc_text.insert(tk.END, "No job descriptions available.")
                job_desc_text.config(state="disabled")
                logger.info(f"No jobs found for degree_id {degree_id}.")
        else:
            job_combo.set("")
            job_combo["values"] = []
            job_combo["state"] = "disabled"
            job_desc_text.config(state="normal")
            job_desc_text.delete("1.0", tk.END)
            job_desc_text.config(state="disabled")

    def on_job_select(event):
        selected_job = job_var.get()
        if selected_job and selected_job in job_id_map:
            display_job_description(selected_job)

    def display_job_description(job_name):
        """Displays the description of the selected job."""
        description = job_id_map.get(job_name, "No description available.")
        job_desc_text.config(state="normal")
        job_desc_text.delete("1.0", tk.END)
        job_desc_text.insert(tk.END, description)
        job_desc_text.config(state="disabled")
        logger.info(f"Displayed description for job: {job_name}")

    # Bind the functions to the dropdowns
    college_combo.bind("<<ComboboxSelected>>", on_college_select)
    department_combo.bind("<<ComboboxSelected>>", on_department_select)
    degree_level_combo.bind("<<ComboboxSelected>>", on_degree_level_select)
    degree_combo.bind("<<ComboboxSelected>>", on_degree_select_degree)
    job_combo.bind("<<ComboboxSelected>>", on_job_select)

    # Initialize Department Dropdown if existing preferences exist
    if existing_prefs.get("college_id"):
        college_name = get_college_name(existing_prefs["college_id"])
        if college_name in college_id_map:
            college_combo.set(college_name)
            on_college_select(None)

    # Save and Reset Buttons Frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20, anchor="e")

    def save_preferences():
        selected_college = college_var.get()
        selected_department = department_var.get()
        selected_degree_level = degree_level_var.get()
        selected_degree = degree_var.get()
        selected_job = job_var.get()

        preferences = {}
        if selected_college and selected_college != "Select your college":
            preferences["college_id"] = college_id_map.get(selected_college)
        if selected_department and selected_department != "Select your department":
            preferences["department_id"] = department_id_map.get(selected_department)
        if (
            selected_degree_level
            and selected_degree_level != "Select your degree level"
        ):
            preferences["degree_level_id"] = degree_level_id_map.get(
                selected_degree_level
            )
        if selected_degree and selected_degree != "Select your degree":
            preferences["degree_id"] = degree_id_map.get(selected_degree)
        if selected_job and selected_job != "Select your job":
            # Fetch job_id based on job_name using job_id_to_name_map
            # Reverse mapping: job_name to job_id
            job_id = None
            for jid, jname in job_id_to_name_map.items():
                if jname == selected_job:
                    job_id = jid
                    break
            if job_id:
                preferences["job_id"] = job_id

        logger.debug(f"Saving preferences: {preferences}")

        # Validations
        if not preferences.get("college_id"):
            messagebox.showerror(
                "Input Error", "Please select your affiliated college."
            )
            logger.warning("Preferences update failed: No college selected.")
            return
        if not preferences.get("department_id"):
            messagebox.showerror("Input Error", "Please select your department.")
            logger.warning("Preferences update failed: No department selected.")
            return
        if not preferences.get("degree_level_id"):
            messagebox.showerror("Input Error", "Please select your degree level.")
            logger.warning("Preferences update failed: No degree level selected.")
            return
        if not preferences.get("degree_id"):
            messagebox.showerror("Input Error", "Please select your degree.")
            logger.warning("Preferences update failed: No degree selected.")
            return
        if "job_id" not in preferences and db_operations.get_jobs_by_degree(
            preferences.get("degree_id")
        ):
            # If jobs are available but user hasn't selected one
            messagebox.showerror("Input Error", "Please select your preferred job.")
            logger.warning("Preferences update failed: No job selected.")
            return

        # Save preferences using db_operations
        success = db_operations.save_user_preferences(
            user_id=current_user["user_id"], preferences=preferences
        )

        if success:
            messagebox.showinfo("Success", "Preferences updated successfully!")
            logger.info("User preferences updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update preferences.")
            logger.error("User preferences update failed.")

    def reset_preferences():
        college_combo.set("Select your college")
        department_combo.set("")
        department_combo["values"] = []
        department_combo["state"] = "disabled"
        degree_level_combo.set("")
        degree_level_combo["values"] = []
        degree_level_combo["state"] = "disabled"
        degree_combo.set("")
        degree_combo["values"] = []
        degree_combo["state"] = "disabled"
        job_combo.set("")
        job_combo["values"] = []
        job_combo["state"] = "disabled"
        job_desc_text.config(state="normal")
        job_desc_text.delete("1.0", tk.END)
        job_desc_text.config(state="disabled")
        logger.debug("Preferences form reset by user.")

    save_btn = ttk.Button(
        button_frame, text="Save Preferences", command=save_preferences
    )
    save_btn.grid(row=0, column=0, padx=5)

    reset_btn = ttk.Button(
        button_frame, text="Reset Preferences", command=reset_preferences
    )
    reset_btn.grid(row=0, column=1, padx=5)


def get_current_user_preferences():
    """Fetches the current user's preferences from the database."""
    if not current_user:
        logger.error("No user is currently logged in.")
        messagebox.showerror("Error", "No user is currently logged in.")
        return None

    user_id = current_user.get("user_id")
    preferences = db_operations.get_user_preferences(user_id)
    if not preferences:
        logger.warning(f"No preferences found for user_id {user_id}.")
        messagebox.showwarning(
            "No Preferences", "You have not set any preferences yet."
        )
    return preferences


def show_recommendations(frame):
    """Displays AI-generated course recommendations in the content area."""
    if not login_status:
        messagebox.showerror(
            "Access Denied", "Please log in to access Recommendations."
        )
        logger.warning("Unauthorized access attempt to Recommendations page.")
        return  # Exit the function without displaying the page

    logger.info("Displaying Recommendations Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Course Recommendations", font=header_font)
    header_label.pack(pady=20)

    # Generate Recommendations Button
    generate_btn = ttk.Button(
        frame,
        text="Generate Recommendations",
        command=lambda: generate_recommendations_ui(frame),
    )
    generate_btn.pack(pady=10)

    # Recommendations Display Frame
    rec_frame = ttk.Frame(frame)
    rec_frame.pack(pady=10, fill="both", expand=True)

    # Optionally, fetch and display existing recommendations
    user_prefs = db_operations.get_user_preferences(current_user["user_id"])
    if user_prefs and user_prefs.get("job_id"):
        existing_recs = db_operations.get_recommendations(
            current_user["user_id"], user_prefs["job_id"]
        )
        if existing_recs:
            display_recommendations(rec_frame, existing_recs)
        else:
            logger.info("No existing recommendations to display.")
    else:
        logger.info("User preferences missing job_id. Please set preferences.")


# ui/gui.py


def generate_recommendations_ui(frame):
    """Generates and displays AI-driven course recommendations."""
    logger.info("Generating course recommendations.")

    rec_frame = frame.winfo_children()[-1]  # Get the last child, which is rec_frame
    clear_content(rec_frame)

    # Fetch user preferences
    user_prefs = get_current_user_preferences()
    if not user_prefs:
        logger.error("Cannot generate recommendations without user preferences.")
        messagebox.showerror(
            "Error", "Cannot generate recommendations without user preferences."
        )
        return

    # Extract job_id, job_name, degree_name from user_prefs
    job_id = user_prefs.get("job_id")
    degree_id = user_prefs.get("degree_id")

    if not job_id:
        logger.error("User preferences do not include a job_id.")
        messagebox.showerror("Error", "Please set your job preference in Preferences.")
        return

    if not degree_id:
        logger.error("User preferences do not include a degree_id.")
        messagebox.showerror(
            "Error", "Please set your degree preference in Preferences."
        )
        return

    # Retrieve job_name from job_id
    try:
        job = db_operations.get_job_by_id(job_id)
        if job:
            job_name = job["name"]
        else:
            logger.error(f"No job found with job_id {job_id}.")
            messagebox.showerror("Error", "Invalid job preference.")
            return
    except Exception as e:
        logger.error(f"Error retrieving job name for job_id {job_id}: {e}")
        messagebox.showerror("Error", "Failed to retrieve job information.")
        return

    # Retrieve degree_name from degree_id
    try:
        degree = db_operations.get_degree_by_id(degree_id)
        if degree:
            degree_name = degree["name"]
        else:
            logger.error(f"No degree found with degree_id {degree_id}.")
            messagebox.showerror("Error", "Invalid degree preference.")
            return
    except Exception as e:
        logger.error(f"Error retrieving degree name for degree_id {degree_id}: {e}")
        messagebox.showerror("Error", "Failed to retrieve degree information.")
        return

    # Fetch degree electives
    try:

        degree_electives = db_operations.get_degree_electives(degree_id)
        logger.debug(f"Fetched {len(degree_electives)} degree electives.")
    except Exception as e:
        logger.error(f"Error fetching degree electives: {e}")
        messagebox.showerror("Error", "Failed to fetch degree electives.")
        return

    # Invoke AI to get recommendations
    # The required format will be Prepare in the ai_integration/ai_module.py file
    try:
        recommendations_raw = get_recommendations_ai(
            job_id, job_name, degree_name, degree_electives
        )
        logger.debug("AI Recommendations Raw Response:")
        logger.debug(recommendations_raw)
    except Exception as e:
        messagebox.showerror(
            "AI Error", "Failed to generate recommendations. Please try again later."
        )
        logger.error(f"Failed to generate recommendations: {e}")
        return

    # Parse the AI response
    recommendations = parse_recommendations(recommendations_raw)
    if not recommendations:
        messagebox.showerror(
            "AI Error", "Failed to parse recommendations. Please try again."
        )
        logger.error("No recommendations parsed from AI response.")
        return

    # Display the recommendations
    display_recommendations_ui(rec_frame, recommendations)

    # Save recommendations to the database
    try:
        user_id = current_user["user_id"]  # Access user_id directly from current_user
        db_operations.clear_recommendations(user_id, job_id)
        save_recommendations_to_db(user_id, job_id, recommendations)
        # Debug: Log the recommendations to the logger
        # log_recommendations(user_id, job_id)

        logger.info("Recommendations generated and saved successfully.")
    except KeyError as ke:
        logger.error(f"Error saving recommendations to database: {ke}")
        messagebox.showerror("Error", f"Error saving recommendations to database: {ke}")
    except Exception as e:
        logger.error(f"Error saving recommendations to database: {e}")
        messagebox.showerror("Error", "Failed to save recommendations to database.")


def display_recommendations(frame, recommendations):
    """
    Displays the list of recommendations in the given frame with toggleable explanations.

    :param frame: ttk.Frame, The parent frame where recommendations will be displayed.
    :param recommendations: list of dicts, The course recommendations to display.
    """
    clear_content(frame)

    if not recommendations:
        messagebox.showinfo("No Recommendations", "No recommendations available.")
        return

    # Create a Canvas widget inside the frame
    canvas = tk.Canvas(frame, borderwidth=0, background="#f0f0f0")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, padding=(10, 10, 10, 10))

    # Configure the scrollable region
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Create a window inside the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar into the frame
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Iterate through each recommendation and display it
    for rec in recommendations:
        rec_container = ttk.Frame(
            scrollable_frame, relief="solid", borderwidth=1, padding=(10, 10)
        )
        rec_container.pack(padx=5, pady=5, fill="x", expand=True)

        # Course Name and Code
        course_label = ttk.Label(
            rec_container,
            text=f"{rec.get('Course Name', 'N/A')} ({rec.get('Course Code', 'N/A')})",
            font=("Helvetica", 12, "bold"),
            background="#ffffff",
        )
        course_label.pack(anchor="w", padx=5, pady=5)

        # Units
        units = rec.get("Units", "N/A")
        units_label = ttk.Label(
            rec_container, text=f"Units: {units}", background="#ffffff"
        )
        units_label.pack(anchor="w", padx=5)

        # Rating
        rating = rec.get("Rating", "N/A")
        rating_label = ttk.Label(
            rec_container, text=f"Rating: {rating}/100", background="#ffffff"
        )
        rating_label.pack(anchor="w", padx=5)

        # Prerequisites
        prereqs = rec.get("Prerequisites", "")
        prereq_text = prereqs if prereqs else "None"
        prereq_label = ttk.Label(
            rec_container, text=f"Prerequisites: {prereq_text}", background="#ffffff"
        )
        prereq_label.pack(anchor="w", padx=5, pady=5)

        # Toggle Button for Explanation
        toggle_btn = ttk.Button(rec_container, text="Show Explanation")
        toggle_btn.pack(anchor="w", padx=5, pady=5)

        # Explanation Label (Initially Hidden)
        explanation = rec.get("Explanation", "No explanation provided.")
        explanation_label = ttk.Label(
            rec_container,
            text=explanation,
            wraplength=800,
            justify="left",
            background="#e6e6e6",
            padding=(5, 5),
        )
        # Do not pack the explanation_label yet (hidden by default)

        def toggle_explanation(label=explanation_label, button=toggle_btn):
            """Toggle the visibility of the explanation label."""
            if label.winfo_ismapped():
                label.pack_forget()
                button.config(text="Show Explanation")
            else:
                label.pack(anchor="w", padx=5, pady=5)
                button.config(text="Hide Explanation")

        toggle_btn.config(command=toggle_explanation)

        # Optional: Button to view more details
        details_btn = ttk.Button(
            rec_container,
            text="View Details",
            command=lambda c=rec: show_course_details(frame, c),
        )
        details_btn.pack(anchor="e", padx=5, pady=5)


def save_recommendations_to_db(user_id, job_id, recommendations):
    """
    Saves the list of course recommendations to the Recommendations table.

    :param user_id: int, The ID of the user.
    :param job_id: int, The ID of the job associated with the recommendations.
    :param recommendations: list of dicts, The course recommendations.
    """

    """
    Process:
        Iterate through each recommendation.
        Extract course_code, rating, explanation, and rank.
        Fetch course_id using db_operations.get_course_by_code(course_code).
        Save the recommendation using db_operations.save_recommendation.
    """

    saved_count = 0  # Counter for successfully saved recommendations

    for rec in recommendations:
        # Access fields using indexing instead of .get()
        course_code = rec["Course Code"] if "Course Code" in rec else None
        rating = rec["Rating"] if "Rating" in rec else None
        explanation = (
            rec["Explanation"] if "Explanation" in rec else "No explanation provided."
        )
        rank = rec["Number"] if "Number" in rec else 0  # Assign default rank if missing

        # Validate required fields
        if not course_code:
            logger.warning("Recommendation missing 'Course Code'. Skipping.")
            continue
        if rating is None:
            logger.warning(
                f"Recommendation for {course_code} missing 'Rating'. Skipping."
            )
            continue

        # Fetch course_id from course_code
        course = db_operations.get_course_by_code(course_code)
        if not course:
            logger.warning(f"Course with code {course_code} not found in database.")
            continue  # Skip if course not found

        # Access course_id using indexing

        # Access course_id more reliably
        course_id = course["course_id"]
        if course_id is None:
            logger.warning(f"Course ID for course code {course_code} is missing.")
            continue  # Skip if course_id is missing

        # Handle rank if 'Number' is missing or invalid
        if not isinstance(rank, int):
            logger.warning(
                f"Recommendation for course {course_code} has invalid 'Number': {rank}. Assigning default rank."
            )
            rank = 0  # Assign default rank

        # Save the recommendation
        try:
            success = db_operations.save_recommendation(
                user_id=user_id,
                job_id=job_id,
                course_id=course_id,
                rating=rating,
                explanation=explanation,
                rank=rank,
            )
            if success:
                saved_count += 1
                logger.info(
                    f"Recommendation for course {course_code} saved successfully."
                )
            else:
                logger.error(f"Failed to save recommendation for course {course_code}.")
        except Exception as e:
            logger.error(f"Error saving recommendation for course {course_code}: {e}")

    logger.info(
        f"Total Recommendations Saved: {saved_count} out of {len(recommendations)}"
    )


def log_recommendations(user_id, job_id):
    """
    Retrieves and logs all recommendations for a specific user and job.

    :param user_id: int, The ID of the user.
    :param job_id: int, The ID of the job associated with the recommendations.
    """
    try:
        recommendations = db_operations.get_recommendations(user_id, job_id)
        if recommendations:
            logger.info(
                f"Logging {len(recommendations)} recommendations for user_id={user_id} and job_id={job_id}:"
            )
            for rec in recommendations:
                course_code = rec["Course Code"]
                course_name = rec["Course Name"]
                units = rec["Units"]
                rating = rec["Rating"]
                explanation = rec["Explanation"]
                prereqs = rec["Prerequisites"] if rec["Prerequisites"] else "None"
                rank = rec["rank"]

                logger.debug(
                    f"Recommendation {rank}: {course_name} ({course_code}) - Units: {units}, Rating: {rating}/100"
                )
                logger.debug(f"Explanation: {explanation}")
                logger.debug(f"Prerequisites: {prereqs}")
        else:
            logger.info(
                f"No recommendations found for user_id={user_id} and job_id={job_id}."
            )
    except Exception as e:
        logger.error(
            f"Error while logging recommendations for user_id={user_id} and job_id={job_id}: {e}"
        )


def parse_recommendations(raw_response):
    """
    Parses the raw AI response (JSON string) into a structured list of course recommendations.

    :param raw_response: str, The raw JSON response from the AI model.
    :return: list of dicts, Each dict contains course details.
    """
    recommendations = []
    try:
        # Parse the JSON string into a Python list
        data = json.loads(raw_response)
        logger.debug("Parsed JSON response successfully.")

        if isinstance(data, list):
            for course in data:
                # Optional: Validate required keys
                required_keys = [
                    "Course Code",
                    "Course Name",
                    "Rating",
                    "Prerequisites",
                    "Explanation",
                ]
                if all(key in course for key in required_keys):
                    recommendations.append(course)
                else:
                    logger.warning(f"Course data missing required keys: {course}")
        else:
            logger.error("AI response is not a list.")
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decoding failed: {jde}")
    except Exception as e:
        logger.error(f"Error parsing AI recommendations: {e}")
    return recommendations


def display_recommendations_ui(rec_frame, recommendations):
    """Displays the list of recommendations in the given frame with toggleable explanations."""
    clear_content(rec_frame)

    if not recommendations:
        messagebox.showinfo("No Recommendations", "No recommendations available.")
        return

    # Create a Canvas widget inside rec_frame
    canvas = tk.Canvas(rec_frame, borderwidth=0, background="#f0f0f0")
    scrollbar = ttk.Scrollbar(rec_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, padding=(10, 10, 10, 10))

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for rec in recommendations:
        rec_container = ttk.Frame(
            scrollable_frame, relief="solid", borderwidth=1, padding=(10, 10)
        )
        rec_container.pack(padx=5, pady=5, fill="x", expand=True)

        # Course Name and Code
        course_label = ttk.Label(
            rec_container,
            text=f"{rec.get('Course Name', 'N/A')} ({rec.get('Course Code', 'N/A')})",
            font=("Helvetica", 12, "bold"),
            background="#ffffff",
        )
        course_label.pack(anchor="w", padx=5, pady=5)

        # Units
        units = rec.get("Units", "N/A")
        units_label = ttk.Label(
            rec_container, text=f"Units: {units}", background="#ffffff"
        )
        units_label.pack(anchor="w", padx=5)

        # Rating
        rating = rec.get("Rating", "N/A")
        rating_label = ttk.Label(
            rec_container, text=f"Rating: {rating}/100", background="#ffffff"
        )
        rating_label.pack(anchor="w", padx=5)

        # Prerequisites
        prereqs = rec.get("Prerequisites", "")
        prereq_text = prereqs if prereqs else "None"
        prereq_label = ttk.Label(
            rec_container, text=f"Prerequisites: {prereq_text}", background="#ffffff"
        )
        prereq_label.pack(anchor="w", padx=5, pady=5)

        # Toggle Button for Explanation
        toggle_btn = ttk.Button(rec_container, text="Show Explanation")
        toggle_btn.pack(anchor="w", padx=5, pady=5)

        # Explanation Label (Initially Hidden)
        explanation = rec.get("Explanation", "No explanation provided.")
        explanation_label = ttk.Label(
            rec_container,
            text=explanation,
            wraplength=800,
            justify="left",
            background="#e6e6e6",
            padding=(5, 5),
        )
        # Do not pack the explanation_label yet (hidden by default)

        def toggle_explanation(label=explanation_label, button=toggle_btn):
            """Toggle the visibility of the explanation label."""
            if label.winfo_ismapped():
                label.pack_forget()
                button.config(text="Show Explanation")
            else:
                label.pack(anchor="w", padx=5, pady=5)
                button.config(text="Hide Explanation")

        toggle_btn.config(command=toggle_explanation)

        # Optional: Button to view more details
        details_btn = ttk.Button(
            rec_container,
            text="View Details",
            command=lambda c=rec: show_course_details(rec_container, c),
        )
        details_btn.pack(anchor="e", padx=5, pady=5)


def show_course_details(parent_frame, course):
    """Displays detailed information about a selected course in a popup window."""
    logger.info(f"Displaying details for course: {course.get('Course Name', 'N/A')}")

    # Create a new top-level window
    details_window = tk.Toplevel()
    details_window.title(f"Course Details - {course.get('Course Name', 'N/A')}")
    details_window.geometry("600x400")
    details_window.resizable(False, False)

    # Course Name and Code
    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(
        details_window,
        text=f"{course.get('Course Name', 'N/A')} ({course.get('Course Code', 'N/A')})",
        font=header_font,
    )
    header_label.pack(pady=10, padx=10, anchor="w")

    # Units
    units = course.get("Units", "N/A")
    units_label = ttk.Label(details_window, text=f"Units: {units}")
    units_label.pack(pady=5, padx=10, anchor="w")

    # Rating
    rating = course.get("Rating", "N/A")
    rating_label = ttk.Label(details_window, text=f"Rating: {rating}/100")
    rating_label.pack(pady=5, padx=10, anchor="w")

    # Prerequisites
    prereqs = course.get("Prerequisites", "")
    prereq_text = prereqs if prereqs else "None"
    prereq_label = ttk.Label(details_window, text=f"Prerequisites: {prereq_text}")
    prereq_label.pack(pady=5, padx=10, anchor="w")

    # Explanation
    explanation = course.get("Explanation", "No explanation provided.")
    explanation_label = ttk.Label(
        details_window,
        text=f"Explanation:\n{explanation}",
        wraplength=580,
        justify="left",
    )
    explanation_label.pack(pady=10, padx=10, anchor="w")

    # Action Buttons Frame
    action_frame = ttk.Frame(details_window)
    action_frame.pack(pady=20, padx=10, anchor="e")

    def save_course():
        try:
            # Implement save course functionality via db_operations
            # Example: db_operations.save_course(user_id, course_code)
            success = db_operations.save_course(
                current_user["user_id"], course.get("Course Code", "")
            )
            if success:
                messagebox.showinfo(
                    "Save Course",
                    f"Course '{course.get('Course Name', 'N/A')}' saved to your list.",
                )
                logger.info(
                    f"Course '{course.get('Course Name', 'N/A')}' saved by user."
                )
            else:
                messagebox.showerror(
                    "Save Course Failed",
                    f"Failed to save course '{course.get('Course Name', 'N/A')}'.",
                )
                logger.error(
                    f"Course '{course.get('Course Name', 'N/A')}' failed to save by user."
                )
        except Exception as e:
            messagebox.showerror(
                "Save Course Error",
                f"An unexpected error occurred while saving the course: {e}",
            )
            logger.error(
                f"Unexpected error while saving course '{course.get('Course Name', 'N/A')}': {e}"
            )

    def share_with_advisor():
        try:
            # Implement share with advisor functionality via db_operations
            # Example: db_operations.share_course_with_advisor(user_id, course_code)
            success = db_operations.share_course_with_advisor(
                current_user["user_id"], course.get("Course Code", "")
            )
            if success:
                messagebox.showinfo(
                    "Share with Advisor",
                    f"Course '{course.get('Course Name', 'N/A')}' shared with your advisor.",
                )
                logger.info(
                    f"Course '{course.get('Course Name', 'N/A')}' shared with advisor."
                )
            else:
                messagebox.showerror(
                    "Share Failed",
                    f"Failed to share course '{course.get('Course Name', 'N/A')}' with advisor.",
                )
                logger.error(
                    f"Course '{course.get('Course Name', 'N/A')}' failed to share with advisor."
                )
        except Exception as e:
            messagebox.showerror(
                "Share Error",
                f"An unexpected error occurred while sharing the course: {e}",
            )
            logger.error(
                f"Unexpected error while sharing course '{course.get('Course Name', 'N/A')}': {e}"
            )

    save_btn = ttk.Button(action_frame, text="Save Course", command=save_course)
    save_btn.grid(row=0, column=0, padx=5)

    share_btn = ttk.Button(
        action_frame, text="Share with Advisor", command=share_with_advisor
    )
    share_btn.grid(row=0, column=1, padx=5)

    back_btn = ttk.Button(
        action_frame, text="Back to Recommendations", command=details_window.destroy
    )
    back_btn.grid(row=0, column=2, padx=5)


def show_profile(frame):
    """Displays the User Profile and Account Settings in the content area."""
    if not login_status or not current_user:
        messagebox.showerror("Access Denied", "Please log in to access Profile.")
        logger.warning("Unauthorized access attempt to Profile page.")
        return  # Exit the function without displaying the page

    logger.info("Displaying Profile Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="User Profile", font=header_font)
    header_label.pack(pady=20)

    # Profile Information Frame
    profile_frame = ttk.Frame(frame)
    profile_frame.pack(pady=10)

    user_info = {
        "Full Name": current_user["full_name"],
        "Email": current_user["email"],
        "Student ID": current_user["student_id"],
        "GPA": current_user["gpa"],
    }

    for idx, (key, value) in enumerate(user_info.items()):
        label = ttk.Label(profile_frame, text=f"{key}:")
        label.grid(row=idx, column=0, padx=5, pady=5, sticky="e")
        value_label = ttk.Label(profile_frame, text=value)
        value_label.grid(row=idx, column=1, padx=5, pady=5, sticky="w")

    # Account Settings Frame
    settings_frame = ttk.LabelFrame(frame, text="Account Settings")
    settings_frame.pack(pady=20, fill="x", padx=20)

    # Change Password Button
    def change_password():
        logger.info("User initiated password change.")
        # Implement password change functionality via db_operations
        # For demonstration, we'll create a simple password change dialog

        def perform_password_change():
            old_pwd = old_pwd_entry.get()
            new_pwd = new_pwd_entry.get()
            confirm_new_pwd = confirm_new_pwd_entry.get()

            if not old_pwd or not new_pwd or not confirm_new_pwd:
                messagebox.showerror("Input Error", "All fields are required.")
                logger.warning("Password change failed: Incomplete fields.")
                return
            if new_pwd != confirm_new_pwd:
                messagebox.showerror("Input Error", "New passwords do not match.")
                logger.warning("Password change failed: Passwords do not match.")
                return
            if (
                len(new_pwd) < 8
                or not any(char.isdigit() for char in new_pwd)
                or not any(
                    char in r"!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for char in new_pwd
                )
            ):
                messagebox.showerror(
                    "Input Error",
                    "Password must be at least 8 characters long and include numbers and special characters.",
                )
                logger.warning("Password change failed: Weak password.")
                return

            # Attempt to change password using db_operations
            success = db_operations.change_password(
                current_user["user_id"], old_pwd, new_pwd
            )
            if success:
                messagebox.showinfo("Success", "Password changed successfully!")
                logger.info(
                    f"User '{current_user['email']}' changed password successfully."
                )
                password_change_window.destroy()
            else:
                messagebox.showerror(
                    "Error", "Failed to change password. Check your current password."
                )
                logger.error(
                    f"Password change failed for user '{current_user['email']}'."
                )

        password_change_window = tk.Toplevel()
        password_change_window.title("Change Password")
        password_change_window.geometry("400x250")
        password_change_window.resizable(False, False)

        # Old Password
        old_pwd_label = ttk.Label(password_change_window, text="Current Password:")
        old_pwd_label.pack(pady=10, padx=10, anchor="w")
        old_pwd_entry = ttk.Entry(password_change_window, width=30, show="*")
        old_pwd_entry.pack(pady=5, padx=10, anchor="w")

        # New Password
        new_pwd_label = ttk.Label(password_change_window, text="New Password:")
        new_pwd_label.pack(pady=10, padx=10, anchor="w")
        new_pwd_entry = ttk.Entry(password_change_window, width=30, show="*")
        new_pwd_entry.pack(pady=5, padx=10, anchor="w")

        # Confirm New Password
        confirm_new_pwd_label = ttk.Label(
            password_change_window, text="Confirm New Password:"
        )
        confirm_new_pwd_label.pack(pady=10, padx=10, anchor="w")
        confirm_new_pwd_entry = ttk.Entry(password_change_window, width=30, show="*")
        confirm_new_pwd_entry.pack(pady=5, padx=10, anchor="w")

        # Change Password Button
        change_pwd_button = ttk.Button(
            password_change_window,
            text="Change Password",
            command=perform_password_change,
        )
        change_pwd_button.pack(pady=20)

    change_pwd_btn = ttk.Button(
        settings_frame, text="Change Password", command=change_password
    )
    change_pwd_btn.pack(pady=10, padx=10, anchor="w")

    # Manage Notifications (Placeholder)
    def manage_notifications():
        logger.info("User accessed notification settings.")
        # Implement notification settings functionality via db_operations
        messagebox.showinfo(
            "Manage Notifications",
            "Notification settings functionality is not yet implemented.",
        )

    notif_btn = ttk.Button(
        settings_frame, text="Manage Notifications", command=manage_notifications
    )
    notif_btn.pack(pady=10, padx=10, anchor="w")


def show_help(frame):
    """Displays the Help and Support page in the content area."""
    logger.info("Displaying Help Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Help & Support", font=header_font)
    header_label.pack(pady=20)

    # Help Content Frame
    help_frame = ttk.Frame(frame)
    help_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Placeholder Help Information
    help_text = (
        "Welcome to the Smart Elective Advisor Help Center!\n\n"
        "If you need assistance navigating the application or have any questions, please refer to the following resources:\n\n"
        "1. **User Guides:** Comprehensive manuals to help you understand and utilize all features of the application.\n"
        "2. **FAQs:** Answers to the most commonly asked questions by users.\n"
        "3. **Contact Support:** If you encounter any issues or need personalized assistance, please contact our support team at support@university.edu.\n\n"
        "We are here to help you make informed and strategic decisions for your academic journey!"
    )
    help_label = ttk.Label(help_frame, text=help_text, wraplength=800, justify="left")
    help_label.pack(pady=10)

    # Search Help Topics (Placeholder)
    search_label = ttk.Label(help_frame, text="Search Help Topics:")
    search_label.pack(pady=5, anchor="w")
    search_entry = ttk.Entry(help_frame, width=50)
    search_entry.pack(pady=5, anchor="w")

    def search_help():
        query = search_entry.get()
        logger.info(f"User searched for help topic: {query}")
        # Implement search functionality, possibly via db_operations or AI integration
        messagebox.showinfo(
            "Search Help", f"Search functionality for '{query}' is not yet implemented."
        )

    search_btn = ttk.Button(help_frame, text="Search", command=search_help)
    search_btn.pack(pady=5, anchor="w")


def show_help(frame):
    """Displays the Help and Support page in the content area."""
    logger.info("Displaying Help Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Help & Support", font=header_font)
    header_label.pack(pady=20)

    # Help Content Frame
    help_frame = ttk.Frame(frame)
    help_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Placeholder Help Information
    help_text = (
        "Welcome to the Smart Elective Advisor Help Center!\n\n"
        "If you need assistance navigating the application or have any questions, please refer to the following resources:\n\n"
        "1. **User Guides:** Comprehensive manuals to help you understand and utilize all features of the application.\n"
        "2. **FAQs:** Answers to the most commonly asked questions by users.\n"
        "3. **Contact Support:** If you encounter any issues or need personalized assistance, please contact our support team at support@university.edu.\n\n"
        "We are here to help you make informed and strategic decisions for your academic journey!"
    )
    help_label = ttk.Label(help_frame, text=help_text, wraplength=800, justify="left")
    help_label.pack(pady=10)

    # Search Help Topics (Placeholder)
    search_label = ttk.Label(help_frame, text="Search Help Topics:")
    search_label.pack(pady=5, anchor="w")
    search_entry = ttk.Entry(help_frame, width=50)
    search_entry.pack(pady=5, anchor="w")

    def search_help():
        query = search_entry.get()
        logger.info(f"User searched for help topic: {query}")
        # Implement search functionality, possibly via db_operations or AI integration
        messagebox.showinfo(
            "Search Help", f"Search functionality for '{query}' is not yet implemented."
        )

    search_btn = ttk.Button(help_frame, text="Search", command=search_help)
    search_btn.pack(pady=5, anchor="w")


def show_help(frame):
    """Displays the Help and Support page in the content area."""
    logger.info("Displaying Help Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Help & Support", font=header_font)
    header_label.pack(pady=20)

    # Help Content Frame
    help_frame = ttk.Frame(frame)
    help_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Placeholder Help Information
    help_text = (
        "Welcome to the Smart Elective Advisor Help Center!\n\n"
        "If you need assistance navigating the application or have any questions, please refer to the following resources:\n\n"
        "1. **User Guides:** Comprehensive manuals to help you understand and utilize all features of the application.\n"
        "2. **FAQs:** Answers to the most commonly asked questions by users.\n"
        "3. **Contact Support:** If you encounter any issues or need personalized assistance, please contact our support team at support@university.edu.\n\n"
        "We are here to help you make informed and strategic decisions for your academic journey!"
    )
    help_label = ttk.Label(help_frame, text=help_text, wraplength=800, justify="left")
    help_label.pack(pady=10)

    # Search Help Topics (Placeholder)
    search_label = ttk.Label(help_frame, text="Search Help Topics:")
    search_label.pack(pady=5, anchor="w")
    search_entry = ttk.Entry(help_frame, width=50)
    search_entry.pack(pady=5, anchor="w")

    def search_help():
        query = search_entry.get()
        logger.info(f"User searched for help topic: {query}")
        # Implement search functionality, possibly via db_operations or AI integration
        messagebox.showinfo(
            "Search Help", f"Search functionality for '{query}' is not yet implemented."
        )

    search_btn = ttk.Button(help_frame, text="Search", command=search_help)
    search_btn.pack(pady=5, anchor="w")


def show_help(frame):
    """Displays the Help and Support page in the content area."""
    logger.info("Displaying Help Page.")
    clear_content(frame)

    header_font = ("Helvetica", 14, "bold")
    header_label = ttk.Label(frame, text="Help & Support", font=header_font)
    header_label.pack(pady=20)

    # Help Content Frame
    help_frame = ttk.Frame(frame)
    help_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Placeholder Help Information
    help_text = (
        "Welcome to the Smart Elective Advisor Help Center!\n\n"
        "If you need assistance navigating the application or have any questions, please refer to the following resources:\n\n"
        "1. **User Guides:** Comprehensive manuals to help you understand and utilize all features of the application.\n"
        "2. **FAQs:** Answers to the most commonly asked questions by users.\n"
        "3. **Contact Support:** If you encounter any issues or need personalized assistance, please contact our support team at support@university.edu.\n\n"
        "We are here to help you make informed and strategic decisions for your academic journey!"
    )
    help_label = ttk.Label(help_frame, text=help_text, wraplength=800, justify="left")
    help_label.pack(pady=10)

    # Search Help Topics (Placeholder)
    search_label = ttk.Label(help_frame, text="Search Help Topics:")
    search_label.pack(pady=5, anchor="w")
    search_entry = ttk.Entry(help_frame, width=50)
    search_entry.pack(pady=5, anchor="w")

    def search_help():
        query = search_entry.get()
        logger.info(f"User searched for help topic: {query}")
        # Implement search functionality, possibly via db_operations or AI integration
        messagebox.showinfo(
            "Search Help", f"Search functionality for '{query}' is not yet implemented."
        )

    search_btn = ttk.Button(help_frame, text="Search", command=search_help)
    search_btn.pack(pady=5, anchor="w")
