import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModel
import math

# Basic cosine similarity calculation with additional distance measures
class CosineSimilarityBasic:
    @staticmethod
    def calculate(buffer1: List[float], buffer2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(buffer1, buffer2)
        norm_buffer1 = np.linalg.norm(buffer1)
        norm_buffer2 = np.linalg.norm(buffer2)
        return dot_product / (norm_buffer1 * norm_buffer2)

    @staticmethod
    def angular_distance(buffer1: List[float], buffer2: List[float]) -> float:
        """Calculate the angular distance between two vectors."""
        cosine_sim = CosineSimilarityBasic.calculate(buffer1, buffer2)
        return math.acos(min(max(cosine_sim, -1.0), 1.0)) / math.pi

    @staticmethod
    def cosine_distance(buffer1: List[float], buffer2: List[float]) -> float:
        """Calculate cosine distance between two vectors."""
        return 1 - CosineSimilarityBasic.calculate(buffer1, buffer2)

    @staticmethod
    def euclidean_distance(buffer1: List[float], buffer2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        return np.linalg.norm(np.array(buffer1) - np.array(buffer2))

    @staticmethod
    def manhattan_distance(buffer1: List[float], buffer2: List[float]) -> float:
        """Calculate Manhattan (taxicab) distance between two vectors."""
        return np.sum(np.abs(np.array(buffer1) - np.array(buffer2)))

# TF-IDF Vectorizer
class TfidfWordVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def convert(self, words: List[str]) -> List[float]:
        """Convert a list of words into a TF-IDF vector."""
        tfidf_matrix = self.vectorizer.fit_transform(words)
        return tfidf_matrix.toarray().tolist()[0]

# GloVe Word Embedding Vectorizer (uses pre-loaded vectors)
class GloveWordVectorizer:
    def __init__(self, glove_file: str = "glove.6B.50d.txt"):
        self.embeddings = self._load_glove_embeddings(glove_file)

    def _load_glove_embeddings(self, file_path: str) -> Dict[str, np.ndarray]:
        """Load GloVe word vectors from file."""
        glove_dict = {}
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                split_line = line.split()
                word = split_line[0]
                embedding = np.array([float(val) for val in split_line[1:]])
                glove_dict[word] = embedding
        return glove_dict

    def convert(self, words: List[str]) -> List[float]:
        """Convert words into GloVe vectors."""
        vectors = []
        for word in words:
            if word in self.embeddings:
                vectors.append(self.embeddings[word])
            else:
                raise ValueError(f"Word '{word}' not found in GloVe embeddings.")
        # Return average of the word vectors
        return np.mean(vectors, axis=0).tolist()

# Hugging Face BERT/Transformer Vectorizer
class HuggingFaceWordVectorizer:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def convert(self, sentence: str) -> List[float]:
        """Convert a sentence into a word embedding using a transformer model."""
        inputs = self.tokenizer(sentence, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

# Main handler to compute cosine similarity and other distances for word lists
class CosineSimilarityWithWords:
    def __init__(self, vectorizer: Optional[object] = None):
        if vectorizer is None:
            raise ValueError("A valid vectorizer must be provided.")
        self.vectorizer = vectorizer

    def calculate(self, words1: List[str], words2: List[str], metric: str = "cosine_similarity") -> float:
        """Calculate similarity or distance between two lists of words."""
        try:
            vector1 = self.vectorizer.convert(words1)
            vector2 = self.vectorizer.convert(words2)

            if metric == "cosine_similarity":
                return CosineSimilarityBasic.calculate(vector1, vector2)
            elif metric == "angular_distance":
                return CosineSimilarityBasic.angular_distance(vector1, vector2)
            elif metric == "cosine_distance":
                return CosineSimilarityBasic.cosine_distance(vector1, vector2)
            elif metric == "euclidean_distance":
                return CosineSimilarityBasic.euclidean_distance(vector1, vector2)
            elif metric == "manhattan_distance":
                return CosineSimilarityBasic.manhattan_distance(vector1, vector2)
            else:
                raise ValueError(f"Unknown metric: {metric}")
        except Exception as e:
            raise ValueError(f"Error during similarity calculation: {e}")

"""
# TF-IDF Example:
tfidf_vectorizer = TfidfWordVectorizer()
cosine_tfidf = CosineSimilarityWithWords(vectorizer=tfidf_vectorizer)
similarity = cosine_tfidf.calculate(["apple", "banana", "fruit"], ["fruit", "apple", "orange"], metric="cosine_similarity")
print(f"Cosine Similarity (TF-IDF): {similarity}")

# Angular Distance Example:
angular_distance = cosine_tfidf.calculate(["apple", "banana", "fruit"], ["fruit", "apple", "orange"], metric="angular_distance")
print(f"Angular Distance (TF-IDF): {angular_distance}")

# Cosine Distance Example:
cosine_distance = cosine_tfidf.calculate(["apple", "banana", "fruit"], ["fruit", "apple", "orange"], metric="cosine_distance")
print(f"Cosine Distance (TF-IDF): {cosine_distance}")

# Euclidean Distance Example:
euclidean_distance = cosine_tfidf.calculate(["apple", "banana", "fruit"], ["fruit", "apple", "orange"], metric="euclidean_distance")
print(f"Euclidean Distance (TF-IDF): {euclidean_distance}")

# Manhattan Distance Example:
manhattan_distance = cosine_tfidf.calculate(["apple", "banana", "fruit"], ["fruit", "apple", "orange"], metric="manhattan_distance")
print(f"Manhattan Distance (TF-IDF): {manhattan_distance}")
"""
