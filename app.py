from flask import Flask, render_template, request, redirect, url_for
import re
import csv, requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Sample profile data (replace with your own data)
profile_data = {
    'name': 'Guneet Singh',
    'email': 'guneetsinghbali@gmail.com',
    'bio': 'Senior Test Engineer | Mentor @Topmate | QA Career Advisor',
    'image': 'images/img.jpeg',
    'linkedin': 'https://www.linkedin.com/in/guneetsinghbali/',
    'topmate': 'https://topmate.io/guneet_singh_07'
    # Add more profile data as needed
}

# GitHub API endpoint for public repositories
GITHUB_API_URL = 'https://api.github.com/repositories'

# GitHub Personal Access Token (replace 'YOUR_ACCESS_TOKEN' with your actual token)
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
print(GITHUB_ACCESS_TOKEN)

# Function to check if user exists in users.txt file
def is_valid_user(username, password):
    with open('users.txt', 'r') as file:
        for line in file:
            user, pwd = line.strip().split(':')
            if user == username and pwd == password:
                return True
    return False


# Function to validate password strength
def is_strong_password(password):
    # Minimum length of 8 characters
    if len(password) < 8:
        return False
    # At least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    # At least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    # At least one digit
    if not re.search(r'\d', password):
        return False
    return True

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        try:
        # Write data to CSV file
            with open('contacts.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, email, message])

            return render_template('contact.html',success='Your message has been successfully submitted. We will get back to you shortly.')
        except Exception as e:
            return "Error: Missing form field - " + str(e), 400
    return render_template('contact.html')    

@app.route('/about')
def about():
    return render_template('about.html',profile=profile_data)    

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Validate if username and password are correct
    if is_valid_user(username, password):
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='Invalid username or password.')

@app.route('/home')
def home():
    page = int(request.args.get('page', 1))
    params = {
        'q': 'stars:>2',  # Query to search for repositories with more than 2 stars
        'per_page': 10,   # Number of repositories per page
        'page': page, 
        'sort': 'stars',  # Sort by stars
        'order': 'desc'   # Sort in descending order (highest stars first)
    }
    # Fetch open source projects from GitHub API
    headers = {'Authorization': f'token {GITHUB_ACCESS_TOKEN}'}
    response = requests.get(GITHUB_API_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        projects = data
        # print(projects)
        # total_count = data.get('total_count', 0)
        total_pages = calculate_total_pages(100, params['per_page'])
        return render_template('home.html', projects=projects, current_page=page, total_pages=total_pages)
    else:
        return 'Error fetching GitHub projects', 500

def calculate_total_pages(total_count, per_page):
    return (total_count + per_page - 1) // per_page


def filter_automation_projects(projects):
    automation_keywords = ['automation', 'automated', 'testing', 'CI/CD', 'Selenium', 'WebDriver', 'TestNG', 'JUnit']  # Keywords related to automation
    automation_projects = []
    for project in projects:
        description = project.get('description')
        if description and any(keyword.lower() in description.lower() for keyword in automation_keywords):
            automation_projects.append(project)
    return automation_projects       

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        # Check if password is strong
        if not is_strong_password(password):
            return render_template('register.html', error='Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.')

        # Save user data to a text file
        with open('users.txt', 'a') as file:
            file.write(f'{username}:{password}\n')

        # Render the register template with a success message
        return render_template('register.html', success='Registration successful. Please login.')

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
