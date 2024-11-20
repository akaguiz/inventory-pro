from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.item import Item
from app.models.sale import Sale
from app import db
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta

reports = Blueprint('reports', __name__)

@reports.route('/reports', methods=['GET'])
@login_required
def show_reports():
    items = Item.query.filter_by(user_id=current_user.id).all()
    
    if not items:
        flash('Você precisa cadastrar produtos primeiro!', 'warning')
        return render_template('reports.html', predictions=None, has_enough_data=False)
    
    product_predictions = {}
    product_statistics = {}
    
    for item in items:
        sales = Sale.query.filter_by(user_id=current_user.id, item_id=item.id).all()
        
        if len(sales) < 30:
            product_statistics[item.name] = {
                'total_sales': len(sales),
                'total_quantity': sum(sale.quantity for sale in sales),
                'average_quantity': round(sum(sale.quantity for sale in sales) / len(sales), 2) if sales else 0,
                'needs_more_data': True
            }
            continue
            
        sales_data = pd.DataFrame([sale.to_dict() for sale in sales])
        sales_data['sale_date'] = pd.to_datetime(sales_data['sale_date'])
        
        sales_data['day_of_week'] = sales_data['sale_date'].dt.dayofweek
        sales_data['month'] = sales_data['sale_date'].dt.month
        sales_data['day'] = sales_data['sale_date'].dt.day
        
        X = sales_data[['day_of_week', 'month', 'day']]
        y = sales_data['quantity']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        future_features = pd.DataFrame({
            'day_of_week': future_dates.dayofweek,
            'month': future_dates.month,
            'day': future_dates.day
        })
        
        future_features_scaled = scaler.transform(future_features)
        predictions = model.predict(future_features_scaled)
        
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        prediction_data = []
        total_predicted = 0
        for date, pred in zip(future_dates, predictions):
            predicted_value = max(0, round(pred))
            total_predicted += predicted_value
            prediction_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_sales': predicted_value
            })
        
        product_statistics[item.name] = {
            'total_sales': len(sales),
            'total_quantity': sum(sale.quantity for sale in sales),
            'average_quantity': round(sum(sale.quantity for sale in sales) / len(sales), 2),
            'predicted_next_30_days': total_predicted,
            'average_predicted_daily': round(total_predicted / 30, 2),
            'model_accuracy': round(test_score * 100, 2),
            'needs_more_data': False
        }
        
        product_predictions[item.name] = {
            'predictions': prediction_data,
            'train_score': f"{train_score:.2f}",
            'test_score': f"{test_score:.2f}"
        }
    
    return render_template(
        'reports.html',
        product_predictions=product_predictions,
        product_statistics=product_statistics,
        has_predictions=bool(product_predictions)
    )

@reports.route('/record_sale', methods=['GET'])
@login_required
def record_sale():
    try:
        item_id = int(request.form['item_id'])
        quantity = int(request.form['quantity'])
        
        item = Item.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            flash('Acesso negado!', 'error')
            return redirect(url_for('inventory.index'))
        
        sale = Sale(
            item_id=item_id,
            quantity=quantity,
            user_id=current_user.id
        )
        
        db.session.add(sale)
        db.session.commit()
        
        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('reports.show_reports'))
        
    except Exception as e:
        flash(f'Erro ao registrar venda: {str(e)}', 'error')
        return redirect(url_for('reports.show_reports'))