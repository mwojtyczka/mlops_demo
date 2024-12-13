import pathlib


def test_notebook_format():
    # Verify that all Databricks notebooks have the required header
    paths = list(pathlib.Path("./notebooks").glob("**/*.py"))
    for f in paths:
        with open(str(f), encoding="uft-8") as file:
            notebook_str = file.read()
        assert notebook_str.startswith("# Databricks notebook source")
