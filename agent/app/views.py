from flask import render_template, flash, redirect, session, url_for, abort, g, jsonify
from commands import getoutput
from app import app, db
from app.models import Job
from sqlalchemy import desc

@app.route('/new', method=['POST'])
def add_job():
    pass


@app.route('/queue')
def queue_status():
    jobs = Job.query.filter_by(completed=False).all()
    return jsonify([job.json for job in jobs])


@app.route('/list')
def container_list():
    return jsonify(getoutput('vzlist -j'))