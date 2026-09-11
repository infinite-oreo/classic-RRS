from . import archive, entries, favorites, feeds, opml_routes, today


def register_blueprints(app):
    app.register_blueprint(today.bp)
    app.register_blueprint(feeds.bp)
    app.register_blueprint(entries.bp)
    app.register_blueprint(favorites.bp)
    app.register_blueprint(archive.bp)
    app.register_blueprint(opml_routes.bp)
