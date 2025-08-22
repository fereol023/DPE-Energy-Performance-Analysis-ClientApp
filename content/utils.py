import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from scipy import stats

def plot_quantitative_with_dpe_hue_plotly(df, col_name, col_name_alias, hue_col_alias, hue_col=None,
                                          colormap='RdYlGn_r', plot_type='histogram', 
                                          height=600, width=1000, opacity=0.7):
    """
    Plots the distribution of a quantitative variable with optional hue using Plotly.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        col_name (str): The name of the quantitative column to plot.
        hue_col (str, optional): The column to use for hue. If None, plots without hue. 
                                Defaults to None.
        colormap (str, optional): The colormap to use for the hue. Defaults to 'RdYlGn_r'.
        plot_type (str, optional): Type of plot - 'histogram', 'box', 'violin', or 'density'. 
                                  Defaults to 'histogram'.
        height (int): Height of the plot in pixels. Defaults to 600.
        width (int): Width of the plot in pixels. Defaults to 1000.
        opacity (float): Opacity of the plot elements. Defaults to 0.7.
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object.
    """
    
    # Define DPE color mapping (RdYlGn_r: green=good/A, red=bad/G)
    dpe_color_map = {
        'A': '#1a9641',  # Dark green (best)
        'B': '#a6d96a',  # Light green
        'C': '#ffffbf',  # Yellow
        'D': '#fdae61',  # Light orange
        'E': '#f46d43',  # Orange
        'F': '#d73027',  # Red
        'G': '#a50026'   # Dark red (worst)
    }
    
    # Define the order for DPE labels
    dpe_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    
    # Filter out any missing values
    if hue_col:
        df_clean = df.dropna(subset=[col_name, hue_col])
    else:
        df_clean = df.dropna(subset=[col_name])
    
    if plot_type == 'histogram':
        if hue_col:
            fig = px.histogram(
                df_clean,
                x=col_name,
                color=hue_col,
                marginal="rug",  # Add rug plot on top
                color_discrete_map=dpe_color_map,
                category_orders={hue_col: dpe_order},
                title=f'Distribution of {col_name}' + (f' by {hue_col}' if hue_col else ''),
                labels={col_name: col_name, hue_col: hue_col.replace('_', ' ').title()} if hue_col else {col_name: col_name},
                opacity=opacity,
                height=height,
                width=width
            )
        else:
            fig = px.histogram(
                df_clean,
                x=col_name,
                marginal="rug",  # Add rug plot on top
                title=f'Distribution of {col_name}',
                labels={col_name: col_name},
                opacity=opacity,
                height=height,
                width=width
            )
        
    elif plot_type == 'box':
        if hue_col:
            fig = px.box(
                df_clean,
                y=col_name,
                color=hue_col,
                color_discrete_map=dpe_color_map,
                category_orders={hue_col: dpe_order},
                title=f'Box Plot of {col_name_alias}' + (f' by {hue_col_alias}' if hue_col else ''),
                labels={col_name: col_name, hue_col: hue_col.replace('_', ' ').title()} if hue_col else {col_name: col_name},
                height=height,
                width=width
            )
        else:
            fig = px.box(
                df_clean,
                y=col_name,
                title=f'Box Plot of {col_name_alias}',
                labels={col_name: col_name},
                height=height,
                width=width
            )
        
    elif plot_type == 'violin':
        if hue_col:
            fig = px.violin(
                df_clean,
                y=col_name,
                color=hue_col,
                color_discrete_map=dpe_color_map,
                category_orders={hue_col: dpe_order},
                title=f'Violin Plot of {col_name}' + (f' by {hue_col}' if hue_col else ''),
                labels={col_name: col_name, hue_col: hue_col.replace('_', ' ').title()} if hue_col else {col_name: col_name},
                height=height,
                width=width
            )
        else:
            fig = px.violin(
                df_clean,
                y=col_name,
                title=f'Violin Plot of {col_name}',
                labels={col_name: col_name},
                height=height,
                width=width
            )
        
    elif plot_type == 'density':
        # Create density plots using distplot (similar to seaborn's kdeplot)
        fig = go.Figure()
        
        if hue_col:
            for dpe_label in dpe_order:
                if dpe_label in df_clean[hue_col].values:
                    data_subset = df_clean[df_clean[hue_col] == dpe_label][col_name]
                    
                    if len(data_subset) > 1:  # Need at least 2 points for KDE
                        # Create KDE
                        x_range = np.linspace(data_subset.min(), data_subset.max(), 100)
                        kde = stats.gaussian_kde(data_subset)
                        density = kde(x_range)
                        
                        fig.add_trace(go.Scatter(
                            x=x_range,
                            y=density,
                            mode='lines',
                            fill='tonexty' if dpe_label != dpe_order[0] else 'tozeroy',
                            name=f'{hue_col}: {dpe_label}',
                            line=dict(color=dpe_color_map[dpe_label]),
                            fillcolor=dpe_color_map[dpe_label],
                            opacity=opacity
                        ))
            title_text = f'Density Distribution of {col_name_alias} by {hue_col_alias}'
        else:
            # Single density plot without hue
            data_subset = df_clean[col_name]
            if len(data_subset) > 1:
                x_range = np.linspace(data_subset.min(), data_subset.max(), 100)
                kde = stats.gaussian_kde(data_subset)
                density = kde(x_range)
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=density,
                    mode='lines',
                    fill='tozeroy',
                    name='Density',
                    line=dict(color='blue'),
                    fillcolor='blue',
                    opacity=opacity
                ))
            title_text = f'Density Distribution of {col_name_alias}'
        
        fig.update_layout(
            title=title_text,
            xaxis_title=col_name_alias,
            yaxis_title='Density',
            height=height,
            width=width
        )
    
    else:
        raise ValueError("plot_type must be one of: 'histogram', 'box', 'violin', or 'density'")
    
    # Update layout for better appearance
    if hue_col:
        fig.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            margin=dict(r=150),  # Add right margin for legend
            showlegend=True
        )
    else:
        fig.update_layout(
            showlegend=False
        )
    return fig


def plot_categorical_with_dpe_hue_plotly(df, col_name, col_name_alias, col_map=None, log_scale_y=False, 
                                        stacked=True, height=600, width=1000):
    """
    Plots a categorical variable from a DataFrame with 'etiquette_dpe_ademe' as hue,
    ordered by DPE label and sorted within each category, as a stacked bar chart using Plotly.
    Color code: RdYlGn_r colormap (green=A/good, red=G/bad)
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        col_name (str): The name of the categorical column to plot.
        col_map (dict, optional): A dictionary mapping the categorical labels to their desired order. 
                                 Defaults to None.
        log_scale_y (bool, optional): Whether to use a log scale for the y-axis. Defaults to False.
        stacked (bool, optional): Whether to show as percentages (True) or counts (False). 
                                 Defaults to True.
        height (int): Height of the plot in pixels. Defaults to 600.
        width (int): Width of the plot in pixels. Defaults to 1000.
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object.
    """
    
    # Create a copy to avoid modifying the original DataFrame
    df_plot = df.copy()
    
    # Group by the categorical column and the DPE label, then count
    grouped_counts = df_plot.groupby([col_name, 'etiquette_dpe_ademe']).size().unstack(fill_value=0)
    
    # Reindex rows (x-axis categories) based on the provided col_map or default to sorting
    if col_map:
        # Create a list of ordered categories from col_map that are present in the grouped_counts index
        ordered_categories = [k for k, v in sorted(col_map.items(), key=lambda item: item[1]) 
                            if k in grouped_counts.index]
        ordered_categories = list(map(lambda m: f"{m[:10]}.", ordered_categories))
        grouped_counts = grouped_counts.reindex(ordered_categories)
    elif col_name in df.columns and df[col_name].dtype.name == 'category':
        ordered_categories = df[col_name].cat.categories
        ordered_categories = list(map(lambda m: f"{m[:10]}.", ordered_categories))
        grouped_counts = grouped_counts.reindex(ordered_categories)
    else:
        grouped_counts = grouped_counts.sort_index()  # Default to sorting index
        categs = list(map(lambda m: f"{m[:10]}" if len(m)>10 else m, list(grouped_counts.index)))
        grouped_counts.reindex(categs)
    
    # Convert to percentages if stacked
    if stacked:
        grouped_counts_pct = grouped_counts.div(grouped_counts.sum(axis=1), axis=0) * 100
        data_to_plot = grouped_counts_pct
        y_title = 'Percentage (%)'
    else:
        data_to_plot = grouped_counts
        y_title = 'Count (log scale)' if log_scale_y else 'Count'
    
    # Define DPE color mapping (RdYlGn_r: green=good/A, red=bad/G)
    dpe_color_map = {
        'A': '#1a9641',  # Dark green (best)
        'B': '#a6d96a',  # Light green
        'C': '#ffffbf',  # Yellow
        'D': '#fdae61',  # Light orange
        'E': '#f46d43',  # Orange
        'F': '#d73027',  # Red
        'G': '#a50026'   # Dark red (worst)
    }
    
    # Reset index to make it work with plotly
    data_melted = data_to_plot.reset_index().melt(
        id_vars=[col_name], 
        var_name='etiquette_dpe_ademe', 
        value_name='value'
    )
    
    # Create the stacked bar chart
    fig = px.bar(
        data_melted,
        x=col_name,
        y='value',
        color='etiquette_dpe_ademe',
        color_discrete_map=dpe_color_map,
        category_orders={
            'etiquette_dpe_ademe': ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        },
        title=f'Distribution of {col_name_alias} by Etiquette DPE ADEME ({"Stacked %" if stacked else "Stacked Count"})',
        labels={
            col_name: col_name_alias,
            'value': y_title,
            'etiquette_dpe_ademe': 'Etiquette DPE ADEME'
        },
        height=height,
        width=width
    )
    
    # Apply log scale if requested
    if log_scale_y:
        fig.update_yaxes(type="log")
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_tickangle=-45,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150),  # Add right margin for legend
        showlegend=True
    )
    return fig