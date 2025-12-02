#!/usr/bin/env python3
import click
from src.tools import generate_synthetic
from src.train import train_demo

@click.group()
def cli():
    """CitySafeSense CLI"""
    pass

@cli.command()
@click.option('--out', default='data/sample.npy', help='Output file')
@click.option('--duration', default=60, help='Duration in seconds')
def synth(out, duration):
    """Generate synthetic sensor data"""
    generate_synthetic.main(out, duration)

@cli.command()
@click.option('--epochs', default=1, help='Epochs for demo')
def train(epochs):
    """Run a tiny training demo"""
    train_demo.main(int(epochs))

if __name__ == '__main__':
    cli()
