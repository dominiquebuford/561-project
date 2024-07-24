from sentence_transformers import SentenceTransformer, util
import numpy as np

def calc_cosine_similarity(sentence1, sentence2):
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    embedding_1 = model.encode(sentence1, convert_to_numpy=True)
    embedding_2 = model.encode(sentence2, convert_to_numpy= True)
    cosine_sim = util.pytorch_cos_sim(embedding_1, embedding_2).item()
    return cosine_sim

if __name__ == "__main__":
    with open("evaluation.txt", 'r') as file:
        for line in file:
            lineList = line.split(',')
            cosine_sim = calc_cosine_similarity(lineList[0], lineList[1])
            print(cosine_sim)