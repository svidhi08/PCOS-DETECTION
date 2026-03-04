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
import tensorflow as tf
from tensorflow.keras.applications.mobilenet import preprocess_input

# ============================================================
# ENVIRONMENT & MEMORY CONFIG
# ============================================================
# Force TensorFlow to use only CPU and minimal memory for deployment compatibility
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Limit TensorFlow CPU threads (VERY IMPORTANT for Render Free tier)
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# LOAD MODELS
# ============================================================
MODEL_PATH = "model/bestmodel.h5"
try:
    # compile=False avoids version mismatch errors in the optimizer
    model = load_model(MODEL_PATH, compile=False)
    logger.info("✅ TensorFlow Model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading Deep Learning model: {e}")
    model = None

try:
    # Load ML models for the health questionnaire analysis
    ml_model = joblib.load("model/pcos_model.pkl")
    preprocessor = joblib.load("model/preprocessor.pkl")
    logger.info("✅ Health Questionnaire Model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading ML models: {e}")
    ml_model = None
    preprocessor = None

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def allowed_file(filename):
    """Check if file extension is among the allowed types"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def model_predict(img_path, model):
    """
    MobileNet requires 224x224 input and specific pixel scaling.
    """
    try:
        img = load_img(img_path, target_size=(224, 224))
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x, verbose=0)
        return preds
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        raise

def get_prediction_result(val):
    """Map prediction value to result data for the frontend"""
    # val=0 usually indicates PCOS (Positive) in binary classification folders
    if val == 0:
        return {
            "result": "PCOS Detected",
            "status": "infected",
            "message": "The ultrasound shows characteristic signs of PCOS. Please consult with a healthcare professional.",
            "color": "#ff6b6b",
            "symptoms": [
                "Irregular or missed menstrual periods", 
                "Excess facial and body hair (hirsutism)", 
                "Severe acne or oily skin",
                "Thinning hair on the scalp",
                "Weight gain or difficulty losing weight"
            ],
            "precautions": [
                "Schedule a consultation with a Gynecologist", 
                "Maintain a balanced, low-sugar diet", 
                "Engage in regular physical activity",
                "Monitor your blood sugar and insulin levels"
            ],
            "advice": "Early diagnosis can help manage symptoms effectively and prevent long-term complications."
        }
    else:
        return {
            "result": "No PCOS Detected",
            "status": "not_infected",
            "message": "The ultrasound scan appears normal with no visible cystic patterns.",
            "color": "#51cf66",
            "watch_for": [
                "Changes in menstrual cycle frequency", 
                "Sudden appearance of hormonal acne", 
                "Unexplained changes in weight"
            ],
            "healthy_tips": [
                "Stay hydrated and maintain a high-fiber diet", 
                "Aim for 7-8 hours of quality sleep", 
                "Practice stress management through yoga or meditation"
            ],
            "advice": "Maintain a healthy lifestyle for hormonal balance."
        }

# ============================================================
# ROUTES
# ============================================================
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
            return jsonify({'error': 'Invalid file type (PNG, JPG, JPEG only)'}), 400
        
        filename = secure_filename(f.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(file_path)
        
        # Prediction
        preds = model_predict(file_path, model)
        pred_value = float(preds[0][0])
        
        # Classification Logic
        if pred_value < 0.5:
            y_class_idx = 0 
            confidence = 1 - pred_value 
        else:
            y_class_idx = 1
            confidence = pred_value

        result = get_prediction_result(y_class_idx)
        result['confidence'] = f"{confidence * 100:.2f}%"
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {e}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

@app.route('/analyze_health', methods=['POST'])
def analyze_health():
    """Processes the questionnaire data using the Scikit-Learn model"""
    try:
        if ml_model is None or preprocessor is None:
            return jsonify({'error': 'Health analysis model not available'}), 500

        form_data = request.get_json()
        if not form_data:
            return jsonify({'error': 'No data received'}), 400

        # DataFrame conversion
        input_df = pd.DataFrame([form_data])

        # Processing & Prediction
        input_processed = preprocessor.transform(input_df)
        prob = ml_model.predict_proba(input_processed)[0][1]
        risk_score = round(prob * 100, 1)

        # Risk Level Mapping
        if risk_score >= 70:
            risk_level, color, message = "High Risk", "#ff6b6b", "Higher likelihood of PCOS symptoms. Clinical consultation recommended."
        elif risk_score >= 40:
            risk_level, color, message = "Moderate Risk", "#ffa94d", "Some indicators present. Monitor your symptoms closely."
        else:
            risk_level, color, message = "Low Risk", "#51cf66", "Low correlation with typical PCOS risk factors."

        # Factor Extraction for UI
        risk_factors = []
        if form_data.get('cycle_pattern') != 'regular': risk_factors.append("Irregular Cycles")
        if 'yes' in str(form_data.get('hirsutism', '')).lower(): risk_factors.append("Excessive Hair Growth")
        if 'yes' in str(form_data.get('acne', '')).lower(): risk_factors.append("Hormonal Acne")

        return jsonify({
            "risk_level": risk_level,
            "risk_score": risk_score,
            "color": color,
            "message": message,
            "confidence": f"{risk_score}%",
            "risk_factors": risk_factors,
            "recommendations": [
                "Consult a healthcare professional",
                "Maintain a consistent sleep schedule",
                "Regular physical activity (30 mins/day)"
            ]
        })

    except Exception as e:
        logger.error(f"Error in health analysis: {e}")
        return jsonify({'error': 'Analysis failed. Please ensure all questions are answered.'}), 500

# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large (Max 16MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

# ============================================================
# APP EXECUTION
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)