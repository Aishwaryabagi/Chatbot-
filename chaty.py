# Install embedchain
# Create your bot (20 lines of code)
from embedchain import App

# Create a chatbot app
chatbot = App()

# Add your data sources
chatbot.add("pdf_file.pdf")  # or .txt, .docx, YouTube links, websites, etc.
chatbot.add("https://www.youtube.com/watch?v=vWbTwi0aXNM", "https://www.youtube.com/watch?v=7GdwIPx9FWk",)

# Query your chatbot
response = chatbot.query("Your question here")
print(response)