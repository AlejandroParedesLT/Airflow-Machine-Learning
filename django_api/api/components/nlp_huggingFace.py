import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
import pandas as pd
from peft import PeftModel ### Nueva libreria
import json
from unidecode import unidecode

#model_path = '/opt/airflow/dags/model_distilbert_nps_spanish_2.pth'
#m_time = os.path.getmtime(model_path)

class DistillBERTClass(torch.nn.Module):
    def __init__(self):
        super(DistillBERTClass, self).__init__()
        self.path_json = rf'./ml_model/ganabert/labels_classes.json'
        self.data = json.load(open(self.path_json))
        self.id2label = self.data[0]['11cl']['id2label']
        self.label2id = self.data[0]['11cl']['label2id']
        self.general_model_path = './ml_model/distilbert/distilbert-base-spanish-uncased'
        self.model_checkpoint_11 = './ml_model/ganabert/checkpoint-18460'
        self.model = AutoModelForSequenceClassification.from_pretrained(self.general_model_path, num_labels=len(self.id2label), id2label=self.id2label, label2id=self.label2id, local_files_only=True)
        self.model = PeftModel.from_pretrained(self.model, self.model_checkpoint_11)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_checkpoint_11, add_prefix=True)

    def forward(self, input_ids, attention_mask):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output
    
    
    def normalizar_remplazar(self, text):
        my_dictionary = {
            'x': 'por',
            'q': 'que',
            'xq': 'porque',
            'atencioa': 'atencion',
            'rralidad': 'realidad'
        }

        if text is not None:
            text = str(text)
            text = text.lower()
            text = unidecode(text)
            words = text.split()
            replaced_words = [my_dictionary.get(word, word) for word in words]
            replaced_text = ' '.join(replaced_words)
        else: replaced_text = ''
        return replaced_text


    def predict(self, text):
        inputs = self.tokenizer.encode(text, return_tensors='pt').to('cpu')
        with open('./ml_model/distilbert/version.txt', encoding='utf8') as f:
            for line in f:
                version = line.strip()
        with torch.no_grad():
            output = self.model(inputs).logits
            prediction = torch.max(output, 1).indices
        return prediction.tolist()[0], output, version