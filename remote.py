from flask import Flask, jsonify, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

def remote():
    