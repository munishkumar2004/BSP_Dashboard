import httpx
from groq import Groq
from decouple import config

def generate_ai_summary(analyzer):
    api_key = config('GROQ_API_KEY', default='')
    if not api_key:
        return "AI summary unavailable: API Key missing in .env file."

    # 🟢 FIX: Timeout add karo taaki API slow ho toh server hang na ho
    # verify=False abhi local Mac ke liye rakha hai, deployment par isko True kar dena
    http_client = httpx.Client(timeout=15.0, verify=False) 
    
    try:
        client = Groq(api_key=api_key, http_client=http_client)
        num_rows = len(analyzer.df)
        cols = list(analyzer.df.columns)
        data_info = f"Dataset has {num_rows} rows and columns: {', '.join(cols[:10])}"
        prompt = f"Analyze this dataset and give a short professional summary in 3-4 lines: {data_info}"

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
        )
        return response.choices[0].message.content
        
    except Exception as e:
        # 🟢 FIX: Graceful Fallback (Crash hone ki jagah error message dikhao)
        return f"AI summary temporarily unavailable. Please try again later. (Error: {str(e)[:50]})"
    finally:
        http_client.close()