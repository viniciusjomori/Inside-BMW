from flask import Flask, request, abort
import pandas as pd

from utils import format_number

app = Flask(__name__)
app.json.sort_keys = False

def get_df_bmw() -> pd.DataFrame:
    file = None
    
    try:
        file = request.files['file']
    except KeyError:
        abort(400, description="O arquivo 'file' é obrigatório.")

    if not file or file.filename == '':
        abort(400)

    return pd.read_csv(file)

@app.route("/bmw/resume", methods=["POST"])
def get_resume():
    df_bmw = get_df_bmw()

    resume = {
        'length': len(df_bmw),
        'period': f"{df_bmw['Year'].min()} - {df_bmw['Year'].max()}",
        'different_models': int(df_bmw['Model'].nunique()),
        'price_avg': format_number(
            float(df_bmw['Price_USD'].mean())
        ),
        'colors': df_bmw['Color'].unique().tolist(),
        'total': format_number(
            int(df_bmw['Price_USD'].sum() * df_bmw['Sales_Volume'].sum())
        ),
    }

    return resume

@app.route('/bmw/sales_by_region', methods=["POST"])
def get_sales_by_region():
    df_bmw = get_df_bmw()

    df_groupped = df_bmw.groupby('Region', as_index=False)['Sales_Volume'].sum()
    df_groupped['Sales_Volume'] = df_groupped['Sales_Volume'].apply(format_number)
    df_groupped = df_groupped.sort_values('Sales_Volume', ascending=False)

    return df_groupped.to_dict(orient='records')

@app.route('/bmw/fuel_popularity', methods=["POST"])
def get_eletric_popularity():
    df_bmw = get_df_bmw()
    allowed_types = df_bmw['Fuel_Type'].unique().tolist()

    fuel_type = request.args.get('fuel_type', type=str)

    if not fuel_type:
        abort(400, description=f"O parâmetro 'fuel_type' deve ser um entre {', '.join(allowed_types)}")
    
    fuel_type = fuel_type.capitalize()

    if fuel_type not in allowed_types:
        abort(400, description=f"O parâmetro 'fuel_type' deve ser um entre {', '.join(allowed_types)}")

    df_filtred = df_bmw.query(f"Fuel_Type == '{fuel_type}'")
    df_groupped = df_filtred.groupby('Year', as_index=False)['Sales_Volume'].sum()

    df_groupped = df_groupped.sort_values('Year', ascending=True)
    df_groupped['evolution'] = df_groupped['Sales_Volume'].diff()

    df_groupped['Sales_Volume'] = df_groupped['Sales_Volume'].apply(format_number)
    df_groupped['evolution'] = df_groupped['evolution'].apply(format_number)

    return df_groupped.to_dict(orient='records')

@app.route('/bmw/colorful_winners', methods=["POST"])
def get_colorful_winners():
    df_bmw = get_df_bmw()

    df_bmw['colorful'] = df_bmw['Color'].apply(
        lambda c: c not in ['Black', 'White']
    )

    is_colorful = request.args.get('colorful', default=False, type=lambda c: c.lower() in ['true', '1', 'yes', 'sim'])
    df_bmw = df_bmw.query(f'colorful == {is_colorful}')
    df_groupped = df_bmw.groupby('Model', as_index=False)['Sales_Volume'].sum()

    df_groupped['Sales_Volume'] = df_groupped['Sales_Volume'].apply(format_number)
    df_groupped = df_groupped.sort_values('Sales_Volume', ascending=False)

    return df_groupped.to_dict(orient='records')

@app.route('/bmw/price_evolution', methods=["POST"])
def get_pricing_evolution():
    df_bmw = get_df_bmw()

    df_gp = df_bmw.groupby(['Year', 'Model'], as_index=False)['Price_USD'].mean()

    df_pivot = df_gp.pivot_table(
        index='Model',
        columns='Year',
        values='Price_USD',
        aggfunc='mean'
    ).reset_index()

    for col in df_pivot.columns[1:]:
        df_pivot[col] = df_pivot[col].apply(format_number)

    return df_pivot.to_dict(orient='records')

if __name__ == '__main__':
    app.run(debug=True)