from pathlib import Path
import re


def convert_line(previous:str, current: str):
    html_line = current
    # headers
    if re.match(r'^#{1,6}\ ', current):
        count = current.count('#')
        html_line = f'<h{count}>{current[count + 1:]}</h{count}>'
    # tags
    if re.match(r'^%%C', current):
        html_line = ""
        for token in current.split():
            html_line += f'<a href="{token[3:].lower()}.html">{token[3:]}</a>\n'
        html_line += "<br>"
    # images
    if re.match(r'^!.*\[.*\].*\((.*)\)', current):
        path = re.match(r'^!.*\[.*\].*\((.*)\)', current).group(1)
        html_line = f'<img src="{path}" width="60%">\n<br>\n<br>'
    # quantity
    if re.match(r'^%%Q\ (.*?)([0-9]{1,})(.*)$', current):
        m = re.match(r'^%%Q\ (.*?)([0-9]{1,})(.*)$', current)
        html_line = f'{m.group(1)}<input id="scale" type="number" oninput="scale()" style="width: 45px;" value={m.group(2)} data-original={m.group(2)}></input>{m.group(3)}<br>'
    # continuing ulist
    if  re.match(r'^-\ ', current):
        html_line = f'  <li>{current[2:]}</li>'
    # continuing olist
    if re.match(r'^[0-9]*\.\ ', current):
        html_line = f'  <li>{current[2:]}</li>'

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
    
    return html_line

def replace_quantities(html_string: str):
    m = re.search(r'%([0-9]{1,})%', html_string)
    while m:
        html_string = html_string[:m.span()[0]] + \
        f'<span class="quantity" data-original={m.group(1)}>{m.group(1)}</span>'+ \
        html_string[m.span()[1]:]
        m = re.search(r'%([0-9]{0,}\.{0,1}[0-9]{0,})%', html_string)
    return html_string

def md_to_html(file_name):
    
    html_string = '''<head>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="content">
'''
    with open(Path(file_name), encoding='utf-8') as f:
        old_line = ''
        for line in f.readlines():
            html_string += convert_line(old_line.strip(), line.strip()) + '\n'
            old_line = line

    html_string += '''<script>
    function scale() {
        scale_element = document.getElementById("scale")
        const scale = scale_element.value / scale_element.getAttribute("data-original");
        qs = document.getElementsByClassName("quantity")
        for (var i = 0; i < qs.length; i++) {
            qs[i].innerText = (Number(qs[i].getAttribute("data-original")) * scale).toFixed(1);
        };
    }
</script>
</div>
</body>'''

    html_string = replace_quantities(html_string)
    
    with open(Path(file_name).stem + ".html", 'w', encoding='utf-8') as f:
        f.write(html_string)
        
if __name__ == "__main__":
    md_to_html("cookie.md")
