import numpy as np
import os
from pathlib import Path
from ..output.printer import print_prediction
from ..config import MODEL_PATH
import torch
from transformers import BertForSequenceClassification, BertTokenizer
from transformers import logging

class DarkBert:
    model_checkpoint = MODEL_PATH

    def __init__(self) -> None:
        logging.set_verbosity_error()
        # Load the pretrained BERT model and tokenizer (assuming you used BERT for training)
        model_name = 'bert-base-uncased'  # Change this to match the architecture you used during training
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name,num_labels=4,output_attentions=False,
                                                      output_hidden_states=False)
        

        # Load the fine-tuned model checkpoint 
        self.model.load_state_dict(torch.load(self.model_checkpoint, map_location='cpu'))

        # Put the model in evaluation mode
        self.model.eval()

    def predict(self,text):
        input_ids = self.tokenizer.encode(text, add_special_tokens=True, max_length=128, truncation=True, padding='max_length', return_tensors='pt')
        attention_mask = input_ids != self.tokenizer.pad_token_id  # Create attention mask

        # Perform inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Get the predicted class probabilities (logits)
        logits = outputs.logits

        # Convert logits to probabilities using softmax
        probabilities = torch.softmax(logits, dim=1)


        # Get the predicted class label (index with highest probability)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        label_resolver = {0 : 'Drugs', 1: 'Fraud', 2: 'Services', 3 : 'Pedophilia'}
        predicted_label = label_resolver[predicted_class]
        print_prediction(probabilities.squeeze().tolist(),predicted_class,predicted_label,label_resolver)
