"""Utility functions
"""
import json

def read_json(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)

def write_json(file_path, json_obj):
    with open(file_path, "w") as json_file:
        json.dump(json_obj, json_file)