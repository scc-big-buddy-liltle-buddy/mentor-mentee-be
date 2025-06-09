"""
selfintro_similarity.py

This module provides utility functions to compute the semantic similarity 
between mentor and mentee self-introductions. It includes:

- Extraction of self-introduction text from Mentee and Mentor objects
- Text preprocessing (lowercasing, tokenization, stopword removal)
- Part-of-speech tagging and lemmatization
- Embedding-based semantic similarity scoring using the BGE-M3 model

Dependencies:
- underthesea
- sklearn
- FlagEmbedding
- app.models (Mentee, Mentor)
- app.utils.stopwords (VIET_STOPWORDS)
"""

import string

from sklearn.metrics.pairwise import cosine_similarity
from underthesea import pos_tag, word_tokenize
from FlagEmbedding import BGEM3FlagModel

from app.models import (
    Mentee, Mentor
)

VIET_STOPWORDS = set([
    "có", "của", "trong", "các", "được", "đến", "và", "nhiều", "này", "một",
    "chỉ", "đó", "sẽ", "số", "để", "đã", "ở", "những", "vào", "qua", "đi",
    "không", "là", "ra", "mà", "khi", "rằng", "từ", "năm", "rất", "hay", "tại",
    "sau", "bị", "đều", "vẫn", "lần", "như", "đồng", "mình", "còn", "xảy", "đợt",
    "theo", "hiện", "tuy nhiên", "10", "gì", "tới", "lại", "về", "2"
])

def extract_selfintro(mentee:Mentee, mentor:Mentor): 
    mentee_selfintro = mentee.bio.selfIntroduction
    mentor_selfintro = mentor.bio.selfIntroduction
    return mentee_selfintro, mentor_selfintro

def clean_and_tokenize(mentee_intro, mentor_intro):
    mentee_intro = mentee_intro.lower()
    mentor_intro = mentor_intro.lower()

    mentee_tokenized = word_tokenize(mentee_intro)
    mentor_tokenized = word_tokenize(mentor_intro)

    mentee_tokenized = [word for word in mentee_tokenized if word not in string.punctuation]
    mentor_tokenized = [word for word in mentor_tokenized if word not in string.punctuation]
    
    filtered_mentee = [word for word in mentee_tokenized if word not in VIET_STOPWORDS]
    filtered_mentor = [word for word in mentor_tokenized if word not in VIET_STOPWORDS]

    pos_tags_mentee = pos_tag(' '.join(filtered_mentee))
    pos_tags_mentor = pos_tag(' '.join(filtered_mentor))

    lemmatized_mentee = [word for word, pos in pos_tags_mentee]
    lemmatized_mentor = [word for word, pos in pos_tags_mentor]

    return lemmatized_mentee, lemmatized_mentor

def semantic_similarity(cleaned_mentee, cleaned_mentor):
    model = BGEM3FlagModel('BAAI/bge-m3',  
                       use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation
    embeddings_1 = model.encode(cleaned_mentee, 
                            batch_size=12, 
                            max_length=6000, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
                            )['dense_vecs']
    embeddings_2 = model.encode(cleaned_mentor)['dense_vecs']
    similarity_matrix = cosine_similarity(embeddings_1, embeddings_2)
    return similarity_matrix

def calculateSelfIntroScore(mentee:Mentee, mentor:Mentor): 
    mentee_intro, mentor_intro = extract_selfintro(mentor, mentee)
    print(f"Mentee Intro: {mentee_intro}")
    print(f"Mentor Intro: {mentor_intro}")

    cleaned_mentee, cleaned_mentor= clean_and_tokenize(mentee_intro, mentor_intro)
    print(f"Cleaned/Tokenized Mentee Intro: {cleaned_mentee}")
    print(f"Cleaned/Tokenzied Mentor Intro: {cleaned_mentor}")

    semantic_score_matrix = semantic_similarity(cleaned_mentee, cleaned_mentor)

    # make vector into score
    semantic_score = float(cosine_similarity(
        [semantic_score_matrix.mean(axis=1)],
        [semantic_score_matrix.mean(axis=0)]
    )[0][0])
    print(f"Semantic Score (Cos Similarity): {semantic_score}")

    return semantic_score
