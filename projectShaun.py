from app import app



app.run(ssl_context='adhoc', host="0.0.0.0", threaded=True)
