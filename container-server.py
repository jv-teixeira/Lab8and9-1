from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return """
Available API endpoints:

GET /containers                     List all containers
GET /containers?state=running      List running containers (only)
GET /containers/<id>                Inspect a specific container
GET /containers/<id>/logs           Dump specific container logs
GET /images                         List all images


POST /images                        Create a new image
POST /containers                    Create a new container

PATCH /containers/<id>              Change a container's state
PATCH /images/<id>                  Change a specific image's attributes

DELETE /containers/<id>             Delete a specific container
DELETE /containers                  Delete all containers (including running)
DELETE /images/<id>                 Delete a specific image
DELETE /images                      Delete all images

"""

@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers
 
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool

    """
    if request.args.get('state') == 'running':
        output = docker('ps')
    else:
        output = docker('ps', '-a')
    resp = json.dumps(docker_ps_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
def images_index():
    """
    List all images
 
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/images | python -mjson.tool

    """
    if request.args.get('state') == 'running':
        output = docker('images')
    else:
        output = docker('images', '-a')
    resp = json.dumps(docker_images_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
    """
    Inspect specific container
    
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/<id> | python -mjson.tool 
    
    """
    if request.args.get('state') == 'running':
        output = docker('inspect')
    else:
        output = docker('inspect', id)
    resp = json.dumps(docker_logs_to_object(id,output))

    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
    """
    Dump specific container logs
    
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/<id>/logs | python -mjson.tool 

    """

    if request.args.get('state') == 'running':
        output = docker('logs',id)
    else:
        output = docker('logs',id)
    resp = json.dumps(docker_logs_to_object(id,output))
    
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
    """
    Delete a specific image

    curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/images/<imgID> | python -mjson.tool

    """
    docker ('rmi', id)
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
    """
    Delete a specific container - must be already stopped/killed

    curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/containers/<contID> | python -mjson.tool

    """
    docker ('rm', id)
    resp = '{"id": "%s"}' % id    
    return Response(response=resp, mimetype="application/json")

@app.route('/containersDel', methods=['DELETE'])
def containers_remove_all():
    """
    Force remove all containers - dangrous!

    curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/containersDel | python -mjson.tool

    """
    all = docker_ps_to_array(docker('ps', '-a'))
    for i in all:
    	docker ('stop',i['id'])
	docker('rm',' -f', i['id'])
    resp = '{"count": "%d"}' %len(all)
    return Response(response=resp, mimetype="application/json")

@app.route('/imagesDel', methods=['DELETE'])
def images_remove_all():
    """
    Force remove all images - dangrous!

    curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/imagesDel | python -mjson.tool

    """
    all = docker_images_to_array(docker('images'))
    for i in all:
        docker('rmi', i['id'])
    resp = '{"count": "%d"}' %len(all)
    return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['POST'])
def containers_create():
    """
    Create container (from existing image using id or name)

    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "my-app"}' | python -mjson.tool
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "<imgID>"}' | python -mjson.tool
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "<imgID>","publish":"8081:22"}' | python -mjson.tool

    """
    body = request.get_json(force=True)
    image = body['image']
    args = ('run', '-d')
    try:		
       # Optional attributes		
        publish = body['publish']		
        args = args + ('-p', publish)		
    except:		
        pass
    id = docker(*(args + (image,)))[0:12]
    return Response(response='{"id": "%s"}' % id, mimetype="application/json")

@app.route('/images', methods=['POST'])
def images_create():
    """
    Create image (from uploaded Dockerfile)

    curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images

    """
    dockerfile = request.files['file']
    
    dockerfile.save(os.path.join(app.config['/home/user/Lab8and9/my_application', dockerfile))
    
    docker('build', dockerfile, '.')
    resp = ''
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
    """
    Update container attributes (support: state=running|stopped)
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'
    """
    body = request.get_json(force=True)
    try:
        state = body['state']
        if state == 'running':
            docker('stop', id)
	elif state == 'stopped': 
	    docker('restart', id)
    except:
        pass

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
    """
    Update image attributes (support: name[:tag])  tag name should be lowercase only

    curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/<id> -d '{"tag": "test:1.0"}'

    """
    
    body = request.get_json(force=True)
    name = body['tag']
    docker('tag', id, name)

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith('Error'):
        print 'Error: {0} -> {1}'.format(' '.join(cmd), stderr)
    return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['image'] = c[1]
        each['name'] = c[-1]
        each['ports'] = c[-2]
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2]
        each['tag'] = c[1]
        each['name'] = c[0]
        all.append(each)
    return all

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
