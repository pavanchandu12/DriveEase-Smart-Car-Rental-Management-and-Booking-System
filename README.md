Car Rental Management System
This project is a Flask-based web application that manages car rentals, customer reservations, car returns, and rental reports.
It uses a MySQL database (car_rental) for backend data storage and provides a multi-role interface for customers, car owners, and administrators.

🚀 Features
✅ Register individual or company customers
✅ Add new cars and associate them with owners
✅ Manage car availability and rental periods
✅ Make reservations and calculate rental charges (daily/weekly)
✅ Update car rental rates for different car types
✅ Handle car returns and update availability
✅ Generate earnings reports for vehicle owners

🏗️ Tech Stack
Backend: Python Flask

Frontend: HTML templates (Jinja2), CSS (inside /static)

Database: MySQL (via PyMySQL)

Others: Math, datetime, file handling

📂 Project Structure

/car-rental-app
├── app.py                  # Main Flask app
├── templates/              # HTML templates
├── static/                 # Static CSS/JS/images
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
⚙️ Setup Instructions
1️⃣ Clone the repository


git clone https://github.com/your-username/car-rental-app.git
cd car-rental-app
2️⃣ Set up virtual environment (optional but recommended)


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3️⃣ Install required Python packages


pip install -r requirements.txt
4️⃣ Set up MySQL Database

Create a database named car_rental.

Import the required tables (customer, car, cartype, vehicle_owner, rents, availability) into MySQL.

Update the database connection in app.py if needed:


hostname = 'localhost'
username = 'root'
password = 'YourPassword'
database = 'car_rental'
5️⃣ Run the Flask app


python app.py
6️⃣ Access the app in your browser


http://localhost:5000/
📝 Main Routes
Route	Description
/	Main dashboard
/upload	Navigate between modules
/selectcustomer	Choose between Individual or Company customer
/Individual	Insert Individual customer
/CompanyInsertion	Insert Company customer
/Car	Add a new car
/reservation	Show available cars for reservation
/booking	Book a car
/Carreturn	Process car return
/deletereservation	Delete/complete reservation
/UpdateRental	Update rental rates

