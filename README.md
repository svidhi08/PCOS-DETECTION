<div align="center">
  <h1>PCOS Detector – Smart PCOS Checking System</h1>
  <p><strong>A web application that uses AI to help check the risk of PCOS at an early stage.</strong></p>

</div>

<hr/>

<h2>📌 Project Overview</h2>

<p>
<strong>PCOS Detector</strong> is a web application that helps women check the possible risk of PCOS using AI.
It combines image checking and health questions to give better results.
</p>

<ul>
  <li><strong>Ultrasound Image Check:</strong> Upload a scan image and the system analyzes it using a deep learning model.</li>
  <li><strong>Health Risk Questions:</strong> Answer simple questions about symptoms and health conditions to calculate risk.</li>
</ul>

<hr/>

<h2>🛠️ Technologies Used</h2>

<ul>
  <li><strong>Deep Learning (CNN):</strong> A trained model that checks ultrasound images and predicts PCOS probability.</li>
  <li><strong>Machine Learning:</strong> A model that analyzes symptoms using health-related data.</li>
  <li><strong>Flask:</strong> Handles the backend, image upload, and model predictions.</li>
  <li><strong>Frontend Design:</strong> Clean and modern UI using Glassmorphism style with smooth animations.</li>
</ul>

<hr/>

<h2>🚀 Main Features</h2>

<ul>
  <li><strong>Shows Probability:</strong> Instead of just Yes/No, it shows the percentage chance (like 87%).</li>
  <li><strong>Secure Image Upload:</strong> Accepts only valid image types (PNG/JPG) and resizes automatically.</li>
  <li><strong>Responsive Dashboard:</strong> Works properly on different screen sizes.</li>
  <li><strong>Fast Processing:</strong> Results appear without refreshing the page.</li>
</ul>

<hr/>

<h2>📸 Project Screenshots</h2>

<table align="center" border="1" cellpadding="6">
  <tr>
    <td align="center">
      <img src="images/home.png" width="250"><br/>
      <b>Home Page</b>
    </td>
    <td align="center">
      <img src="images/questionarries.png" width="250"><br/>
      <b>Health Questionnaire</b>
    </td>
    <td align="center">
      <img src="images/about.png" width="250"><br/>
      <b>About Us</b>
    </td>
  </tr>
</table>

<hr/>


<h2>📖 How to Run the Project</h2>

<ol>
  <li>Clone the repository and install required libraries:
    <pre>git clone git clone https://github.com/your-username/Foodies.git</pre>
    <pre>pip install requirements.txt</pre>
  </li>
  <li>Make sure the model folder looks like this:
    <pre>
/model
  ├── bestmodel.h5
  ├── pcos_model.pkl
  └── preprocessor.pkl
    </pre>
  </li>
  <li>Run the app:
    <pre>python app.py</pre>
  </li>
</ol>

<hr/>

<h2>⚠️ Disclaimer</h2>

<p>
This project is for learning and early screening only.
It does NOT replace a real doctor’s diagnosis.
Please consult a medical professional for proper medical advice.
</p>

<div align="center">
  <p><i>Developed by <b>Vidhi</b> 💜</i></p>
</div>
