from bs4 import BeautifulSoup
import json
from pathlib import Path
import re


def convert_line(previous:str, current: str):
    html_line = current
    extra = None
    # headers
    if re.match(r'^#{1,6}\ ', current):
        count = current.count('#')
        html_line = f'<h{count}>{current[count + 1:]}</h{count}>'
        if count == 1:
            extra = current[count + 1:]
    
    # tags
    if re.match(r'^%%tag\ .{1,}', current):
        html_line = ""
        extra = []
        for token in current.split()[1:]:
            tag_type = token.split('%%')[0]
            tag_value = token.split('%%')[1]
            extra.append(
                {
                    'type': tag_type,
                    'value': tag_value,
                }
            )
            html_line += f'<a class="category" href="/recipe-site/categories/{tag_value.lower()}.html">{tag_value}</a>\n'
        html_line += "<br>"
    
    # images
    if re.match(r'^!.*\[.*\].*\((.*)\)', current):
        path = re.match(r'^!.*\[.*\].*\((.*)\)', current).group(1)
        html_line = f'<img src="/recipe-site/{path}" width="60%">\n<br>\n<br>'
        extra = path
    
    # quantity
    if re.match(r'^%%Q\ (.*?)([0-9]{1,})(.*)$', current):
        m = re.match(r'^%%Q\ (.*?)([0-9]{1,})(.*)$', current)
        html_line = f'{m.group(1)}<input id="scale" type="number" oninput="scale()" style="width: 45px;" value={m.group(2)} data-original={m.group(2)}></input>{m.group(3)}<br>'
    
    # continuing ulist
    if  re.match(r'^-\ ', current):
        html_line = f'  <li>{current[2:]}</li>'
    
    # continuing olist
    if re.match(r'^[0-9]*\.\ ', current):
        html_line = f'  <li>{current[current.index(" ") + 1:]}</li>'

    
    # start of ulist
    if not re.match(r'^-\ ', previous) and re.match(r'^-\ ', current):
        html_line = '<ul>\n' + html_line 
    
    # end of ulist
    if re.match(r'^-\ ', previous) and not re.match(r'^-\ ', current):
        html_line = '</ul>\n' + html_line
    
    # start of olist
    if not re.match(r'^[0-9]*\.\ ', previous) and re.match(r'^[0-9]*\.\ ', current):
        html_line = '<ol>\n' + html_line  
    
    # end of olist
    if re.match(r'^[0-9]*\.\ ', previous) and not re.match(r'^[0-9]*\.\ ', current):
        html_line = '</ol>\n' + html_line
    
    return (html_line, extra)

def replace_quantities(html_string: str):
    m = re.search(r'%([0-9]{1,})%', html_string)
    while m:
        html_string = html_string[:m.span()[0]] + \
        f'<span class="quantity" data-original={m.group(1)}>{m.group(1)}</span>'+ \
        html_string[m.span()[1]:]
        m = re.search(r'%([0-9]{0,}\.{0,1}[0-9]{0,})%', html_string)
    return html_string

def convert_file(file_name):
    with open('templating.json') as f:
        templating = json.load(f)
    html_string = templating['recipe1']
    metadata = {}
    with open(Path(file_name), encoding='utf-8') as f:
        old_line = ''
        for line in f.readlines() + ['']:
            html_line, extra = convert_line(old_line.strip(), line.strip())
            html_string += html_line + '\n'
            if isinstance(extra, str):
                if extra.lower().endswith(('.jpg', '.jpeg', 'png')):
                    metadata['image'] = metadata['image'] if metadata.get('image', None) else extra
                else:
                    metadata['name'] = extra

            if isinstance(extra, list):
                metadata['tags'] = extra
            old_line = line

    for i in range(len(metadata['tags'])):
        metadata['tags'][i]['recipe'] = metadata['name']
    html_string += templating['recipe2']
    html_string = replace_quantities(html_string)
    
    metadata['file'] = 'recipes/' + Path(file_name).stem + '.html'
    if not metadata.get('image'):
        metadata['image'] = '/static/images/no_image.jpg'

    html_string = BeautifulSoup(html_string, 'html.parser').prettify(formatter='html')
    with open(metadata['file'], 'w', encoding='utf-8') as f:
        f.write(html_string)

    return metadata
        

if __name__ == '__main__':
    m = convert_file(Path('md_recipes', 'pork_stew.md'))
    print(m)
