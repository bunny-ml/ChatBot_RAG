from app_backend.api.routes import Flask_app

if __name__ == "__main__":
    app_instance = Flask_app()
    app = app_instance.get_app()
    app.run(debug=True)
