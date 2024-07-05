from waitress import serve
from server import app, main

if __name__ == '__main__':
    main()  # Hauptskript von server.py ausführen
    serve(app, host='127.0.0.1', port=5000, threads=4)