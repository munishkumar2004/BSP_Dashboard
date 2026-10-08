from groq import Groq
from decouple import config

def generate_ai_summary(analyzer):
    api_key = config('GROQ_API_KEY')
    client = Groq(api_key=api_key)
    
    num_rows = len(analyzer.df)
    cols = list(analyzer.df.columns)
    data_info = f"Dataset has {num_rows} rows and columns: {', '.join(cols[:10])}"
    
    prompt = f"Analyze this dataset and give a short professional summary in 3-4 lines: {data_info}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI summary unavailable: {str(e)[:80]}"