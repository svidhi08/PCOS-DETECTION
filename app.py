from __future__ import division, print_function
import os
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# LOAD TENSORFLOW MODEL (from Jupyter notebook)
# ============================================================
MODEL_PATH = "model/bestmodel.h5"
model = load_model(MODEL_PATH)
logger.info("✅ TensorFlow Model loaded successfully!")

# ============================================================
# LOAD ML MODELS FOR HEALTH QUESTIONNAIRE
# ============================================================
try:
    ml_model = joblib.load("model/pcos_model.pkl")
    preprocessor = joblib.load("model/preprocessor.pkl")  # Only preprocessor now
    logger.info("✅ Health Questionnaire Model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading ML models: {e}")
    logger.warning("⚠️  Health questionnaire will not be available")
    ml_model = None
    preprocessor = None

logger.info("💻 Starting Flask app at: http://127.0.0.1:5000/")

# HELPER FUNCTIONS
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def model_predict(img_path, model):
    """Make prediction on the image"""
    try:
        img = load_img(img_path, target_size=(224, 224), interpolation='nearest')
        x = img_to_array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        preds = model.predict(x, verbose=0)
        return preds
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise

def get_prediction_result(val):
    """Map prediction value to result with confidence"""
    if val == 0:
        return {
            "result": "PCOS Detected",
            "status": "infected",
            "message": "The ultrasound shows signs of PCOS. Please consult with a healthcare professional for proper diagnosis and treatment.",
            "color": "#ff6b6b"
        }
    else:
        return {
            "result": "No PCOS Detected",
            "status": "not_infected",
            "message": "The ultrasound appears normal. However, if you have symptoms, please consult a healthcare professional.",
            "color": "#51cf66"
        }


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/aboutus', methods=['GET'])
def aboutus():
    return render_template('about.html')

@app.route('/contactus', methods=['GET'])
def contactus():
    return render_template('contact.html')

@app.route('/detailcheck', methods=['GET'])
def detailcheck():
    return render_template('detailcheck.html')

@app.route('/predict', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        f = request.files['file']
        if f.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not allowed_file(f.filename):
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or JPEG files only.'}), 400
        
        filename = secure_filename(f.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(file_path)
        
        preds = model_predict(file_path, model)
        y_class = ((preds > 0.5) + 0).ravel()
        pred_value = float(preds[0][0])
        confidence = pred_value if y_class[0] == 1 else 1 - pred_value
        
        result = get_prediction_result(y_class[0])
        result['confidence'] = f"{confidence * 100:.2f}%"
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {e}")
        return jsonify({'error': 'An error occurred during prediction. Please try again.'}), 500

# HEALTH QUESTIONNAIRE
@app.route('/analyze_health', methods=['POST'])
def analyze_health():
    try:
        if ml_model is None or preprocessor is None:
            return jsonify({'error': 'Health model not loaded'}), 500

        form_data = request.get_json()
        if not form_data:
            return jsonify({'error': 'No data received'}), 400

        # Convert form data to DataFrame
        input_df = pd.DataFrame([form_data])

        # Preprocess input
        input_processed = preprocessor.transform(input_df)

        # Predict probability
        prob = ml_model.predict_proba(input_processed)[0][1]  # probability of PCOS
        risk_score = round(prob * 100, 1)

        # Determine risk level and color
        if risk_score >= 70:
            risk_level = "High Risk"
            color = "#ff6b6b"
            message = "Higher likelihood of PCOS. Please consult a healthcare professional."
        elif risk_score >= 40:
            risk_level = "Moderate Risk"
            color = "#ffa94d"
            message = "Moderate risk indicators for PCOS. Consider consulting a healthcare provider."
        else:
            risk_level = "Low Risk"
            color = "#51cf66"
            message = "Low risk for PCOS."

        # Identify risk factors from form data
        risk_factors = []
        if form_data.get('cycle_pattern') in ['irregular', 'rare', 'absent']:
            risk_factors.append("Irregular menstrual cycles")
        if form_data.get('hirsutism', '').startswith('yes'):
            risk_factors.append("Excess hair growth")
        if form_data.get('acne', '').startswith('yes'):
            risk_factors.append("Acne or oily skin")
        if form_data.get('weight_difficulty', '').startswith('yes'):
            risk_factors.append("Weight management difficulties")
        if form_data.get('insulin_resistance') == 'yes_diagnosed':
            risk_factors.append("Insulin resistance or diabetes")
        if form_data.get('ultrasound_pco') == 'yes':
            risk_factors.append("Polycystic ovaries on ultrasound")

        recommendations = [
            "Maintain a healthy lifestyle with regular exercise",
            "Monitor menstrual cycle",
            "Consult a healthcare provider if concerned"
        ]

        return jsonify({
            "risk_level": risk_level,
            "risk_score": risk_score,
            "color": color,
            "message": message,
            "confidence": f"{prob*100:.1f}%",
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "next_steps": "Consult a healthcare professional if you are concerned about your results."
        })

    except Exception as e:
        logger.error(f"Error in health analysis: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred during health analysis.'}), 500

# ERROR HANDLERS
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500

# RUN APP
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
