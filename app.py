import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import mysql.connector
import pandas as pd

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Use environment variables or a secure method to manage these credentials
db_config = {
    'user': 'doadmin',
    'password': 'AVNS_PKmLcExYHHwoMSYhxhi',
    'host': 'pddata-do-user-15980530-0.c.db.ondigitalocean.com',
    'database': 'defaultdb',
    # Ensure you add your SSL parameters here if required
}
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.Error as e:
        print(e)
    return conn

# Function to create a table
def create_doctors_table():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) NOT NULL
    );
    """
    try:
        cursor.execute(create_table_query)
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Call the function to create the table
create_doctors_table()


def fetch_doctors():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def add_doctor(name, specialization):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO doctors (id, name,email,phone_number) VALUES (%s, %s,%s,%s, %s)", (id, name,email,phone_number))
    conn.commit()
    cursor.close()
    conn.close()

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P("A simple sidebar layout with navigation links", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Doctors", href="/"),
                dbc.NavLink("Patients", href="/page-1"),
                dbc.NavLink("Account", href="/page-2"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        doctors = fetch_doctors()
        table_header = [html.Thead(html.Tr([html.Th("ID"), html.Th("name"), html.Th("email"), html.Th("phone_number")]))]
        table_body = [html.Tbody([html.Tr([html.Td(doctor['id']), html.Td(doctor['name']), html.Td(doctor['email']), html.Td(doctor['phone_number']), html.Td(doctor['email'])]) for doctor in doctors])]
        table = dbc.Table(table_header + table_body, bordered=True, dark=True, hover=True, responsive=True, striped=True)
        form = dbc.Form(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Name", html_for="name-input"),
                        dbc.Input(id="name-input", type="text", placeholder="Enter name"),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("email", html_for="email-input"),
                        dbc.Input(id="email-input", type="text", placeholder="Enter email"),
                    ]
                ),
                  dbc.FormGroup(
                    [
                        dbc.Label("phone_number", html_for="phone_number-input"),
                        dbc.Input(id="phone_number-input", type="text", placeholder="Enter phone_number"),
                    ]
                ),
                dbc.Button("Add Doctor", id="add-btn", className="mr-2", color="primary", n_clicks=0),
            ]
        )
        return html.Div([table, html.Hr(), form])
    elif pathname == "/page-1":
        return html.P("This is the content of page 1.")
    elif pathname == "/page-2":
        return html.P("This is the content of page 2.")
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback(
    Output("url", "pathname"),
    [Input("add-btn", "n_clicks")],
    [State("name-input", "value"), State("spec-input", "value")],
    prevent_initial_call=True
)
def add_new_doctor(n_clicks, name, specialization):
    if n_clicks > 0 and name and specialization:
        add_doctor(name, specialization)
        return "/"  # Redirect to the home page to show the updated list
    return dash.no_update

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
