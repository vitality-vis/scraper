import click
from paperscraper._preprocess import (get_processed_db, get_extracted_data, get_processed_data)
from paperscraper._postprocess import get_post_processed_data
from paperscraper.config import config

@click.group()
def cli():
    """Cli interface for paperscraper."""
    pass


@cli.group()
def process():
    """Process and setup database."""
    pass


@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def process_db(force):
    """Process the dblp xml file."""
    get_processed_db(config=config, force=force)


@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def extract_data(force):
    """Extract data from processed dblp xml file."""
    get_extracted_data(config=config, force=force)


@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def process_data(force):
    """Process extracted data."""
    get_processed_data(config=config, force=force)


@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def post_process_data(force):
    """Run cleanup process after processing data."""
    get_post_processed_data(config=config, force=force)


@process.command()
@click.option("-f", "--force", help="Force run all steps", is_flag=True)
def run_all(force):
    """Run all steps in order."""
    get_processed_db(config=config, force=force)
    get_extracted_data(config=config, force=force)
    get_processed_data(config=config, force=force)
    get_post_processed_data(config=config, force=force)
