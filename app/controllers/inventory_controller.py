from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.item import Item
from app import db
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime

inventory = Blueprint('inventory', __name__)

# Rota para visualizar a previsão de vendas
@inventory.route('/sales_forecast/<int:item_id>', methods=['GET'])
@login_required
def sales_forecast(item_id):
    item = Item.query.get_or_404(item_id)

    # Simulação de dados de vendas (aqui você substitui pelos dados reais do banco)
    sales_data = [
        {"date": "2024-11-01", "quantity": 10},
        {"date": "2024-11-02", "quantity": 12},
        {"date": "2024-11-03", "quantity": 14},
        {"date": "2024-11-04", "quantity": 13},
        {"date": "2024-11-05", "quantity": 15},
        {"date": "2024-11-06", "quantity": 16},
        {"date": "2024-11-07", "quantity": 17},
    ]

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(sales_data)
    df['date'] = pd.to_datetime(df['date'])

    # Extraindo as características do tempo
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day'] = df['date'].dt.day

    # Modelagem de previsão (usando regressão linear)
    X = df[['day_of_week', 'day']]  # Características
    y = df['quantity']  # Quantidade de vendas

    model = LinearRegression()
    model.fit(X, y)

    # Prevendo as vendas para os próximos 7 dias
    future_dates = pd.date_range(datetime.now(), periods=7, freq='D')
    future_features = pd.DataFrame({
        'day_of_week': future_dates.dayofweek,
        'day': future_dates.day
    })

    predictions = model.predict(future_features)

    # Criando o gráfico de previsão com Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=future_dates, 
        y=predictions, 
        mode='lines+markers', 
        name='Previsão de Vendas',
        marker=dict(color='blue')
    ))

    # Gerando o gráfico como HTML
    graph_html = fig.to_html(full_html=False)

    # Retornando o template de previsão de vendas
    return render_template('sales_forecast.html', item=item, graph_html=graph_html)


@inventory.route('/')
@login_required
def index():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', items=items)

@inventory.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        
        new_item = Item(
            name=name, 
            description=description, 
            quantity=quantity,
            user_id=current_user.id
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        flash('Item adicionado com sucesso!', 'success')
        return redirect(url_for('inventory.index'))
    
    return render_template('add.html')

@inventory.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    item = Item.query.get_or_404(id)
    
    if item.user_id != current_user.id:
        flash('Acesso negado!', 'error')
        return redirect(url_for('inventory.index'))
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.quantity = int(request.form['quantity'])
        
        db.session.commit()
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('inventory.index'))
    
    return render_template('edit.html', item=item)

@inventory.route('/delete/<int:id>')
@login_required
def delete(id):
    item = Item.query.get_or_404(id)
    
    if item.user_id != current_user.id:
        flash('Acesso negado!', 'error')
        return redirect(url_for('inventory.index'))
        
    db.session.delete(item)
    db.session.commit()
    
    flash('Item excluído com sucesso!', 'success')
    return redirect(url_for('inventory.index'))