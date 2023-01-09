from bs4 import BeautifulSoup
import requests
import pandas as pd

detailed_tags = ['ul', 'ol', 'li', 'div', 'ul']
ignore_tags = ['strong', 'u', 'i', 'em']


def findTags(tag, file):
    
    '''BeautifulSoup 4 for scraping and arranging a list of texts and save into a file.'''

    el = tag.find_all(recursive=False)
    if(len(el)==0 or not verify(el)):
        file.write(tag.text+"\n")
        next_tag_recursed = tag.next_sibling.string if(tag.next_sibling != None and 
                                (tag.next_sibling == '\n' or not verify([tag.next_sibling]))) else ''
        file.write(next_tag_recursed)
        return

    main_text = ""
    for child_el in range(0, len(el)):
        if(el[child_el].name in detailed_tags):

            file.write(main_text)
            main_text = ""
            findTags(el[child_el], file)

            next_tag_recursed_1 = el[child_el].next_sibling.string if(el[child_el].next_sibling != None and 
                (el[child_el].next_sibling == '\n' or not verify([el[child_el].next_sibling]))) else ''
            file.write(next_tag_recursed_1)
        else:
            if(el[child_el].name in ignore_tags):

                if(child_el == 0):
                    main_text += el[child_el].previous_sibling.string if(el[child_el].previous_sibling != None and 
                    (el[child_el].previous_sibling == '\n' or not verify([el[child_el].previous_sibling]))) else ''

                main_text += el[child_el].text
                main_text += el[child_el].next_sibling.string if(el[child_el].next_sibling != None and 
                            (el[child_el].next_sibling == '\n' or not verify([el[child_el].next_sibling]))) else ''



def verify(el_tags):
    for i in el_tags:
        if(i.name in detailed_tags):
            return True
    return False

def process():
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    df = pd.read_excel('Input.xlsx')

    for index in range(0, len(df)):
        html_url = requests.get(df.iloc[index]["URL"], headers=agent).text
        soup = BeautifulSoup(html_url, 'html.parser')
        content = soup.find("div", class_="td-post-content")
        
        if(content != None):
            content = BeautifulSoup(''.join(str(r) for r in content), 'html.parser')
            all_tags = content.find_all(recursive=False)
            
            for tag in range(0, len(all_tags)):

                with open("files/{}.txt".format(df['URL_ID'][index]), "a", encoding='utf8') as f:
                    if(all_tags[tag].name == "pre"):
                        continue                   
                    
                    prev_tag = all_tags[tag].previous_sibling.string if(all_tags[tag].previous_sibling != None and 
                                (all_tags[tag].previous_sibling == '\n' or not verify([all_tags[tag].previous_sibling]))) else None
                    f.write(prev_tag)
                    findTags(all_tags[tag], f)

                    if(tag == len(all_tags) - 1):
                        next_tag = all_tags[tag].next_sibling.string if(all_tags[tag].next_sibling != None and 
                                    (all_tags[tag].next_sibling == '\n' or not verify([all_tags[tag].next_sibling]))) else None         
                        f.write(next_tag)
            
        else:
            print(df.iloc[index]["URL_ID"])

process()