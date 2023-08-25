# COVERED

This Flask-based web application, primarily consisting of a Blueprint named `views`, offers a platform for users to interact with and generate tailored job application content. The application leverages user profiles, notes, skills, and projects. Here's a summary of the key functionalities and the tech stack used:

**Functionalities:**
1. **Home Page:** The home page is a simple view that renders the "home.html" template, displaying basic user information.

2. **Profile Page:** Users can access their profiles via this route. They can add notes, skills, API keys, and project details through various forms. These entries are stored in the database for the respective user.

3. **Generate Page:** Users are required to have an OpenAI API key linked to their profile. On this page, users can provide a job advertisement and additional information. The application then generates a set of prompts based on the job advertisement and the user's skills. These prompts are sent to the OpenAI API for analysis.

4. **Results Page:** This page displays the results of the analysis performed on the job advertisement. It shows the matching skills, user's qualifications, and other insights based on the analysis.

5. **Deletion Routes:** There are routes for deleting notes, skills, API keys, and projects. These are invoked via AJAX calls to update the database.

**Tech Stack:**
- **Flask:** The application is built using the Flask web framework, which enables route handling, template rendering, and more.
- **Flask-Login:** This extension manages user sessions and authentication.
- **SQLAlchemy:** It provides an Object-Relational Mapping (ORM) layer for database interactions. The application uses this to define and manage database models.
- **Werkzeug:** Used for password hashing and security utilities.
- **OpenAI API:** The application communicates with the OpenAI API to generate prompts and analyze job advertisements.
- **Fuzzywuzzy:** A library used to perform string matching and similarity calculations, which is useful for comparing skills against job requirements.
- **JavaScript (AJAX):** AJAX is used for asynchronous interactions, such as deleting notes, skills, API keys, and projects without refreshing the page.
- **HTML/CSS:** These are used for structuring the user interface and styling the templates.
- **Jinja2:** The template engine for rendering dynamic content in HTML templates.
- **SQLite:** The default database engine used by SQLAlchemy to store user data, notes, skills, etc.
- **Python 3:** The primary programming language for building the backend logic.

The application focuses on allowing users to manage their profiles, notes, skills, and projects. It also facilitates the generation of tailored job application content by analyzing job advertisements and matching them with the user's skills. This provides insights to help users better understand their suitability for specific roles.
