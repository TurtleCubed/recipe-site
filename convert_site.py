from bs4 import BeautifulSoup
from convert import convert_file
import json
from pathlib import Path
import polars as pl


def create_categories_page(df: pl.DataFrame, df_recipes: pl.DataFrame):
    with open(Path('templating.json')) as f:
        templating = json.load(f)
    html_string = templating['head'] + '\n<body>\n' + templating['topnav'] + '\n' + '<div class="content">'
    
    for name, data in df.group_by('type', maintain_order=True):
        html_string += f'<h1>{name[0]}</h1>\n'
        for name1, data1 in data.group_by('value', maintain_order=True):
            html_string += f'<a class="category-list" href="/recipe-site/categories/{name1[0].lower()}.html">{name1[0]}</a> <br>\n'
            create_category_page(data1, df_recipes)
            
    html_string += '\n</div>\n</body>'
    with open(Path('categories.html'), 'w') as f:
        f.write(BeautifulSoup(html_string, 'html.parser').prettify())

def create_category_page(df: pl.DataFrame, df_recipes: pl.DataFrame):
    with open(Path('templating.json')) as f:
        templating = json.load(f)
    html_string = templating['head'] + '\n<body>\n' + templating['topnav'] + '\n' + '<div class="content">'
    html_string += f'<h1>{df.row(0)[1]}</h1>\n<ul id="myUL">\n'
    for row in df.iter_rows():
        recipe = df_recipes.filter(pl.col('name') == row[2]).row(0)
        file = '/recipe-site/' + recipe[2]
        image = '/recipe-site' + recipe[1]
        html_string += f'<li><a href="{file}">{row[2]} <br>\n'
        html_string += f'<img src="{image}" class="thumbnail"> </a> </li><br>\n'

    html_string += '\n</ul>\n<div>\n</body>'
    with open(Path('categories', row[1].lower() + '.html'), 'w') as f:
        f.write(BeautifulSoup(html_string, 'html.parser').prettify())
    # add thumbnail + name + categories for each recipe

def create_index_page(df: pl.DataFrame):
    with open(Path('templating.json')) as f:
        templating = json.load(f)
    html_string = templating['head'] + '\n<body>\n' + templating['topnav'] + '\n'
    html_string += templating['index1']
    for row in df.iter_rows():
        name = row[0]
        image = '/recipe-site' + row[1]
        link = '/recipe-site/' + row[2]
        html_string += f'<li><a href="{link}">{name}<br><img src="{image}" class="thumbnail"></a></li>\n'
    html_string += '</ul>\n</div>\n'
    html_string += templating['search_script'] + '\n</body>'
    with open(Path('index.html'), 'w') as f:
        f.write(BeautifulSoup(html_string, 'html.parser').prettify())


def main():
    md_recipes = Path('md_recipes').glob('**/*.md')
    recipes = pl.DataFrame()
    tags = pl.DataFrame()

    for md_recipe in md_recipes:
        metadata = convert_file(md_recipe)
        recipes = pl.concat([recipes, pl.DataFrame({'name': metadata['name'], 'image': metadata['image'], 'file': metadata['file']})])
        tags = pl.concat([tags, pl.DataFrame(metadata['tags'])])
    # print(recipes.head())
    # print(tags.head())

    # create a page for all categories
    create_categories_page(tags.sort(['type', 'value']), recipes)
    create_index_page(recipes)
    
                

if __name__ == '__main__':
    main()