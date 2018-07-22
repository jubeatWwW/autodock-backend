from flask import Flask, jsonify
import docker


app = Flask(__name__)
cli = docker.from_env()


@app.route('/api/v1/docker/list', methods=['GET'])
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
def get_images():
    return jsonify([{
            'id': i.id,
            'labels': i.labels,
            'short_id': i.short_id,
            'tags': i.tags,
        } for i in cli.images.list()])


@app.route('/api/v1/docker', methods=['POST'])
def run_docker():
    pass


if __name__ == '__main__':
    app.run()
