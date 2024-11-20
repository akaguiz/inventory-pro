from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.item import Item
from app import db

inventory = Blueprint('inventory', __name__)

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