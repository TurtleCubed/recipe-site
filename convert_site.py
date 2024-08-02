from bs4 import BeautifulSoup
from convert import convert_file
import json
from pathlib import Path
import polars as pl


def create_categories_page(df: pl.DataFrame, df_recipes: pl.DataFrame):
    with open(Path('templating.json')) as f:
        templating = json.load(f)
    html_string = templating['head'] + "\n<body>\n" + templating['topnav'] + "\n"
    
    for name, data in df.group_by('type', maintain_order=True):
        html_string += f'{name[0]} <br>\n'
        # create_category_page()
        # create a page for each category
        for name1, data1 in data.group_by('value', maintain_order=True):
            html_string += f'<a href="/recipe-site/categories/{name1[0].lower()}.html">{name1[0]}</a> <br>\n'
            create_category_page(data1, df_recipes)
            
    html_string += "\n</body>"
    with open(Path('categories.html'), 'w') as f:
        f.write(BeautifulSoup(html_string, 'html.parser').prettify())

def create_category_page(df: pl.DataFrame, df_recipes: pl.DataFrame):
    with open(Path('templating.json')) as f:
        templating = json.load(f)
    html_string = templating['head'] + "\n<body>\n" + templating['topnav'] + "\n"

    for row in df.iter_rows():
        recipe_file = df_recipes.filter(pl.col('name') == row[2]).row(0)[2]
        html_string += f'<a href="/recipe-site/{recipe_file}">{row[2]}</a> <br>\n'

    html_string += "\n</body>"
    with open(Path('categories', row[1].lower() + '.html'), 'w') as f:
        f.write(BeautifulSoup(html_string, 'html.parser').prettify())
    # add thumbnail + name + categories for each recipe

def create_index_page():
    # create index page with search box
        # make recipe list into a list of clickable links

    #     updates index with a list of all recipes
    pass

def main():
    md_recipes = Path("md_recipes").glob('**/*.md')
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
    
                

if __name__ == '__main__':
    main()