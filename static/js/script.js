document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

let currentData = {
    turmas: [],
    disciplinas_catalogo: [],
    alunos: [],
    turma_disciplinas_ofertas: [],
    matriculas: []
};

let currentSearchTerms = { // Para manter os termos de busca entre as chamadas
    turma: '',
    disciplina: '', // Para catálogo de disciplinas
    aluno: ''
};
let currentActiveSection = 'turmas'; // Para saber qual seção está ativa

// Modificada para aceitar parâmetros de busca
async function fetchData(section = currentActiveSection) {
    currentActiveSection = section; // Atualiza a seção ativa

    let url = '/api/data';
    const params = new URLSearchParams();

    // Adiciona termos de busca baseados na seção ativa
    if (section === 'turmas' && currentSearchTerms.turma) {
        params.append('search_turma', currentSearchTerms.turma);
    } else if (section === 'disciplinas_catalogo' && currentSearchTerms.disciplina) { // Corrigido para disciplinas_catalogo
        params.append('search_disciplina', currentSearchTerms.disciplina);
    } else if (section === 'alunos' && currentSearchTerms.aluno) {
        params.append('search_aluno', currentSearchTerms.aluno);
    }

    if (params.toString()) {
        url += '?' + params.toString();
    }

    try {
        const response = await fetch(url);
        currentData = await response.json();
        console.log("Dados carregados:", currentData); // Para debug
        renderTurmas();
        renderDisciplinas(); // Renderiza catálogo
        renderAlunos();
        renderOfertasDisciplinas(); // Renderiza ofertas
        renderMatriculas(); // Renderiza matrículas
        updateSelects(); // Atualiza dropdowns
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
        alert('Erro ao carregar dados do servidor.');
    }
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(`${sectionId}-section`).style.display = 'block';
    currentActiveSection = sectionId; // Atualiza a seção ativa
    fetchData(sectionId); // Recarrega os dados para a seção ativa
}


// --- Funções de Renderização ---

function renderTurmas() {
    const container = document.getElementById('turmas-list');
    container.innerHTML = '';
    if (!currentData.turmas || currentData.turmas.length === 0) {
        container.innerHTML = '<p>Nenhuma turma cadastrada (ou encontrada com o filtro).</p>';
        return;
    }

    currentData.turmas.forEach(turma => {
        const turmaDiv = document.createElement('div');
        turmaDiv.classList.add('item-list');
        turmaDiv.innerHTML = `
            <span>ID: ${turma.id}, Nome: ${turma.nome}</span>
            <div class="actions">
                <button onclick="editTurma('${turma.id}', '${turma.nome}')">Editar</button>
                <button onclick="deleteTurma('${turma.id}')">Remover</button>
            </div>
        `;
        container.appendChild(turmaDiv);
    });
}

function renderDisciplinas() { // Renderiza Catálogo de Disciplinas
    const container = document.getElementById('disciplinas-catalogo-list');
    container.innerHTML = '';
    if (!currentData.disciplinas_catalogo || currentData.disciplinas_catalogo.length === 0) {
        container.innerHTML = '<p>Nenhuma disciplina no catálogo (ou encontrada com o filtro).</p>';
        return;
    }

    currentData.disciplinas_catalogo.forEach(disciplina => {
        const disciplinaDiv = document.createElement('div');
        disciplinaDiv.classList.add('item-list');
        disciplinaDiv.innerHTML = `
            <span>ID: ${disciplina.id}, Código: ${disciplina.codigo}, Nome: ${disciplina.nome}</span>
            <div class="actions">
                <button onclick="editDisciplina('${disciplina.id}', '${disciplina.codigo}', '${disciplina.nome}')">Editar</button>
                <button onclick="deleteDisciplina('${disciplina.id}')">Remover</button>
            </div>
        `;
        container.appendChild(disciplinaDiv);
    });
}

function renderAlunos() {
    const container = document.getElementById('alunos-list');
    container.innerHTML = '';
    if (!currentData.alunos || currentData.alunos.length === 0) {
        container.innerHTML = '<p>Nenhum aluno cadastrado (ou encontrado com o filtro).</p>';
        return;
    }

    currentData.alunos.forEach(aluno => {
        const alunoDiv = document.createElement('div');
        alunoDiv.classList.add('item-list');
        alunoDiv.innerHTML = `
            <span>ID: ${aluno.id}, Matrícula: ${aluno.matricula}, Nome: ${aluno.nome}, Telefone: ${aluno.telefone}</span>
            <div class="actions">
                <button onclick="editAluno('${aluno.id}', '${aluno.matricula}', '${aluno.nome}', '${aluno.telefone}')">Editar</button>
                <button onclick="deleteAluno('${aluno.id}')">Remover</button>
            </div>
        `;
        container.appendChild(alunoDiv);
    });
}

function renderOfertasDisciplinas() { // Renderiza ofertas de disciplina
    const container = document.getElementById('turma-disciplinas-ofertas-list');
    container.innerHTML = '';
    if (!currentData.turma_disciplinas_ofertas || currentData.turma_disciplinas_ofertas.length === 0) {
        container.innerHTML = '<p>Nenhuma oferta de disciplina cadastrada.</p>';
        return;
    }

    currentData.turma_disciplinas_ofertas.forEach(oferta => {
        const ofertaDiv = document.createElement('div');
        ofertaDiv.classList.add('item-list');
        ofertaDiv.innerHTML = `
            <span>ID Oferta: ${oferta.id}, Turma: ${oferta.turma_nome}, Disciplina: ${oferta.disciplina_nome} (${oferta.disciplina_codigo}), Professor: ${oferta.professor}</span>
            <div class="actions">
                <button onclick="editOfertaDisciplina('${oferta.id}', '${oferta.professor}')">Editar</button>
                <button onclick="deleteOfertaDisciplina('${oferta.id}')">Remover</button>
            </div>
        `;
        container.appendChild(ofertaDiv);
    });
}

function renderMatriculas() { // Renderiza matrículas
    const container = document.getElementById('matriculas-list-container');
    container.innerHTML = '';
    if (!currentData.matriculas || currentData.matriculas.length === 0) {
        container.innerHTML = '<p>Nenhuma matrícula cadastrada.</p>';
        return;
    }

    currentData.matriculas.forEach(matricula => {
        const matriculaDiv = document.createElement('div');
        matriculaDiv.classList.add('item-list');
        matriculaDiv.innerHTML = `
            <span>ID Matrícula: ${matricula.id}, Aluno: ${matricula.aluno_nome} (${matricula.aluno_matricula}), Disciplina: ${matricula.disciplina_nome} (${matricula.professor}) em ${matricula.turma_nome}</span>
            <div class="actions">
                <button onclick="deleteMatricula('${matricula.id}')">Remover</button>
            </div>
        `;
        container.appendChild(matriculaDiv);
    });
}

// --- Funções para Preencher Selects (Dropdowns) ---
function updateSelects() {
    // Select de ofertas para Matrícula
    const matriculaTurmaDisciplinaSelect = document.getElementById('matricula-turma-disciplina-select');
    matriculaTurmaDisciplinaSelect.innerHTML = '<option value="">Selecione uma oferta de disciplina</option>';
    currentData.turma_disciplinas_ofertas.forEach(oferta => {
        const option = document.createElement('option');
        option.value = oferta.id;
        option.textContent = `Turma: ${oferta.turma_nome} - ${oferta.disciplina_nome} (${oferta.professor})`;
        matriculaTurmaDisciplinaSelect.appendChild(option);
    });

    // Select de Alunos para Matrícula
    const matriculaAlunoSelect = document.getElementById('matricula-aluno-select');
    matriculaAlunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
    currentData.alunos.forEach(aluno => {
        const option = document.createElement('option');
        option.value = aluno.id;
        option.textContent = `${aluno.nome} (${aluno.matricula})`;
        matriculaAlunoSelect.appendChild(option);
    });

    // Select de Turmas para Oferta de Disciplina
    const ofertaTurmaSelect = document.getElementById('oferta-turma-select');
    ofertaTurmaSelect.innerHTML = '<option value="">Selecione uma turma</option>';
    currentData.turmas.forEach(turma => {
        const option = document.createElement('option');
        option.value = turma.id;
        option.textContent = turma.nome;
        ofertaTurmaSelect.appendChild(option);
    });

    // Select de Disciplinas (Catálogo) para Oferta de Disciplina
    const ofertaDisciplinaSelect = document.getElementById('oferta-disciplina-select');
    ofertaDisciplinaSelect.innerHTML = '<option value="">Selecione uma disciplina do catálogo</option>';
    currentData.disciplinas_catalogo.forEach(disciplina => {
        const option = document.createElement('option');
        option.value = disciplina.id;
        option.textContent = `${disciplina.nome} (${disciplina.codigo})`;
        ofertaDisciplinaSelect.appendChild(option);
    });
}


// --- Funções de Adição (POST) ---

async function addTurma() {
    const nome = document.getElementById('turma-nome').value;
    if (!nome) {
        alert('Preencha o nome da turma.');
        return;
    }
    try {
        const response = await fetch('/api/turmas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome: nome })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('turma-nome').value = '';
            fetchData('turmas'); // Recarrega os dados da seção de turmas
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao adicionar turma:', error);
        alert('Erro ao adicionar turma.');
    }
}

async function addDisciplina() { // Esta função é para o Catálogo de Disciplinas
    const codigo = document.getElementById('disciplina-codigo').value;
    const nome = document.getElementById('disciplina-nome').value;
    if (!codigo || !nome) {
        alert('Preencha todos os campos para adicionar a disciplina ao catálogo.');
        return;
    }

    try {
        const response = await fetch('/api/disciplinas_catalogo', { // Rota corrigida
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ codigo: codigo, nome: nome })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('disciplina-codigo').value = '';
            document.getElementById('disciplina-nome').value = '';
            fetchData('disciplinas_catalogo'); // Recarrega os dados do catálogo
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao adicionar disciplina ao catálogo:', error);
        alert('Erro ao adicionar disciplina ao catálogo.');
    }
}

async function addAluno() {
    const matricula = document.getElementById('aluno-matricula').value;
    const nome = document.getElementById('aluno-nome').value;
    const telefone = document.getElementById('aluno-telefone').value;
    if (!matricula || !nome || !telefone) {
        alert('Preencha todos os campos para adicionar o aluno.');
        return;
    }
    try {
        const response = await fetch('/api/alunos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ matricula: matricula, nome: nome, telefone: telefone })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('aluno-matricula').value = '';
            document.getElementById('aluno-nome').value = '';
            document.getElementById('aluno-telefone').value = '';
            fetchData('alunos'); // Recarrega os dados da seção de alunos
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao adicionar aluno:', error);
        alert('Erro ao adicionar aluno.');
    }
}

async function addOfertaDisciplina() {
    const turmaId = document.getElementById('oferta-turma-select').value;
    const disciplinaCatalogoId = document.getElementById('oferta-disciplina-select').value;
    const professor = document.getElementById('oferta-professor').value;

    if (!turmaId || !disciplinaCatalogoId || !professor) {
        alert('Selecione a turma, a disciplina e preencha o professor para adicionar a oferta.');
        return;
    }

    try {
        const response = await fetch('/api/turma_disciplinas_ofertas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ turma_id: turmaId, disciplina_catalogo_id: disciplinaCatalogoId, professor: professor })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('oferta-turma-select').value = '';
            document.getElementById('oferta-disciplina-select').value = '';
            document.getElementById('oferta-professor').value = '';
            fetchData('matriculas'); // Recarrega a seção de matrículas/ofertas
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao adicionar oferta de disciplina:', error);
        alert('Erro ao adicionar oferta de disciplina.');
    }
}


async function addMatricula() {
    const alunoId = document.getElementById('matricula-aluno-select').value;
    const turmaDisciplinaId = document.getElementById('matricula-turma-disciplina-select').value;

    if (!alunoId || !turmaDisciplinaId) {
        alert('Selecione o aluno e a oferta de disciplina para realizar a matrícula.');
        return;
    }

    try {
        const response = await fetch('/api/matriculas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ aluno_id: alunoId, turma_disciplina_id: turmaDisciplinaId })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('matricula-aluno-select').value = '';
            document.getElementById('matricula-turma-disciplina-select').value = '';
            fetchData('matriculas'); // Recarrega os dados das matrículas
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao realizar matrícula:', error);
        alert('Erro ao realizar matrícula.');
    }
}


// --- Funções de Edição (PUT) ---
let currentEditId = null;
let currentEditType = null;

function openModal(id, type, data) {
    currentEditId = id;
    currentEditType = type;
    const modal = document.getElementById('edit-modal');
    const modalFormContent = document.getElementById('modal-form-content');
    modalFormContent.innerHTML = ''; // Limpa conteúdo anterior

    let formHtml = '';
    switch (type) {
        case 'turma':
            formHtml = `
                <div class="form-group">
                    <label for="edit-turma-nome">Nome da Turma:</label>
                    <input type="text" id="edit-turma-nome" value="${data.nome || ''}">
                </div>
            `;
            break;
        case 'disciplina': // Catálogo
            formHtml = `
                <div class="form-group">
                    <label for="edit-disciplina-codigo">Código da Disciplina:</label>
                    <input type="text" id="edit-disciplina-codigo" value="${data.codigo || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-disciplina-nome">Nome da Disciplina:</label>
                    <input type="text" id="edit-disciplina-nome" value="${data.nome || ''}">
                </div>
            `;
            break;
        case 'aluno':
            formHtml = `
                <div class="form-group">
                    <label for="edit-aluno-matricula">Matrícula do Aluno:</label>
                    <input type="text" id="edit-aluno-matricula" value="${data.matricula || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-aluno-nome">Nome do Aluno:</label>
                    <input type="text" id="edit-aluno-nome" value="${data.nome || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-aluno-telefone">Telefone do Aluno:</label>
                    <input type="text" id="edit-aluno-telefone" value="${data.telefone || ''}">
                </div>
            `;
            break;
        case 'oferta':
            formHtml = `
                <div class="form-group">
                    <label for="edit-oferta-professor">Professor:</label>
                    <input type="text" id="edit-oferta-professor" value="${data.professor || ''}">
                </div>
            `;
            break;
        default:
            formHtml = '<p>Tipo de edição desconhecido.</p>';
            break;
    }
    modalFormContent.innerHTML = formHtml;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('edit-modal').style.display = 'none';
    currentEditId = null;
    currentEditType = null;
}

async function saveEdit() {
    if (!currentEditId || !currentEditType) {
        alert('Nenhum item selecionado para edição.');
        return;
    }

    let url = '';
    let data = {};

    switch (currentEditType) {
        case 'turma':
            url = `/api/turmas/${currentEditId}`;
            data = { nome: document.getElementById('edit-turma-nome').value };
            if (!data.nome) { alert('Nome da turma é obrigatório.'); return; }
            break;
        case 'disciplina': // Catálogo
            url = `/api/disciplinas_catalogo/${currentEditId}`;
            data = {
                codigo: document.getElementById('edit-disciplina-codigo').value,
                nome: document.getElementById('edit-disciplina-nome').value
            };
            if (!data.codigo || !data.nome) { alert('Código e nome da disciplina são obrigatórios.'); return; }
            break;
        case 'aluno':
            url = `/api/alunos/${currentEditId}`;
            data = {
                matricula: document.getElementById('edit-aluno-matricula').value,
                nome: document.getElementById('edit-aluno-nome').value,
                telefone: document.getElementById('edit-aluno-telefone').value
            };
            if (!data.matricula || !data.nome || !data.telefone) { alert('Matrícula, nome e telefone são obrigatórios.'); return; }
            break;
        case 'oferta':
            url = `/api/turma_disciplinas_ofertas/${currentEditId}`;
            data = { professor: document.getElementById('edit-oferta-professor').value };
            if (!data.professor) { alert('Professor é obrigatório.'); return; }
            break;
        default:
            alert('Tipo de edição desconhecido.');
            return;
    }

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            closeModal();
            fetchData(currentActiveSection); // Recarrega os dados da seção atual
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao salvar edição:', error);
        alert('Erro ao salvar edição.');
    }
}

// Funções edit que chamam o modal
function editTurma(id, nome) {
    openModal(id, 'turma', { nome: nome });
}

function editDisciplina(id, codigo, nome) { // Catálogo
    openModal(id, 'disciplina', { codigo: codigo, nome: nome });
}

function editAluno(id, matricula, nome, telefone) {
    openModal(id, 'aluno', { matricula: matricula, nome: nome, telefone: telefone });
}

function editOfertaDisciplina(id, professor) {
    openModal(id, 'oferta', { professor: professor });
}


// --- Funções de Remoção (DELETE) ---

async function deleteItem(url, successMessage, sectionToRefresh) {
    if (!confirm('Tem certeza que deseja remover este item?')) {
        return;
    }
    try {
        const response = await fetch(url, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            fetchData(sectionToRefresh); // Recarrega os dados da seção
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao remover item:', error);
        alert('Erro ao remover item.');
    }
}

function deleteTurma(id) {
    deleteItem(`/api/turmas/${id}`, 'Turma removida com sucesso!', 'turmas');
}

function deleteDisciplina(id) { // Catálogo
    deleteItem(`/api/disciplinas_catalogo/${id}`, 'Disciplina do catálogo removida com sucesso!', 'disciplinas_catalogo');
}

function deleteAluno(id) {
    deleteItem(`/api/alunos/${id}`, 'Aluno removido com sucesso!', 'alunos');
}

function deleteOfertaDisciplina(id) {
    deleteItem(`/api/turma_disciplinas_ofertas/${id}`, 'Oferta de disciplina removida com sucesso!', 'matriculas'); // Matrículas section contains offers
}

function deleteMatricula(id) {
    deleteItem(`/api/matriculas/${id}`, 'Matrícula removida com sucesso!', 'matriculas');
}


// --- Funções de Busca ---

function searchData(type) {
    const searchInput = document.getElementById(`search-${type}-input`);
    if (searchInput) {
        currentSearchTerms[type] = searchInput.value;
    }
    fetchData(currentActiveSection); // Recarrega a seção atual com o termo de busca
}