import json, requests, bs4

html_file = requests.get("https://mtgtop8.com/event?e=30456&f=HI#")

parsed_html = bs4.BeautifulSoup(html_file.text, 'html.parser')

text = str(parsed_html)

file_to_save = open("test_page.html", "w+")

file_to_save.write(text)

file_to_save.close()



#print(deck)
