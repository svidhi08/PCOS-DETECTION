$(document).ready(function () {
    // Init
    $('.result-section').hide();
    $('.loader').hide();
    $('#result').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                // Clear previous content and show image directly
                $('#imagePreview').html('<img src="' + e.target.result + '" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 10px;">');
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    
    $("#imageUpload").change(function () {
        $('.result-section').show();
        $('#btn-predict').show();
        $('#result').html('');
        $('#result').hide();
        readURL(this);
    });

    // Predict
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Hide loader
                $('.loader').hide();
                
                // Check if there's an error
                if (data.error) {
                    $('#result').html(`
                        <div style="padding: 20px; background: rgba(255, 107, 107, 0.15); border-radius: 15px; border: 2px solid rgba(255, 107, 107, 0.4);">
                            <h2 style="color: #ff6b6b; margin: 0 0 10px 0; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">❌ Error</h2>
                            <p style="color: white; margin: 0; font-size: 1.1rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">${data.error}</p>
                        </div>
                    `);
                } else {
                    // Display success result with styling
                    const resultColor = data.color || '#51cf66';
                    const statusIcon = data.status === 'infected' ? '⚠️' : '✅';
                    
                    let resultHTML = `
                        <div style="padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);">
                            <h2 style="color: ${resultColor}; margin: 0 0 15px 0; font-size: 2rem; text-shadow: 2px 2px 8px rgba(0,0,0,0.4);">
                                ${statusIcon} ${data.result}
                            </h2>
                            <p style="color: white; margin: 0 0 15px 0; font-size: 1.2rem; font-weight: 600; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">
                                Confidence: ${data.confidence}
                            </p>
                            <p style="color: rgba(255, 255, 255, 0.95); margin: 0 0 20px 0; font-size: 1rem; line-height: 1.6; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 10px; border-left: 4px solid rgba(255, 255, 255, 0.4); text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                ${data.message}
                            </p>
                    `;

                    // Add symptoms section if PCOS detected
                    if (data.symptoms && data.symptoms.length > 0) {
                        resultHTML += `
                            <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.06); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15);">
                                <h3 style="color: white; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">
                                    🔍 Common Symptoms
                                </h3>
                                <ul style="list-style: none; padding: 0; margin: 0;">
                        `;
                        
                        data.symptoms.forEach(function(symptom) {
                            resultHTML += `
                                <li style="color: rgba(255, 255, 255, 0.95); padding: 10px 0 10px 30px; position: relative; font-size: 1rem; line-height: 1.5; border-bottom: 1px solid rgba(255, 255, 255, 0.08); text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                    <span style="position: absolute; left: 0; color: #66ff99; font-weight: bold; font-size: 1.2rem; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">✓</span>
                                    ${symptom}
                                </li>
                            `;
                        });
                        
                        resultHTML += `
                                </ul>
                            </div>
                        `;
                    }

                    // Add watch_for section if normal result
                    if (data.watch_for && data.watch_for.length > 0) {
                        resultHTML += `
                            <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.06); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15);">
                                <h3 style="color: white; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">
                                    🩺 Watch For These Signs
                                </h3>
                                <ul style="list-style: none; padding: 0; margin: 0;">
                        `;
                        
                        data.watch_for.forEach(function(sign) {
                            resultHTML += `
                                <li style="color: rgba(255, 255, 255, 0.95); padding: 10px 0 10px 30px; position: relative; font-size: 1rem; line-height: 1.5; border-bottom: 1px solid rgba(255, 255, 255, 0.08); text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                    <span style="position: absolute; left: 0; color: #66ff99; font-weight: bold; font-size: 1.2rem; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">✓</span>
                                    ${sign}
                                </li>
                            `;
                        });
                        
                        resultHTML += `
                                </ul>
                            </div>
                        `;
                    }

                    // Add precautions section if PCOS detected
                    if (data.precautions && data.precautions.length > 0) {
                        resultHTML += `
                            <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.06); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15);">
                                <h3 style="color: white; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">
                                    💊 What You Should Do
                                </h3>
                                <ul style="list-style: none; padding: 0; margin: 0;">
                        `;
                        
                        data.precautions.forEach(function(precaution) {
                            resultHTML += `
                                <li style="color: rgba(255, 255, 255, 0.95); padding: 10px 0 10px 30px; position: relative; font-size: 1rem; line-height: 1.5; border-bottom: 1px solid rgba(255, 255, 255, 0.08); text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                    <span style="position: absolute; left: 0; color: #66ff99; font-weight: bold; font-size: 1.2rem; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">✓</span>
                                    ${precaution}
                                </li>
                            `;
                        });
                        
                        resultHTML += `
                                </ul>
                            </div>
                        `;
                    }

                    // Add healthy_tips section if normal result
                    if (data.healthy_tips && data.healthy_tips.length > 0) {
                        resultHTML += `
                            <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.06); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15);">
                                <h3 style="color: white; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">
                                    💚 Healthy Living Tips
                                </h3>
                                <ul style="list-style: none; padding: 0; margin: 0;">
                        `;
                        
                        data.healthy_tips.forEach(function(tip) {
                            resultHTML += `
                                <li style="color: rgba(255, 255, 255, 0.95); padding: 10px 0 10px 30px; position: relative; font-size: 1rem; line-height: 1.5; border-bottom: 1px solid rgba(255, 255, 255, 0.08); text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                    <span style="position: absolute; left: 0; color: #66ff99; font-weight: bold; font-size: 1.2rem; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">✓</span>
                                    ${tip}
                                </li>
                            `;
                        });
                        
                        resultHTML += `
                                </ul>
                            </div>
                        `;
                    }

                    // Add advice box at the end
                    if (data.advice) {
                        resultHTML += `
                            <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.08); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.25);">
                                <p style="color: white; font-size: 1.05rem; line-height: 1.7; font-style: italic; margin: 0; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">
                                    💡 ${data.advice}
                                </p>
                            </div>
                        `;
                    }

                    resultHTML += `</div>`;
                    
                    $('#result').html(resultHTML);
                }
                
                $('#result').fadeIn(600);
                console.log('Success!');
            },
            error: function(xhr, status, error) {
                // Handle AJAX errors
                $('.loader').hide();
                $('#result').html(`
                    <div style="padding: 20px; background: rgba(255, 107, 107, 0.15); border-radius: 15px; border: 2px solid rgba(255, 107, 107, 0.4);">
                        <h2 style="color: #ff6b6b; margin: 0 0 10px 0; text-shadow: 1px 1px 5px rgba(0,0,0,0.3);">❌ Error</h2>
                        <p style="color: white; margin: 0; font-size: 1.1rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">Failed to process image. Please try again.</p>
                    </div>
                `);
                $('#result').fadeIn(600);
                console.error('Error:', error);
            }
        });
    });

});

// About us navigation
$('#aboutus').click(function () {
    window.location.href = '/aboutus';
});