from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse
import uvicorn
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from PIL import Image
import io
import numpy as np
import imagehash
import os

# Translation dictionary for class names and disposal tips
TRANSLATIONS = {
    "en": {
        "class_names": {
            "plastic bottle": "plastic bottle",
            "plastic bag": "plastic bag",
            "lithium battery": "lithium battery",
            "aerosol sprays": "aerosol sprays"
        },
        "disposal_tips": {
            "plastic bottle": {
                "disposalTip": "Rinse and place in recycling bin.",
                "badEffect": "Improper disposal contributes to plastic pollution in landfills and oceans.",
                "alternative": "Use reusable water bottles to reduce plastic waste.",
                "creativeReuse": "Repurpose into planters, bird feeders, or storage containers.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=5-MCZm0GWg4",  # DIY plastic bottle crafts
                "profitIdea": "Collect and sell to recycling centers for processing into new plastic products."
            },
            "plastic bag": {
                "disposalTip": "Dispose of by reusing or recycling at designated drop-off points.",
                "badEffect": "Do not burn, as it releases harmful chlorine gas and dioxins, causing air pollution and health issues like respiratory problems.",
                "alternative": "Use cloth or jute bags to reduce plastic use.",
                "creativeReuse": "Transform into woven mats or storage pouches.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=ZpB-HknpOAg",  # Plastic bag weaving tutorial
                "profitIdea": "Sell Collected Bags to Recycling Companies – Collect used plastic bags and sell them directly to recycling plants, where they are shredded, melted, and turned into plastic granules."
            },
            "lithium battery": {
                "disposalTip": "Do not dispose in regular trash; take to designated battery recycling centers.",
                "badEffect": "Improper disposal can lead to fires, explosions, or leakage of toxic chemicals, harming the environment and health.",
                "alternative": "Use rechargeable batteries with proper recycling programs.",
                "creativeReuse": "Donate functional batteries to community programs or repurpose for low-power DIY projects.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=9qP3T5A2cZ8",  # DIY battery repurposing project
                "profitIdea": "Partner with recycling companies to collect and sell used lithium batteries for safe processing."
            },
            "aerosol sprays": {
                "disposalTip": "Ensure cans are completely empty and recycle at designated facilities; check local regulations.",
                "badEffect": "Puncturing or burning can cause explosions and release harmful chemicals into the air.",
                "alternative": "Use pump or non-aerosol alternatives for sprays.",
                "creativeReuse": "Repurpose empty cans as storage containers or art project materials after ensuring they are depressurized.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=6oB6Y3tI41Q",  # Aerosol can repurposing ideas
                "profitIdea": "Collect and sell empty aerosol cans to scrap metal recyclers for profit."
            }
        }
    },
    "hi": {
        "class_names": {
            "plastic bottle": "प्लास्टिक की बोतल",
            "plastic bag": "प्लास्टिक की थैली",
            "lithium battery": "लिथियम बैटरी",
            "aerosol sprays": "एरोसोल स्प्रे"
        },
        "disposal_tips": {
            "plastic bottle": {
                "disposalTip": "कुल्ला करें और रीसाइक्लिंग बिन में डालें।",
                "badEffect": "अनुचित निपटान से लैंडफिल और समुद्र में प्लास्टिक प्रदूषण बढ़ता है।",
                "alternative": "प्लास्टिक कचरे को कम करने के लिए पुन: उपयोग योग्य पानी की बोतलें उपयोग करें।",
                "creativeReuse": "प्लांटर्स, बर्ड फीडर, या स्टोरेज कंटेनर के रूप में पुन: उपयोग करें।",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=5-MCZm0GWg4",  # Same video (language-agnostic)
                "profitIdea": "रीसाइक्लिंग केंद्रों को इकट्ठा करें और बेचें ताकि नए प्लास्टिक उत्पादों में संसाधित किया जा सके।"
            },
            "plastic bag": {
                "disposalTip": "पुन: उपयोग करें या निर्दिष्ट ड्रॉप-ऑफ पॉइंट्स पर रीसाइक्लिंग करें।",
                "badEffect": "जलाएं नहीं, क्योंकि यह हानिकारक क्लोरीन गैस और डाइऑक्सिन छोड़ता है, जिससे वायु प्रदूषण और श्वसन समस्याओं जैसी स्वास्थ्य समस्याएं होती हैं।",
                "alternative": "प्लास्टिक के उपयोग को कम करने के लिए कपड़े या जूट के थैले का उपयोग करें।",
                "creativeReuse": "बुने हुए मैट या स्टोरेज पाउच में बदलें।",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=ZpB-HknpOAg",  # Same video
                "profitIdea": "रीसाइक्लिंग सेंटरों को बेचें या पुन: उपयोग योग्य शॉपिंग बैग जैसे विपणन योग्य उत्पादों में बनाएं।"
            },
            "lithium battery": {
                "disposalTip": "नियमित कचरे में न फेंकें; निर्दिष्ट बैटरी रीसाइक्लिंग केंद्रों में ले जाएं।",
                "badEffect": "अनुचित निपटान से आग, विस्फोट या जहरीले रसायनों का रिसाव हो सकता है, जो पर्यावरण और स्वास्थ्य को नुकसान पहुंचाता है।",
                "alternative": "उचित रीसाइक्लिंग कार्यक्रमों के साथ रिचार्जेबल बैटरी का उपयोग करें।",
                "creativeReuse": "कार्यात्मक बैटरी को सामुदायिक कार्यक्रमों में दान करें या कम-शक्ति वाले DIY प्रोजेक्ट्स के लिए पुन: उपयोग करें।",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=9qP3T5A2cZ8",  # Same video
                "profitIdea": "रीसाइक्लिंग कंपनियों के साथ साझेदारी करके उपयोग की गई लिथियम बैटरी एकत्र करें और बेचें।"
            },
            "aerosol sprays": {
                "disposalTip": "सुनिश्चित करें कि डिब्बे पूरी तरह से खाली हैं और निर्दिष्ट सुविधाओं पर रीसाइक्लिंग करें; स्थानीय नियमों की जांच करें।",
                "badEffect": "छेद करने या जलाने से विस्फोट हो सकता है और हानिकारक रसायन हवा में निकल सकते हैं।",
                "alternative": "स्प्रे के लिए पंप या गैर-एरोसोल विकल्पों का उपयोग करें।",
                "creativeReuse": "खाली डिब्बों को सुनिश्चित करने के बाद भंडारण कंटेनर या कला परियोजना सामग्री के रूप में पुन: उपयोग करें।",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=6oB6Y3tI41Q",  # Same video
                "profitIdea": "खाली एरोसोल डिब्बों को स्क्रैप धातु रीसाइक्लर्स को बेचकर लाभ कमाएं।"
            }
        }
    },
    "kn": {
        "class_names": {
            "plastic bottle": "ಪ್ಲಾಸ್ಟಿಕ್ ಬಾಟಲ್",
            "plastic bag": "ಪ್ಲಾಸ್ಟಿಕ್ ಚೀಲ",
            "lithium battery": "ಲಿಥಿಯಂ ಬ್ಯಾಟರಿ",
            "aerosol sprays": "ಏರೋಸಾಲ್ ಸ್ಪ್ರೇ"
        },
        "disposal_tips": {
            "plastic bottle": {
                "disposalTip": "ತೊಳೆದು ಮರುಬಳಕೆ ಬಿನ್‌ಗೆ ಹಾಕಿ.",
                "badEffect": "ಅನುಚಿತ ವಿಲೇವಾರಿಯಿಂದ ಭೂಕುಸಿತ ಮತ್ತು ಸಮುದ್ರದಲ್ಲಿ ಪ್ಲಾಸ್ಟಿಕ್ ಮಾಲಿನ್ಯ ಹೆಚ್ಚಾಗುತ್ತದೆ.",
                "alternative": "ಪ್ಲಾಸ್ಟಿಕ್ ಕಸವನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಮರುಬಳಕೆಯ ಜಲದ ಬಾಟಲಿಗಳನ್ನು ಬಳಸಿ.",
                "creativeReuse": "ಪ್ಲಾಂಟರ್‌ಗಳು, ಪಕ್ಷಿಗಳ ಆಹಾರಕಾರಕ, ಅಥವಾ ಸಂಗ್ರಹಣೆ ಕಂಟೇನರ್‌ಗಳಾಗಿ ಮರುಬಳಕೆ ಮಾಡಿ.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=5-MCZm0GWg4",  # Same video
                "profitIdea": "ಮರುಬಳಕೆ ಕೇಂದ್ರಗಳಿಗೆ ಸಂಗ್ರಹಿಸಿ ಮತ್ತು ಮಾರಾಟ ಮಾಡಿ, ಇದನ್ನು ಹೊಸ ಪ್ಲಾಸ್ಟಿಕ್ ಉತ್ಪನ್ನಗಳಾಗಿ ಸಂಸ್ಕರಿಸಬಹುದು."
            },
            "plastic bag": {
                "disposalTip": "ಮರುಬಳಕೆ ಮಾಡಿ ಅಥವಾ ನಿಗದಿತ ಡ್ರಾಪ್-ಆಫ್ ಪಾಯಿಂಟ್‌ಗಳಲ್ಲಿ ಮರುಬಳಕೆಗೆ ಒಡ್ಡಿ.",
                "badEffect": "ಸುಡಬೇಡಿ, ಏಕೆಂದರೆ ಇದು ಹಾನಿಕಾರಕ ಕ್ಲೋರಿನ್ ಗ್ಯಾಸ್ ಮತ್ತು ಡಯಾಕ್ಸಿನ್‌ಗಳನ್ನು ಬಿಡುಗಡೆ ಮಾಡುತ್ತದೆ, ಇದರಿಂದ ವಾಯು ಮಾಲಿನ್ಯ ಮತ್ತು ಉಸಿರಾಟದ ಸಮಸ್ಯೆಗಳಂತಹ ಆರೋಗ್ಯ ಸಮಸ್ಯೆಗಳು ಉಂಟಾಗುತ್ತವೆ.",
                "alternative": "ಪ್ಲಾಸ್ಟಿಕ್ ಬಳಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಬಟ್ಟೆ ಅಥವಾ ಜೂಟ್ ಚೀಲಗಳನ್ನು ಬಳಸಿ.",
                "creativeReuse": "ನೇಯ್ದ ಮ್ಯಾಟ್‌ಗಳು ಅಥವಾ ಸಂಗ್ರಹಣೆ ಪೌಚ್‌ಗಳಾಗಿ ಪರಿವರ್ತಿಸಿ.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=ZpB-HknpOAg",  # Same video
                "profitIdea": "ಮರುಬಳಕೆ ಕೇಂದ್ರಗಳಿಗೆ ಮಾರಾಟ ಮಾಡಿ ಅಥವಾ ಮರುಬಳಕೆ ಶಾಪಿಂಗ್ ಬ್ಯಾಗ್‌ಗಳಂತಹ ಮಾರಾಟಕ್ಕೆ ಯೋಗ್ಯ ಉತ್ಪನ್ನಗಳಾಗಿ ರೂಪಿಸಿ."
            },
            "lithium battery": {
                "disposalTip": "ನಿಯಮಿತ ಕಸದೊಂದಿಗೆ ವಿಲೇವಾರಿ ಮಾಡಬೇಡಿ; ನಿಗದಿತ ಬ್ಯಾಟರಿ ಮರುಬಳಕೆ ಕೇಂದ್ರಗಳಿಗೆ ತೆಗೆದುಕೊಂಡು ಹೋಗಿ.",
                "badEffect": "ಅನುಚಿತ ವಿಲೇವಾರಿಯಿಂದ ಬೆಂಕಿ, ಸ್ಫೋಟ ಅಥವಾ ವಿಷಕಾರಿ ರಾಸಾಯನಿಕಗಳ ಸೋರಿಕೆಯಾಗಬಹುದು, ಇದು ಪರಿಸರ ಮತ್ತು ಆರೋಗ್ಯಕ್ಕೆ ಹಾನಿಯನ್ನುಂಟುಮಾಡುತ್ತದೆ.",
                "alternative": "ಸರಿಯಾದ ಮರುಬಳಕೆ ಕಾರ್ಯಕ್ರಮಗಳೊಂದಿಗೆ ರೀಚಾರ್ಜ್ ಮಾಡಬಹುದಾದ ಬ್ಯಾಟರಿಗಳನ್ನು ಬಳಸಿ.",
                "creativeReuse": "ಕಾರ್ಯಾತ್ಮಕ ಬ್ಯಾಟರಿಗಳನ್ನು ಸಮುದಾಯ ಕಾರ್ಯಕ್ರಮಗಳಿಗೆ ದಾನ ಮಾಡಿ ಅಥವಾ ಕಡಿಮೆ-ಶಕ್ತಿಯ DIY ಯೋಜನೆಗಳಿಗೆ ಮರುಬಳಕೆ ಮಾಡಿ.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=9qP3T5A2cZ8",  # Same video
                "profitIdea": "ಮರುಬಳಕೆ ಕಂಪನಿಗಳೊಂದಿಗೆ ಸಹಭಾಗಿತ್ವವನ್ನು ಹೊಂದಿ, ಬಳಸಿದ ಲಿಥಿಯಂ ಬ್ಯಾಟರಿಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ ಮತ್ತು ಮಾರಾಟ ಮಾಡಿ."
            },
            "aerosol sprays": {
                "disposalTip": "ಕ್ಯಾನ್‌ಗಳು ಸಂಪೂರ್ಣವಾಗಿ ಖಾಲಿಯಾಗಿರುವುದನ್ನು ಖಚಿತಪಡಿಸಿಕೊಂಡು ನಿಗದಿತ ಸೌಲಭ್ಯಗಳಲ್ಲಿ ಮರುಬಳಕೆ ಮಾಡಿ; ಸ್ಥಳೀಯ ನಿಯಮಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
                "badEffect": "ಕುಟ್ಟುವುದು ಅಥವಾ ಸುಡುವುದರಿಂದ ಸ್ಫೋಟವಾಗಬಹುದು ಮತ್ತು ಹಾನಿಕಾರಕ ರಾಸಾಯನಿಕಗಳು ಗಾಳಿಯಲ್ಲಿ ಬಿಡುಗಡೆಯಾಗಬಹುದು.",
                "alternative": "ಸ್ಪ್ರೇಗಾಗಿ ಪಂಪ್ ಅಥವಾ ಏರೋಸಾಲ್ ಅಲ್ಲದ ವಿಕಲ್ಪಗಳನ್ನು ಬಳಸಿ.",
                "creativeReuse": "ಖಾಲಿಯಾದ ಕ್ಯಾನ್‌ಗಳನ್ನು ಒತ್ತಡರಹಿತಗೊಳಿಸಿದ ನಂತರ ಶೇಖರಣಾ ಕಂಟೇನರ್‌ಗಳು ಅಥವಾ ಕಲಾ ಯೋಜನೆಯ ವಸ್ತುಗಳಾಗಿ ಮರುಬಳಕೆ ಮಾಡಿ.",
                "creativeReuseVideo": "https://www.youtube.com/watch?v=6oB6Y3tI41Q",  # Same video
                "profitIdea": "ಖಾಲಿ ಏರೋಸಾಲ್ ಕ್ಯಾನ್‌ಗಳನ್ನು ಸ್ಕ್ರಾಪ್ ಲೋಹದ ಮರುಬಳಕೆಗಾರರಿಗೆ ಮಾರಾಟ ಮಾಡಿ ಲಾಭ ಗಳಿಸಿ."
            }
        }
    }
}

# Predefined image hashes (loaded dynamically if images exist)
KNOWN_IMAGES = {}

image_files = [
    "plastic_bag1.jpg",
    "plastic_bag2.jpg",
    "plastic_bag3.jpg",
    "plastic_bag4.jpg",
    "plastic_bag5.jpg",
    "plastic_bag6.jpg",
   
    "plastic_bottle1.jpg",
    "lithium_battery1.jpg",
    "lithium_battery2.jpg",
    "lithium_battery3.jpg",
    "lithium_battery4.jpg",
    "lithium_battery5.jpg",
    "lithium_battery6.jpg",
    "lithium_battery7.jpg",
    "aerosol_spray1.jpg",
    "aerosol_spray2.jpg",
    "aerosol_spray3.jpg",
    "aerosol_spray4.jpg",
    "aerosol_spray5.jpg",
    "aerosol_spray6.jpg",
    "aerosol_spray7.jpg",
    "aerosol_spray8.jpg",
    
    "aerosol_spray10.jpg"
]

for img_file in image_files:
    if os.path.exists(img_file):
        try:
            img = Image.open(img_file)
            # Determine class name based on file name prefix
            if img_file.startswith("plastic_bag"):
                class_name = "plastic bag"
            elif img_file.startswith("plastic_bottle"):
                class_name = "plastic bottle"
            elif img_file.startswith("lithium_battery"):
                class_name = "lithium battery"
            elif img_file.startswith("aerosol_spray"):
                class_name = "aerosol sprays"
            else:
                continue  # Skip files that don't match expected prefixes
            KNOWN_IMAGES[str(imagehash.average_hash(img))] = class_name
        except Exception as e:
            print(f"⚠️ Could not load {img_file}: {e}")
    else:
        print(f"⚠️ File not found: {img_file}")

# Load pre-trained MobileNetV2 model and modify classifier
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(len(TRANSLATIONS["en"]["class_names"]), activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# FastAPI app
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "✅ Python model API is running. Use POST /predict"}


# Image preprocessing
def preprocess_image(image):
    image = image.resize((224, 224))
    image = np.array(image) / 127.5 - 1  # Normalize to [-1, 1]
    image = np.expand_dims(image, axis=0)
    return image

def get_image_hash(image):
    return str(imagehash.average_hash(image))

@app.post("/predict")
async def predict(file: UploadFile = File(...), language: str = Query("en", enum=["en", "hi", "kn"])):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Select translation dictionary based on language
        translation = TRANSLATIONS.get(language, TRANSLATIONS["en"])  # Default to English
        class_names = list(translation["class_names"].values())
        disposal_tips = translation["disposal_tips"]

        # Check if the image matches a known image
        image_hash = get_image_hash(image)
        for known_hash, class_name in KNOWN_IMAGES.items():
            if image_hash == known_hash:
                translated_class_name = translation["class_names"][class_name]
                tips = disposal_tips[class_name]
                response_data = {
                    "wasteType": translated_class_name,
                    "confidence": 1.0,  # Full confidence for exact match
                }
                if isinstance(tips, dict):
                    response_data.update(tips)
                else:
                    response_data["disposalTip"] = tips
                return JSONResponse(response_data)

        # If no match, use model prediction
        img_tensor = preprocess_image(image)
        predictions = model.predict(img_tensor)
        predicted_idx = np.argmax(predictions[0])
        predicted_class = list(translation["class_names"].keys())[predicted_idx]
        translated_class_name = translation["class_names"][predicted_class]
        confidence = float(predictions[0][predicted_idx])
        tips = disposal_tips.get(predicted_class, "Sort and dispose according to local waste guidelines.")

        response_data = {
            "wasteType": translated_class_name,
            "confidence": confidence,
        }
        if isinstance(tips, dict):
            response_data.update(tips)
        else:
            response_data["disposalTip"] = tips
        return JSONResponse(response_data)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # use Render's port or fallback to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
