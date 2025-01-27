import dash
from dash import html, dcc
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from db import get_db_connection
import pandas as pd
from datetime import datetime, timedelta
import pymysql

dash.register_page(__name__, path="/stats")

def get_claims_data():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Fetch all relevant data
    cursor.execute("""
        SELECT 
            claim_number,
            Policyholder,
            Date_Of_Loss,
            Insurer,
            coverage_building,
            coverage_contents,
            DwellingUnit_Insured_Damage_RCV_Loss,
            DetachedGarage_Insured_Damage_RCV_Loss,
            Improvements_Insured_Damage_RCV_Loss,
            Contents_Insured_Damage_RCV_Loss,
            Review_Status,
            created_at
        FROM claims
    """)
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(data)
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

def layout():
    df = get_claims_data()
    
    # Calculate key metrics
    total_claims = len(df)
    claims_this_month = len(df[df['created_at'] >= (datetime.now() - timedelta(days=30))])
    avg_building_coverage = pd.to_numeric(df['coverage_building'].str.replace('$', '').str.replace(',', ''), errors='coerce').mean()
    
    # Create status distribution pie chart
    status_dist = df['Review_Status'].value_counts()
    status_fig = px.pie(
        values=status_dist.values,
        names=status_dist.index,
        title='Claims by Review Status'
    )

    # Create claims over time line chart
    claims_over_time = df.groupby(df['created_at'].dt.date).size().reset_index()
    claims_over_time.columns = ['date', 'count']  # Name the columns
    timeline_fig = px.line(
        claims_over_time,
        x='date',
        y='count',
        title='Claims Over Time'
    )

    # Create insurers bar chart
    insurer_dist = df['Insurer'].value_counts()
    insurer_fig = px.bar(
        x=insurer_dist.index,
        y=insurer_dist.values,
        title='Claims by Insurer'
    )

    return dmc.Stack([
        # Header
        dmc.Title("Claims Statistics Dashboard", order=1),
        
        # Key Metrics Cards
        dmc.SimpleGrid(
            cols=4,
            spacing="lg",
            children=[
                dmc.Card([
                    dmc.Text("Total Claims", size="lg", fw=500),
                    dmc.Text(str(total_claims), size="xl", fw=700)
                ]),
                dmc.Card([
                    dmc.Text("Claims This Month", size="lg", fw=500),
                    dmc.Text(str(claims_this_month), size="xl", fw=700)
                ]),
                dmc.Card([
                    dmc.Text("Avg Building Coverage", size="lg", fw=500),
                    dmc.Text(f"${avg_building_coverage:,.2f}", size="xl", fw=700)
                ]),
                dmc.Card([
                    dmc.Text("Review Completion", size="lg", fw=500),
                    dmc.Text(
                        f"{(len(df[df['Review_Status'] == 'Reviewed']) / total_claims * 100):.1f}%",
                        size="xl",
                        fw=700
                    )
                ]),
            ]
        ),
        
        # Charts Grid
        dmc.SimpleGrid(
            cols=2,
            spacing="lg",
            children=[
                dmc.Card(dcc.Graph(figure=status_fig)),
                dmc.Card(dcc.Graph(figure=timeline_fig)),
                dmc.Card(dcc.Graph(figure=insurer_fig)),
                dmc.Card(
                    dmc.Stack([
                        dmc.Text("Recent Activity", size="lg", fw=500),
                        dmc.Table(
                            withBorder=True,
                            highlightOnHover=True,
                            striped=True,
                            children=[
                                html.Thead(
                                    html.Tr([
                                        html.Th("Claim #"),
                                        html.Th("Policyholder"),
                                        html.Th("Status")
                                    ])
                                ),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(row['claim_number']),
                                        html.Td(row['Policyholder']),
                                        html.Td(row['Review_Status'])
                                    ]) for _, row in df.sort_values('created_at', ascending=False).head(5).iterrows()
                                ])
                            ]
                        )
                    ])
                ),
            ]
        ),
    ])
