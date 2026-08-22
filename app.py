with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password="admin123"
        )
        db.session.add(admin)
        db.session.commit()