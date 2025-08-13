from app_backend.api.routes import Flask_app
import os

if __name__ == "__main__":
    app_instance = Flask_app()
    app = app_instance.get_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
