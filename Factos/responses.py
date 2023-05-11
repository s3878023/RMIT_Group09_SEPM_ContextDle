import random
import requests

def get_response(message: str) -> str:
    p_message = message.lower() 
    
    if p_message == '!help':
       return "I'll write this later OK?"
    
    if p_message == '!fact':   
       limit = 1 
       api_url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(limit)
       response = requests.get(api_url, headers={'X-Api-Key': 'MGhdNiHtsqCGxoEw0mTm0g==byuKJsLbtJr2iqB4'})
       if response.status_code == requests.codes.ok:
         print(response.text)
       else:
         print("Error:", response.status_code, response.text)
       return response.text.replace('[{"fact": "','').replace('"}]','')
       
    