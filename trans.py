from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Initialize the model and tokenizer
model_name = "facebook/mbart-large-50-many-to-one-mmt"
model = MBartForConditionalGeneration.from_pretrained(model_name)
tokenizer = MBart50TokenizerFast.from_pretrained(model_name)

# Set the target language to English
tokenizer.src_lang = "en_XX"

# Function for translation
def translate_text(text, source_language_code):
    # Prepare the tokenizer for the source language
    tokenizer.src_lang = source_language_code

    # Tokenize and translate
    inputs = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**inputs)

    # Decode the translation
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return translated_text

# Translate sample text from Telugu, Hindi, and Marathi
telugu_text = "మీరు ఎలా ఉన్నారు?"
hindi_text = "आप कैसे हैं?"
marathi_text = "तुम्ही कसे आहात?"

print("Telugu to English:", translate_text(telugu_text, "te_IN"))
print("Hindi to English:", translate_text(hindi_text, "hi_IN"))
print("Marathi to English:", translate_text(marathi_text, "mr_IN"))
