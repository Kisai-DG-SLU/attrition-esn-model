import google.generativeai as genai

genai.configure(api_key="AIzaSyCNuxa3nwKr-WXM6RWDpuHx7QJJVAbV0DA")

print("Liste des modèles disponibles :")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
