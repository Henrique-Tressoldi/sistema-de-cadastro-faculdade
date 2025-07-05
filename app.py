from flask import Flask, render_template, request, jsonify
import os
import uuid # Para gerar IDs únicos
import json # Para lidar com dados mais complexos (professor na oferta)

app = Flask(__name__)

# --- Definições de Caminho dos Arquivos ---
DATA_DIR = 'data'
TURMAS_FILE = os.path.join(DATA_DIR, 'turmas.txt')
DISCIPLINAS_FILE = os.path.join(DATA_DIR, 'disciplinas.txt') # Catálogo de disciplinas
ALUNOS_FILE = os.path.join(DATA_DIR, 'alunos.txt')
TURMA_DISCIPLINAS_FILE = os.path.join(DATA_DIR, 'turma_disciplinas.txt') # Disciplinas oferecidas em turmas
MATRICULAS_FILE = os.path.join(DATA_DIR, 'matriculas.txt') # Alunos matriculados em disciplinas-oferta

# Garante que o diretório de dados exista
os.makedirs(DATA_DIR, exist_ok=True)

# Funções auxiliares para leitura e escrita dos arquivos
# Usaremos um formato simples de "id|campo1|campo2"

def generate_id():
    """Gera um ID único usando UUID."""
    return str(uuid.uuid4())

# NEW: Helper para ler os dados brutos (dicionários) diretamente dos arquivos
def _read_raw_data_from_files():
    """Lê todos os dados brutos dos arquivos e os estrutura em dicionários em memória."""
    raw_data = {
        'turmas_raw': {},
        'disciplinas_catalogo_raw': {},
        'alunos_raw': {},
        'turma_disciplinas_ofertas_raw': {},
        'matriculas_raw': {}
    }

    # Ler turmas.txt
    if os.path.exists(TURMAS_FILE):
        with open(TURMAS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    raw_data['turmas_raw'][parts[0]] = {'id': parts[0], 'nome': parts[1]}

    # Ler disciplinas.txt (catálogo)
    if os.path.exists(DISCIPLINAS_FILE):
        with open(DISCIPLINAS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3: # id|codigo|nome
                    raw_data['disciplinas_catalogo_raw'][parts[0]] = {'id': parts[0], 'codigo': parts[1], 'nome': parts[2]}

    # Ler alunos.txt
    if os.path.exists(ALUNOS_FILE):
        with open(ALUNOS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4: # id|matricula|nome|telefone
                    raw_data['alunos_raw'][parts[0]] = {'id': parts[0], 'matricula': parts[1], 'nome': parts[2], 'telefone': parts[3]}
    
    # Ler turma_disciplinas.txt (ofertas)
    if os.path.exists(TURMA_DISCIPLINAS_FILE):
        with open(TURMA_DISCIPLINAS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4: # id|turma_id|disciplina_catalogo_id|professor
                    raw_data['turma_disciplinas_ofertas_raw'][parts[0]] = {
                        'id': parts[0], 
                        'turma_id': parts[1], 
                        'disciplina_catalogo_id': parts[2], 
                        'professor': parts[3]
                    }

    # Ler matriculas.txt
    if os.path.exists(MATRICULAS_FILE):
        with open(MATRICULAS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3: # id|aluno_id|turma_disciplina_id
                    raw_data['matriculas_raw'][parts[0]] = {
                        'id': parts[0], 
                        'aluno_id': parts[1], 
                        'turma_disciplina_id': parts[2]
                    }

    return raw_data

# NEW: Helper para escrever os dados brutos de volta para os arquivos
def write_raw_data_to_files(raw_data):
    """Escreve todos os dados brutos de volta para os arquivos."""
    with open(TURMAS_FILE, 'w') as f:
        for turma in raw_data['turmas_raw'].values():
            f.write(f"{turma['id']}|{turma['nome']}\n")
    
    with open(DISCIPLINAS_FILE, 'w') as f:
        for disciplina in raw_data['disciplinas_catalogo_raw'].values():
            f.write(f"{disciplina['id']}|{disciplina['codigo']}|{disciplina['nome']}\n")
            
    with open(ALUNOS_FILE, 'w') as f:
        for aluno in raw_data['alunos_raw'].values():
            f.write(f"{aluno['id']}|{aluno['matricula']}|{aluno['nome']}|{aluno['telefone']}\n")

    with open(TURMA_DISCIPLINAS_FILE, 'w') as f:
        for oferta in raw_data['turma_disciplinas_ofertas_raw'].values():
            f.write(f"{oferta['id']}|{oferta['turma_id']}|{oferta['disciplina_catalogo_id']}|{oferta['professor']}\n")
            
    with open(MATRICULAS_FILE, 'w') as f:
        for matricula in raw_data['matriculas_raw'].values():
            f.write(f"{matricula['id']}|{matricula['aluno_id']}|{matricula['turma_disciplina_id']}\n")
            
    print("Dados salvos com sucesso nos arquivos.") # Para debug no console do Flask


# Função principal para obter dados formatados para o frontend
def get_current_full_data(search_turma=None, search_disciplina=None, search_aluno=None):
    raw_data = _read_raw_data_from_files()

    turmas = []
    for turma_id, turma_info in raw_data['turmas_raw'].items():
        if search_turma and search_turma.lower() not in turma_info['nome'].lower():
            continue
        
        disciplinas_na_turma = []
        for oferta_id, oferta_info in raw_data['turma_disciplinas_ofertas_raw'].items():
            if oferta_info['turma_id'] == turma_id:
                disciplina_catalogo_info = raw_data['disciplinas_catalogo_raw'].get(oferta_info['disciplina_catalogo_id'])
                if disciplina_catalogo_info:
                    
                    # Apply search_disciplina filter if present
                    if search_disciplina and search_disciplina.lower() not in disciplina_catalogo_info['nome'].lower() and \
                       search_disciplina.lower() not in disciplina_catalogo_info['codigo'].lower():
                        continue

                    alunos_na_disciplina = []
                    for matricula_id, matricula_info in raw_data['matriculas_raw'].items():
                        if matricula_info['turma_disciplina_id'] == oferta_id:
                            aluno_info = raw_data['alunos_raw'].get(matricula_info['aluno_id'])
                            if aluno_info:
                                # Apply search_aluno filter if present
                                if search_aluno and search_aluno.lower() not in aluno_info['nome'].lower() and \
                                   search_aluno.lower() not in aluno_info['matricula'].lower():
                                    continue
                                
                                alunos_na_disciplina.append({
                                    'id': aluno_info['id'],
                                    'matricula': aluno_info['matricula'],
                                    'nome': aluno_info['nome'],
                                    'telefone': aluno_info['telefone'],
                                    'matricula_id': matricula_info['id'] # Adiciona o ID da matrícula para facilitar a exclusão
                                })
                    disciplinas_na_turma.append({
                        'id': oferta_id, # ID da oferta
                        'codigo': disciplina_catalogo_info['codigo'],
                        'nome': disciplina_catalogo_info['nome'],
                        'professor': oferta_info['professor'],
                        'alunos': alunos_na_disciplina,
                        'disciplina_catalogo_id': disciplina_catalogo_info['id'] # Adiciona o ID do catálogo
                    })
        turmas.append({
            'id': turma_id,
            'nome': turma_info['nome'],
            'disciplinas': disciplinas_na_turma # Estas são as ofertas de disciplina
        })

    # Preparar catálogo de disciplinas para o frontend (sem filtro de busca aqui)
    disciplinas_catalogo_list = [
        {'id': d_id, 'codigo': d_info['codigo'], 'nome': d_info['nome']} 
        for d_id, d_info in raw_data['disciplinas_catalogo_raw'].items()
    ]
    if search_disciplina: # Apply search to catalog directly if not part of a turma search
        disciplinas_catalogo_list = [
            d for d in disciplinas_catalogo_list 
            if search_disciplina.lower() in d['nome'].lower() or search_disciplina.lower() in d['codigo'].lower()
        ]

    # Preparar lista de alunos para o frontend (sem filtro de busca aqui)
    alunos_list = [
        {'id': a_id, 'matricula': a_info['matricula'], 'nome': a_info['nome'], 'telefone': a_info['telefone']}
        for a_id, a_info in raw_data['alunos_raw'].items()
    ]
    if search_aluno: # Apply search to students directly if not part of a turma search
        alunos_list = [
            a for a in alunos_list 
            if search_aluno.lower() in a['nome'].lower() or search_aluno.lower() in a['matricula'].lower()
        ]

    # Preparar ofertas de disciplina (turma_disciplinas_ofertas) para exibição direta
    # Esta lista é plana para facilitar a busca e renderização sem depender de turmas
    ofertas_list = []
    for oferta_id, oferta_info in raw_data['turma_disciplinas_ofertas_raw'].items():
        turma_info = raw_data['turmas_raw'].get(oferta_info['turma_id'])
        disciplina_catalogo_info = raw_data['disciplinas_catalogo_raw'].get(oferta_info['disciplina_catalogo_id'])
        
        if turma_info and disciplina_catalogo_info:
            ofertas_list.append({
                'id': oferta_id,
                'turma_id': oferta_info['turma_id'],
                'turma_nome': turma_info['nome'],
                'disciplina_catalogo_id': oferta_info['disciplina_catalogo_id'],
                'disciplina_codigo': disciplina_catalogo_info['codigo'],
                'disciplina_nome': disciplina_catalogo_info['nome'],
                'professor': oferta_info['professor']
            })
            
    # Preparar lista de matrículas para exibição direta
    matriculas_list = []
    for matricula_id, matricula_info in raw_data['matriculas_raw'].items():
        aluno_info = raw_data['alunos_raw'].get(matricula_info['aluno_id'])
        oferta_info = raw_data['turma_disciplinas_ofertas_raw'].get(matricula_info['turma_disciplina_id'])
        
        if aluno_info and oferta_info:
            disciplina_catalogo_info = raw_data['disciplinas_catalogo_raw'].get(oferta_info['disciplina_catalogo_id'])
            turma_info = raw_data['turmas_raw'].get(oferta_info['turma_id'])

            if disciplina_catalogo_info and turma_info:
                matriculas_list.append({
                    'id': matricula_id,
                    'aluno_id': aluno_info['id'],
                    'aluno_matricula': aluno_info['matricula'],
                    'aluno_nome': aluno_info['nome'],
                    'turma_disciplina_id': oferta_info['id'],
                    'turma_nome': turma_info['nome'],
                    'disciplina_nome': disciplina_catalogo_info['nome'],
                    'professor': oferta_info['professor']
                })


    return {
        'turmas': turmas,
        'disciplinas_catalogo': disciplinas_catalogo_list,
        'alunos': alunos_list,
        'turma_disciplinas_ofertas': ofertas_list,
        'matriculas': matriculas_list
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    search_turma = request.args.get('search_turma')
    search_disciplina = request.args.get('search_disciplina')
    search_aluno = request.args.get('search_aluno')
    data = get_current_full_data(search_turma, search_disciplina, search_aluno)
    return jsonify(data)

# --- ROTAS DE ADIÇÃO (POST) ---

@app.route('/api/turmas', methods=['POST'])
def add_turma():
    data = request.json
    nome = data.get('nome')
    if not nome:
        return jsonify({'error': 'Nome da turma é obrigatório.'}), 400
    
    raw_data = _read_raw_data_from_files()
    new_id = generate_id()
    raw_data['turmas_raw'][new_id] = {'id': new_id, 'nome': nome}
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Turma adicionada com sucesso!', 'id': new_id}), 201

@app.route('/api/disciplinas_catalogo', methods=['POST'])
def add_disciplina_catalogo():
    data = request.json
    codigo = data.get('codigo')
    nome = data.get('nome')
    if not codigo or not nome:
        return jsonify({'error': 'Código e nome da disciplina são obrigatórios.'}), 400
    
    raw_data = _read_raw_data_from_files()
    
    # Verifica se já existe uma disciplina com o mesmo código
    if any(d['codigo'] == codigo for d in raw_data['disciplinas_catalogo_raw'].values()):
        return jsonify({'error': 'Já existe uma disciplina com este código.'}), 409 # Conflict
        
    new_id = generate_id()
    raw_data['disciplinas_catalogo_raw'][new_id] = {'id': new_id, 'codigo': codigo, 'nome': nome}
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Disciplina adicionada ao catálogo com sucesso!', 'id': new_id}), 201

@app.route('/api/alunos', methods=['POST'])
def add_aluno():
    data = request.json
    matricula = data.get('matricula')
    nome = data.get('nome')
    telefone = data.get('telefone')
    if not matricula or not nome or not telefone:
        return jsonify({'error': 'Matrícula, nome e telefone do aluno são obrigatórios.'}), 400

    raw_data = _read_raw_data_from_files()
    # Verifica se a matrícula já existe
    if any(a['matricula'] == matricula for a in raw_data['alunos_raw'].values()):
        return jsonify({'error': 'Já existe um aluno com esta matrícula.'}), 409 # Conflict

    new_id = generate_id()
    raw_data['alunos_raw'][new_id] = {'id': new_id, 'matricula': matricula, 'nome': nome, 'telefone': telefone}
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Aluno adicionado com sucesso!', 'id': new_id}), 201

@app.route('/api/turma_disciplinas_ofertas', methods=['POST'])
def add_oferta_disciplina():
    data = request.json
    turma_id = data.get('turma_id')
    disciplina_catalogo_id = data.get('disciplina_catalogo_id')
    professor = data.get('professor')

    if not turma_id or not disciplina_catalogo_id or not professor:
        return jsonify({'error': 'Todos os campos (turma, disciplina e professor) são obrigatórios para a oferta.'}), 400

    raw_data = _read_raw_data_from_files()

    if turma_id not in raw_data['turmas_raw']:
        return jsonify({'error': 'Turma não encontrada.'}), 404
    if disciplina_catalogo_id not in raw_data['disciplinas_catalogo_raw']:
        return jsonify({'error': 'Disciplina do catálogo não encontrada.'}), 404
    
    # Verifica se a oferta já existe para evitar duplicatas
    if any(o['turma_id'] == turma_id and o['disciplina_catalogo_id'] == disciplina_catalogo_id 
           for o in raw_data['turma_disciplinas_ofertas_raw'].values()):
        return jsonify({'error': 'Esta disciplina já está sendo ofertada nesta turma.'}), 409

    new_id = generate_id()
    raw_data['turma_disciplinas_ofertas_raw'][new_id] = {
        'id': new_id, 
        'turma_id': turma_id, 
        'disciplina_catalogo_id': disciplina_catalogo_id, 
        'professor': professor
    }
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Oferta de disciplina adicionada com sucesso!', 'id': new_id}), 201

@app.route('/api/matriculas', methods=['POST'])
def add_matricula():
    data = request.json
    aluno_id = data.get('aluno_id')
    turma_disciplina_id = data.get('turma_disciplina_id')

    if not aluno_id or not turma_disciplina_id:
        return jsonify({'error': 'Aluno e oferta de disciplina são obrigatórios para a matrícula.'}), 400
    
    raw_data = _read_raw_data_from_files()
    
    if aluno_id not in raw_data['alunos_raw']:
        return jsonify({'error': 'Aluno não encontrado.'}), 404
    if turma_disciplina_id not in raw_data['turma_disciplinas_ofertas_raw']:
        return jsonify({'error': 'Oferta de disciplina não encontrada.'}), 404
    
    # Verifica se o aluno já está matriculado nesta oferta
    if any(m['aluno_id'] == aluno_id and m['turma_disciplina_id'] == turma_disciplina_id for m in raw_data['matriculas_raw'].values()):
        return jsonify({'error': 'Este aluno já está matriculado nesta oferta de disciplina.'}), 409

    matricula_id = generate_id()
    new_matricula = {
        'id': matricula_id,
        'aluno_id': aluno_id,
        'turma_disciplina_id': turma_disciplina_id
    }
    raw_data['matriculas_raw'][matricula_id] = new_matricula

    write_raw_data_to_files(raw_data)

    return jsonify({'message': 'Matrícula realizada com sucesso!', 'id': matricula_id}), 201


# --- ROTAS DE ATUALIZAÇÃO (PUT) ---
@app.route('/api/turmas/<turma_id>', methods=['PUT'])
def update_turma(turma_id):
    data = request.json
    nome = data.get('nome')
    if not nome:
        return jsonify({'error': 'Nome da turma é obrigatório.'}), 400

    raw_data = _read_raw_data_from_files()
    if turma_id not in raw_data['turmas_raw']:
        return jsonify({'error': 'Turma não encontrada.'}), 404
    
    raw_data['turmas_raw'][turma_id]['nome'] = nome
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Turma atualizada com sucesso!'}), 200

@app.route('/api/disciplinas_catalogo/<disciplina_id>', methods=['PUT'])
def update_disciplina_catalogo(disciplina_id):
    data = request.json
    codigo = data.get('codigo')
    nome = data.get('nome')
    if not codigo or not nome:
        return jsonify({'error': 'Código e nome da disciplina são obrigatórios.'}), 400

    raw_data = _read_raw_data_from_files()
    if disciplina_id not in raw_data['disciplinas_catalogo_raw']:
        return jsonify({'error': 'Disciplina do catálogo não encontrada.'}), 404
    
    # Check for duplicate code (excluding the current discipline being updated)
    if any(d['codigo'] == codigo and d_id != disciplina_id 
           for d_id, d in raw_data['disciplinas_catalogo_raw'].items()):
        return jsonify({'error': 'Já existe outra disciplina com este código.'}), 409
        
    raw_data['disciplinas_catalogo_raw'][disciplina_id]['codigo'] = codigo
    raw_data['disciplinas_catalogo_raw'][disciplina_id]['nome'] = nome
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Disciplina do catálogo atualizada com sucesso!'}), 200

@app.route('/api/alunos/<aluno_id>', methods=['PUT'])
def update_aluno(aluno_id):
    data = request.json
    matricula = data.get('matricula')
    nome = data.get('nome')
    telefone = data.get('telefone')
    if not matricula or not nome or not telefone:
        return jsonify({'error': 'Matrícula, nome e telefone do aluno são obrigatórios.'}), 400

    raw_data = _read_raw_data_from_files()
    if aluno_id not in raw_data['alunos_raw']:
        return jsonify({'error': 'Aluno não encontrado.'}), 404

    # Check for duplicate matricula (excluding the current student being updated)
    if any(a['matricula'] == matricula and a_id != aluno_id 
           for a_id, a in raw_data['alunos_raw'].items()):
        return jsonify({'error': 'Já existe outro aluno com esta matrícula.'}), 409

    raw_data['alunos_raw'][aluno_id]['matricula'] = matricula
    raw_data['alunos_raw'][aluno_id]['nome'] = nome
    raw_data['alunos_raw'][aluno_id]['telefone'] = telefone
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Aluno atualizado com sucesso!'}), 200

@app.route('/api/turma_disciplinas_ofertas/<oferta_id>', methods=['PUT'])
def update_oferta_disciplina(oferta_id):
    data = request.json
    professor = data.get('professor')
    if not professor:
        return jsonify({'error': 'Professor é obrigatório.'}), 400

    raw_data = _read_raw_data_from_files()
    if oferta_id not in raw_data['turma_disciplinas_ofertas_raw']:
        return jsonify({'error': 'Oferta de disciplina não encontrada.'}), 404
    
    raw_data['turma_disciplinas_ofertas_raw'][oferta_id]['professor'] = professor
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Oferta de disciplina atualizada com sucesso!'}), 200


# --- ROTAS DE REMOÇÃO (DELETE) ---

@app.route('/api/turmas/<turma_id>', methods=['DELETE'])
def delete_turma(turma_id):
    raw_data = _read_raw_data_from_files()
    
    if turma_id not in raw_data['turmas_raw']:
        return jsonify({'error': 'Turma não encontrada.'}), 404

    # Check for associated offers (disciplines in this turma)
    if any(o['turma_id'] == turma_id for o in raw_data['turma_disciplinas_ofertas_raw'].values()):
        return jsonify({'error': 'Não é possível remover a turma: existem ofertas de disciplinas associadas a ela.'}), 409
    
    del raw_data['turmas_raw'][turma_id]
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Turma removida com sucesso!'}), 200

@app.route('/api/disciplinas_catalogo/<disciplina_id>', methods=['DELETE'])
def delete_disciplina_catalogo(disciplina_id):
    raw_data = _read_raw_data_from_files()
    
    if disciplina_id not in raw_data['disciplinas_catalogo_raw']:
        return jsonify({'error': 'Disciplina do catálogo não encontrada.'}), 404

    # Check for associated offers (if this catalog discipline is offered in any turma)
    if any(o['disciplina_catalogo_id'] == disciplina_id for o in raw_data['turma_disciplinas_ofertas_raw'].values()):
        return jsonify({'error': 'Não é possível remover a disciplina do catálogo: existem ofertas associadas a ela em turmas.'}), 409
    
    del raw_data['disciplinas_catalogo_raw'][disciplina_id]
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Disciplina do catálogo removida com sucesso!'}), 200

@app.route('/api/alunos/<aluno_id>', methods=['DELETE'])
def delete_aluno(aluno_id):
    raw_data = _read_raw_data_from_files()
    
    if aluno_id not in raw_data['alunos_raw']:
        return jsonify({'error': 'Aluno não encontrado.'}), 404
        
    # Check for associated enrollments (if this student is matriculated in any discipline offer)
    if any(m['aluno_id'] == aluno_id for m in raw_data['matriculas_raw'].values()):
        return jsonify({'error': 'Não é possível remover o aluno: existem matrículas associadas a ele.'}), 409

    del raw_data['alunos_raw'][aluno_id]
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Aluno removido com sucesso!'}), 200

@app.route('/api/turma_disciplinas_ofertas/<oferta_id>', methods=['DELETE'])
def delete_oferta_disciplina(oferta_id):
    raw_data = _read_raw_data_from_files()
    
    if oferta_id not in raw_data['turma_disciplinas_ofertas_raw']:
        return jsonify({'error': 'Oferta de disciplina não encontrada.'}), 404

    # Check for associated enrollments (if students are matriculated in this offer)
    if any(m['turma_disciplina_id'] == oferta_id for m in raw_data['matriculas_raw'].values()):
        return jsonify({'error': 'Não é possível remover esta oferta de disciplina: existem matrículas de alunos associadas a ela.'}), 409

    del raw_data['turma_disciplinas_ofertas_raw'][oferta_id]
    write_raw_data_to_files(raw_data)
    return jsonify({'message': 'Oferta de disciplina removida com sucesso!'}), 200

@app.route('/api/matriculas/<matricula_id>', methods=['DELETE'])
def delete_matricula(matricula_id):
    raw_data = _read_raw_data_from_files()
    
    if matricula_id not in raw_data['matriculas_raw']:
        return jsonify({'error': 'Matrícula não encontrada.'}), 404
    
    del raw_data['matriculas_raw'][matricula_id]
    write_raw_data_to_files(raw_data)

    return jsonify({'message': 'Matrícula removida com sucesso!'}), 200

if __name__ == '__main__':
    app.run()