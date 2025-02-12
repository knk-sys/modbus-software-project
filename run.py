from app import create_app

# Create an instance of the Flask app using the factory function
app = create_app()

# Run the app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)
