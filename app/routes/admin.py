@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if session.get('username') != 'admin':
        flash('У вас нет доступа к этой странице', 'error')
        return redirect(url_for('shop.home'))
        
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category_id = int(request.form['category_id'])
        
        # Обработка характеристик
        specifications = {}
        for key in request.form:
            if key.startswith('spec_key_') and request.form[key]:
                index = key.split('_')[-1]
                value = request.form.get(f'spec_value_{index}')
                if value:
                    specifications[request.form[key]] = value
        
        product.specifications = specifications
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image = filename
        
        db.session.commit()
        flash('Товар успешно обновлен', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', product=product, categories=categories)

@bp.route('/products/<int:product_id>/add_specification', methods=['POST'])
@login_required
def add_specification(product_id):
    if session.get('username') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    product = Product.query.get_or_404(product_id)
    key = request.form.get('key')
    value = request.form.get('value')
    
    if not key or not value:
        return jsonify({'error': 'Key and value are required'}), 400
    
    if not product.specifications:
        product.specifications = {}
    
    product.specifications[key] = value
    db.session.commit()
    
    return jsonify({'success': True, 'specifications': product.specifications})

@bp.route('/products/<int:product_id>/remove_specification', methods=['POST'])
@login_required
def remove_specification(product_id):
    if session.get('username') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    product = Product.query.get_or_404(product_id)
    key = request.form.get('key')
    
    if not key or not product.specifications or key not in product.specifications:
        return jsonify({'error': 'Invalid specification key'}), 400
    
    del product.specifications[key]
    db.session.commit()
    
    return jsonify({'success': True, 'specifications': product.specifications}) 