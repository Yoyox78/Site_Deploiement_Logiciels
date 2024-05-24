from flask import Flask,render_template,request,jsonify
import os
import ansible_runner

app = Flask(__name__)

#logiciels = list(filter(os.path.isfile, os.listdir('./logiciels/')))
directory = "/etc/Deploiement_Logiciel/ansible/logiciels/"

# Liste tous les fichiers dans le répertoire sans leur extension
logiciels = [os.path.splitext(f)[0] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
# utilisateur administrateur des postes, par defaut administrateur
useradm = "USRADM"

@app.route('/')
def index():
  return render_template('index.html',len = len(logiciels), logiciels = logiciels)
  app.run(use_reloader = True, debug = True)

@app.route('/deploy', methods=['GET'])
def deploy():
    # On désactive la colorisation de ansible
    os.environ['ANSIBLE_NOCOLOR'] = 'true'
    # On récup l'IP envoyer via le module request
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    # pareil pour le nom du logiciel
    logiciel = request.args.get('logiciel')

    # Si il manque un argument ca ressort une erreur 400
    if not ip or not logiciel:
        return jsonify({"error": "Missing required parameters"}),   400

    # Préparer les variables pour le playbook en indiquand le logiciel l'user et les paramètre liée à la connexion
    extra_vars = {'ansible_user': useradm, 'package_name': logiciel, 'ansible_shell_type': "powershell", 'ansible_connection': "ssh"}

    # Exécuter le playbook avec ansible_runner, on indique le chemin du dossier contenant le playbook, ansi que le nom de celui-ci
    # on indique l'IP visé reprise de l'url et la variable extra vars indiqué plus haut
    r = ansible_runner.run(private_data_dir='/etc/Deploiement_Logiciel/ansible',
                            playbook='deploiement.yaml',
			                inventory=ip,
                            extravars=extra_vars)

    # Construire la réponse HTTP en json, a voir si euréka peut l'interpréter
    response = {
        "status": "success" if r.rc ==   0 else "failure",
        "return_code": r.rc,
        "stdout": r.stdout.read(),  # Lire le contenu du flux stdout
        "stderr": r.stderr.read()   # Lire le contenu du flux stderr
    }
    return jsonify(response)

@app.route('/remove', methods=['GET'])
def remove():
    # On désactive la colorisation de ansible
    os.environ['ANSIBLE_NOCOLOR'] = 'true'
    # On récup l'IP envoyer via le module request
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    # pareil pour le nom du logiciel
    logiciel = request.args.get('logiciel')

    # Si il manque un argument ca ressort une erreur 400
    if not ip or not logiciel:
        return jsonify({"error": "Missing required parameters"}),   400

    # Préparer les variables pour le playbook en indiquand le logiciel l'user et les paramètre liée à la connexion
    extra_vars = {'ansible_user': useradm, 'package_name': logiciel, 'ansible_shell_type': "powershell", 'ansible_connection': "ssh"}

    # Exécuter le playbook avec ansible_runner, on indique le chemin du dossier contenant le playbook, ansi que le nom de celui-ci
    # on indique l'IP visé reprise de l'url et la variable extra vars indiqué plus haut
    r = ansible_runner.run(private_data_dir='/etc/Deploiement_Logiciel/ansible',
                            playbook='remove.yaml',
			                inventory=ip,
                            extravars=extra_vars)

    # Construire la réponse HTTP en json, a voir si euréka peut l'interpréter
    response = {
        "status": "success" if r.rc ==   0 else "failure",
        "return_code": r.rc,
        "stdout": r.stdout.read(),  # Lire le contenu du flux stdout
        "stderr": r.stderr.read()   # Lire le contenu du flux stderr
    }
    return jsonify(response)

