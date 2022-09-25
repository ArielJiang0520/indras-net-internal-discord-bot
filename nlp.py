from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import google_api

def search_query(raw_text, query):
    """
    vectorizer: TfIdfVectorizer model
    docs_tfidf: tfidf vectors for all docs
    query: query doc

    return: cosine similarity between query and all docs
    """
    vectorizer = TfidfVectorizer()
    docs = google_api.parse_doc(raw_text)
    docs_tfidf = vectorizer.fit_transform(docs)
    query_tfidf = vectorizer.transform([query])

    matrix = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    res = []
    for i in sorted(range(len(matrix)), key=lambda x: matrix[x], reverse=True)[:3]:
        if matrix[i]: 
            res.append(docs[i] if len(docs[i]) < 200 else docs[i][:200] + '...')
    return res

def parse_doc(raw_text):
    lines = raw_text.split('\n')
    answers = []
    questions = []
    recording_answer = False
    for line in lines:
        if line == '':
            recording_answer = False
        elif 'Q:' in line:
            questions.append(line)
        elif 'A:' in line:
            answers.append([])
            answers[-1].append(line)
            recording_answer = True
        elif recording_answer:
            answers[-1].append(line)
        
    answers = [ ' '.join(a_list) for a_list in answers]
    return [ q+' '+a for (q, a) in zip(questions, answers)]
    
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import os
    QUESTION_DOC = os.getenv('QUESTION_DOC_ID')

    question_doc = google_api.get_raw_text_from_doc(QUESTION_DOC)
    all_docs = google_api.parse_doc(question_doc)

    search_query(all_docs, 'node')