#!/usr/bin/env python
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import docker
import socket


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
cli = docker.from_env()


@app.route('/api/v1/docker/list', methods=['GET'])
@cross_origin()
def get_docker():
    return jsonify([{
            'id': i.id,
            'name': i.name,
            'status': i.status,
            'labels': i.labels,
            'short_id': i.short_id,
            'image_id': i.image.id,
        } for i in cli.containers.list()])


@app.route('/api/v1/docker/images', methods=['GET'])
@cross_origin()
def get_images():
    return jsonify([{
            'id': i.id,
            'labels': i.labels,
            'short_id': i.short_id,
            'tags': i.tags,
        } for i in cli.images.list()])


@app.route('/api/v1/docker', methods=['POST'])
@cross_origin()
def run_docker():
    pass


@app.route('/api/v1/docker/status/<name>', methods=['GET'])
@cross_origin()
def get_docker_stat(name):
    c = cli.containers.get(name)
    pre_stat = c.stats(stream=False)
    cur_stat = c.stats(stream=False)
    pre_cpu = pre_stat['cpu_stats']
    cur_cpu = cur_stat['cpu_stats']
    cpu_delta = cur_cpu['cpu_usage']['total_usage'] - pre_cpu['cpu_usage']['total_usage']
    system_delta = cur_cpu['system_cpu_usage'] - pre_cpu['system_cpu_usage']
    if system_delta > 0:
        return jsonify(float(cpu_delta) / float(system_delta) * 100.0 * cur_cpu['online_cpus'])
    else:
        return jsonify(0.0)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
