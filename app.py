

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Cargar los datos del archivo CSV
file_path = "election_data.csv" # Cambia el nombre si el archivo tiene otro nombre en tu sistema
df = pd.read_csv(file_path)

# Mapeo de nombres completos de estados a sus códigos abreviados
state_abbr = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Asegurarnos de que los nombres de estados coincidan con los códigos estándar
df["state"] = df["state"].map(state_abbr)

# Crear la aplicación Dash
app = Dash(__name__)

# Crear un mapa interactivo
fig_map = px.choropleth(
    df.groupby("state", as_index=False).sum(),
    locations="state",
    locationmode="USA-states",
    color="votes",
    scope="usa",
    title="Total de votos por estado",
    labels={"votes": "Votos"}
)

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard Electoral de Estados Unidos"),
    dcc.Graph(id="map", figure=fig_map),
    html.Div(id="state_details", style={"margin-top": "20px"}),
    dcc.Graph(id="bar_chart", style={"display": "none"}),  # Ocultar por defecto
    dcc.Graph(id="party_pie_chart", style={"display": "none"})  # Ocultar por defecto
])

# Callback para actualizar la información y gráficos
@app.callback(
    [Output("state_details", "children"),
     Output("bar_chart", "figure"),
     Output("bar_chart", "style"),
     Output("party_pie_chart", "figure"),
     Output("party_pie_chart", "style")],
    [Input("map", "clickData")]
)
def update_dashboard(clickData):
    if clickData is None:
        return "Selecciona un estado en el mapa para ver la información.", {}, {"display": "none"}, {}, {"display": "none"}

    # Obtener el estado seleccionado
    state = clickData["points"][0]["location"]
    filtered_data = df[df["state"] == state]

    # Si no hay datos para el estado seleccionado
    if filtered_data.empty:
        return (
            html.Div(f"No hay datos disponibles para el estado {state}."),
            {}, {"display": "none"},
            {}, {"display": "none"}
        )

    # Calcular el candidato ganador
    top_candidate = (
        filtered_data.groupby(["candidate", "party"], as_index=False).sum()
        .sort_values(by="votes", ascending=False)
        .iloc[0]
    )
    candidate_name = top_candidate["candidate"]
    candidate_party = top_candidate["party"]
    candidate_votes = top_candidate["votes"]

    # Detalles del estado seleccionado
    total_votes = filtered_data["votes"].sum()
    details = html.Div([
        html.H3(f"Estado seleccionado: {state}"),
        html.P(f"Total de votos: {total_votes:,}"),
        html.P(f"Candidato ganador: {candidate_name} ({candidate_party})"),
        html.P(f"Votos del candidato ganador: {candidate_votes:,}")
    ])

    # Gráfico de barras: votos por candidato
    bar_chart = px.bar(
        filtered_data.groupby("candidate", as_index=False).sum(),
        x="candidate",
        y="votes",
        color="party",
        title=f"Votos por candidato en {state}"
    )

    # Gráfico de pastel: distribución de votos por partido
    party_pie_chart = px.pie(
        filtered_data.groupby("party", as_index=False).sum(),
        names="party",
        values="votes",
        title=f"Distribución de votos por partido en {state}"
    )

    # Mostrar gráficos cuando hay selección
    return details, bar_chart, {"display": "block"}, party_pie_chart, {"display": "block"}

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
