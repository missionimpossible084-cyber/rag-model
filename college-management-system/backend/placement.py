import json
import pickle
from pathlib import Path

import pandas as pd

from google import genai

from .config import (
    GEMINI_API_KEY,
    LLM_MODEL,
    MODEL_DIR
)


# --------------------------------------------------
# Load model files
# --------------------------------------------------

def load_pickle(filename):

    path = MODEL_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found: {path}"
        )

    with open(path, "rb") as file:
        return pickle.load(file)


placement_model = load_pickle(
    "placement_predict.pkl"
)

scaler = load_pickle(
    "scaler.pkl"
)

label_encoders = load_pickle(
    "labelencoders.pkl"
)

target_encoder = load_pickle(
    "target_encoder.pkl"
)


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# --------------------------------------------------
# Model feature order
# --------------------------------------------------

NUM_COLS = [
    "age",
    "cgpa",
    "internships_count",
    "projects_count",
    "certifications_count"
]


FEATURE_ORDER = [
    "age",
    "gender",
    "cgpa",
    "branch",
    "internships_count",
    "projects_count",
    "certifications_count"
]


# --------------------------------------------------
# Extract placement information
# --------------------------------------------------

def extract_placement_data(user_message):

    prompt = f"""
Extract placement prediction information from
the student's message.

Return ONLY valid JSON.

Required fields:

age
gender
cgpa
branch
internships_count
projects_count
certifications_count

If a value is not present, use null.

Do not guess missing values.

Student message:
{user_message}

Example JSON format:

{{
    "age": 21,
    "gender": "Male",
    "cgpa": 8.2,
    "branch": "CSE",
    "internships_count": 2,
    "projects_count": 4,
    "certifications_count": 3
}}
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown JSON fences if Gemini returns them
    if text.startswith("```"):
        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

    try:
        data = json.loads(text)

    except json.JSONDecodeError:

        raise ValueError(
            "Could not understand the placement information."
        )

    return data


# --------------------------------------------------
# Validate categorical value
# --------------------------------------------------

def find_encoder_value(
    encoder,
    value
):

    if value is None:
        return None

    value = str(value).strip()

    classes = list(
        encoder.classes_
    )

    for class_value in classes:

        if str(class_value).lower() == value.lower():
            return class_value

    return None


# --------------------------------------------------
# Validate extracted information
# --------------------------------------------------

def validate_placement_data(data):

    missing = []

    for field in FEATURE_ORDER:

        value = data.get(field)

        if value is None or str(value).strip() == "":
            missing.append(field)

    if missing:
        return False, missing, data

    # Gender
    gender_value = find_encoder_value(
        label_encoders["gender"],
        data["gender"]
    )

    if gender_value is None:

        valid_values = [
            str(x)
            for x in label_encoders["gender"].classes_
        ]

        raise ValueError(
            "Invalid gender. "
            f"Use one of: {', '.join(valid_values)}"
        )

    data["gender"] = gender_value

    # Branch
    branch_value = find_encoder_value(
        label_encoders["branch"],
        data["branch"]
    )

    if branch_value is None:

        valid_values = [
            str(x)
            for x in label_encoders["branch"].classes_
        ]

        raise ValueError(
            "Invalid branch. "
            f"Use one of: {', '.join(valid_values)}"
        )

    data["branch"] = branch_value

    return True, [], data


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def predict_placement(data):

    input_df = pd.DataFrame(
        [data]
    )

    # Correct feature order
    input_df = input_df[
        FEATURE_ORDER
    ]

    # Encode categorical columns
    input_df["gender"] = (
        label_encoders["gender"]
        .transform(
            input_df["gender"]
        )
    )

    input_df["branch"] = (
        label_encoders["branch"]
        .transform(
            input_df["branch"]
        )
    )

    # Scale only numerical columns
    input_df[NUM_COLS] = scaler.transform(
        input_df[NUM_COLS]
    )

    # Prediction
    prediction = placement_model.predict(
        input_df
    )[0]

    # Decode target
    try:

        decoded_prediction = (
            target_encoder
            .inverse_transform(
                [prediction]
            )[0]
        )

    except Exception:

        decoded_prediction = prediction

    prediction_text = str(
        decoded_prediction
    )

    # Normalize result
    if prediction_text.lower() in [
        "1",
        "placed",
        "true",
        "yes"
    ]:

        result = "Placed"

    else:

        result = "Not Placed"

    # Probability if available
    probability = None

    if hasattr(
        placement_model,
        "predict_proba"
    ):

        probabilities = (
            placement_model
            .predict_proba(input_df)[0]
        )

        classes = (
            placement_model.classes_
        )

        for index, class_value in enumerate(
            classes
        ):

            try:

                decoded_class = (
                    target_encoder
                    .inverse_transform(
                        [class_value]
                    )[0]
                )

                if str(
                    decoded_class
                ).lower() in [
                    "1",
                    "placed",
                    "true",
                    "yes"
                ]:

                    probability = (
                        float(
                            probabilities[index]
                        ) * 100
                    )

                    break

            except Exception:
                pass

    return {
        "result": result,
        "raw_prediction": prediction_text,
        "probability": probability
    }


# --------------------------------------------------
# Complete prediction function
# --------------------------------------------------

def process_placement_message(
    user_message
):

    data = extract_placement_data(
        user_message
    )

    valid, missing, data = (
        validate_placement_data(data)
    )

    if not valid:

        return {
            "status": "missing",
            "missing": missing,
            "data": data
        }

    prediction = predict_placement(
        data
    )

    return {
        "status": "success",
        "data": data,
        "prediction": prediction
    }

