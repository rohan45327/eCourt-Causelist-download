from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
from scraper import download_cause_lists
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/download', methods=['POST'])
def readydown():
    data=request.get_json()
    date_obj=datetime.strptime(data.get('date'), '%Y-%m-%d')
    formatted=date_obj.strftime('%d-%m-%Y')
    state=data.get('state')
    district= data.get('district')
    complex= data.get('complex')
    print("--- [App] Received request. Starting background download thread. ---")
    thread = threading.Thread(
        target=download_cause_lists,
        args=(state, district, complex, formatted)
    )
    thread.start()
    return jsonify({
        "status": "success", 
        "message": "Download process has started in the background! Please check your terminal for progress."
    })
if __name__ == '__main__':
    app.run(debug=True)