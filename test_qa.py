import requests
import json
import psycopg2
from news_embedding import search_similar_news

def test_question_answering():
    """Test the question-answering functionality with Gemma3:12b"""
    print("===== Testing NBA Question-Answering System =====")
    
    # Sample question - use something that's more likely to match our existing articles
    question = "Tell me about Deandre Ayton joining the Lakers"
    print(f"\nQuestion: {question}")
    
    # Step 1: Find relevant articles using vector search
    print("\nStep 1: Finding relevant articles...")
    # Lower the similarity threshold to find more articles
    results = search_similar_news(question, top_k=3, similarity_threshold=0.3)
    
    if not results:
        print("No relevant articles found.")
        return
    
    print(f"Found {len(results)} relevant articles:")
    
    # Step 2: Compile context from relevant articles
    context = ""
    for i, (news_id, title, date, source, author, similarity) in enumerate(results):
        print(f"  {i+1}. {title} (similarity: {similarity:.2f})")
        
        # Fetch the content
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT "Content" FROM "NBA"."News" WHERE "NewsID" = %s
        """, (news_id,))
        content = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        # Add to context
        context += f"\nARTICLE {i+1}: {title}\n{content}\n"
    
    # Step 3: Get answer from Gemma model
    print("\nStep 3: Generating answer with Gemma3:12b...")
    
    url = "http://localhost:11434/api/generate"
    
    # Create a prompt that instructs the model to answer based on the context
    prompt = f"""You are an NBA expert assistant. Answer the following question based ONLY on the context provided.
If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer that question."

Question: {question}

Context:
{context}

Answer:"""
    
    payload = {
        "model": "gemma3:12b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            answer = response.json()["response"].strip()
            print("\nAnswer:")
            print(answer)
        else:
            print(f"Error: Failed to get response from AI model. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception during answer generation: {e}")

if __name__ == "__main__":
    test_question_answering() 