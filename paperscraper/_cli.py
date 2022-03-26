import click
from paperscraper._preprocess import (get_processed_db, get_unique_venues, get_extracted_data, get_processed_data)


@click.group()
def cli():
    pass


@cli.group()
def process():
    pass

@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def run_all(force):
    get_processed_db(force=False)
    get_unique_venues(force=False)
    get_extracted_data(force=False)
    get_processed_data(force=force)
