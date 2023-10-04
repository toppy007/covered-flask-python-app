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

**Area of Inprovement:**

1. **Error Handling for Input in Profile Section:**
- Implement robust error handling to prevent program crashes when inputs are not available in the profile section.
- Provide informative error messages to guide users on correcting input issues.

2. **Enhanced Analytical Tools:**
- Integrate additional analytical tools to offer more insights and data analysis capabilities within the program.
- Consider incorporating data visualization tools to make the analysis more user-friendly.

3. **Optimization of Comparisons:**
- Optimize the algorithm for comparing job adverts and user profiles, enhancing the efficiency and accuracy of the matching process.
- Consider incorporating machine learning techniques for more sophisticated profile matching.

3. **Settings Customization:**
- Include settings functionality that allows users to customize OpenAI settings based on their preferences.
- Provide clear documentation or tooltips to guide users through adjusting settings.

4. **Editable Results:**
- Enable users to edit and refine the results of the job matching process.
- Implement a user-friendly interface for modifying and updating profile information after the initial analysis.

5. **Expanded Job Application History:**
- Add more detailed options in the job application history section to track the entire application process.
- Include status updates, interview dates, and any communication details for a comprehensive overview

6. **Add Encryption to the OpenAI DB Entry:**
- PostgreSQL built-in encryption features