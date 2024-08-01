from convert import convert_file
from pathlib import Path
import polars as pl

def create_categories_page(df: pl.DataFrame):
    pass

def create_category_page(df: pl.DataFrame):
    # add thumbnail + name + categories for each recipe
    pass

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
        # tags are created as %%tag Course%%Appetizer Cuisine%%American Cuisine%%French
        metadata = convert_file(md_recipe)
        recipes = pl.concat([recipes, pl.DataFrame({'name': metadata['name'], 'image': metadata['image']})])
        tags = pl.concat([tags, pl.DataFrame(metadata['tags'])])
    # print(recipes.head())
    # print(tags.head())

    # create a page for all categories
    # create_categories_page()
    for name, data in tags.group_by('type'):
        print(name)
        print(data.head())
        # create_category_page()
        # create a page for each category
        for name1, data1 in data.group_by('value'):
            print(name1)
            print(data1.head())
                

if __name__ == '__main__':
    main()