import matplotlib.pyplot as plt
from .baseline_model import baseline_model
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go


def nice_plotting():
    
     # Importing prediction data
    df = baseline_model()

    # Create the plot
    fig = px.line(df, x='ds', y='yhat', template='plotly_dark')

    # Add the confidence interval
    fig.add_trace(
        go.Scatter(
            x=df['ds'].tolist() + df['ds'].tolist()[::-1],
            y=df['yhat_upper'].tolist() + df['yhat_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='gray',
            line=dict(color='gray'),
            hoverinfo = 'skip',
            showlegend=True,
            name = 'Confidence Interval'
        )
    )

    # Add the predicted revenue line
    fig.add_trace(go.Scatter(x=df['ds'], y=df['yhat'], mode='lines', name='Predicted'))

    # Add the actual revenue line
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y_true'], mode='lines', name='Actual'))

    # Add the red dot as a scatter plot
    fig.add_trace(go.Scatter(x=[df['ds'][0]], y=[df['yhat'][0]], mode='markers', marker=dict(size=14, color='red'), name='Prediction Tracker'))

    # Add the annotations with the predicted revenue values
    annotations = []
    for i in range(len(df)):
        annotations.append(dict(x=df['ds'][i], y=df['yhat'][i], text=f"{df['yhat'][i]:.2f}", showarrow=True, arrowhead=1, ax=0, ay=-20))
    fig.update_layout(annotations=annotations)

    # Set the axis range and labels
    fig.update_layout(xaxis=dict(title='Date'), yaxis=dict(title='Revenue', range=[0, df['yhat_upper'].max()]))

    # Add the play button
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                buttons=[dict(label='Play',
                            method='animate',
                            args=[None, {"frame": {"duration": 1200},
                                        "fromcurrent": True, "transition": {"duration": 0}}]
                            )
                    ]
            )
        ]
    )

    # Create the frames for the animation
    frames = [dict(data=[dict(type='scatter',
                            x=df['ds'][:i+1],
                            y=df['yhat'][:i+1],
                            mode='lines'
                            ),
                        dict(type='scatter',
                            x=[df['ds'][i]],
                            y=[df['yhat'][i]],
                            mode='markers',
                            marker=dict(size=14, color='red')
                            )
                        ]) for i in range(len(df))]

    # Add the frames to the animation
    fig.frames = frames

    # Show the plot
    fig.show()


def plotting():

    # Importing prediction data
    df = baseline_model()

    # Set the figure size
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the predicted revenue values
    ax.plot(df['ds'], df['yhat'], color='blue', label='Predicted')

    # Fill in the shaded regions for the confidence intervals
    ax.fill_between(df['ds'], df['yhat_lower'], df['yhat_upper'], color='gray', alpha=0.3, label='Confidence Interval')

    # Plot the actual revenue values
    ax.plot(df['ds'], df['y_true'], color='green', label='Actual')

    # Add a legend and axis labels
    ax.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel('Revenue')

    # Show the plot
    return plt.show()
