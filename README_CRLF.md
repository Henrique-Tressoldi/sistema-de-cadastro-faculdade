# Sistema de Cadastro Faculdade

Sistema web desenvolvido com **Flask (Python)** para gerenciamento acadêmico de **alunos, turmas, disciplinas e matrículas**. O sistema possui uma interface simples e acessível, utilizando **HTML**, **CSS** e **JavaScript**.

---

## 🧪 Tecnologias utilizadas

- Python (Flask)
- HTML5
- CSS3
- JavaScript
- Jinja2 (Templates Flask)
- Bootstrap (opcional)
- Deploy com `Procfile` (Heroku)

---

## 🚀 Funcionalidades

- [x] Cadastro de alunos
- [x] Cadastro de disciplinas
- [x] Cadastro de turmas
- [x] Matrícula de alunos
- [x] Edição e exclusão de registros
- [ ] Integração com banco de dados (em desenvolvimento)
- [ ] Autenticação de usuários

---

## ⚙️ Como executar o projeto

### Pré-requisitos

- Python 3 instalado
- (Opcional) Ambiente virtual configurado

### Passos

```bash
# Clone o repositório
git clone https://github.com/Henrique-Tressoldi/sistema-de-cadastro-faculdade.git
cd sistema-de-cadastro-faculdade

# (Opcional) Crie e ative um ambiente virtual
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o projeto
flask run
# ou
python app.py
```

Acesse em `http://localhost:5000` no seu navegador.

---

## 🗂️ Estrutura de pastas

```
sistema-de-cadastro-faculdade/
│
├── app.py                 # Arquivo principal da aplicação Flask
├── requirements.txt       # Lista de dependências
├── Procfile               # Configuração para deploy no Heroku
│
├── templates/             # Arquivos HTML (Jinja2)
│   ├── index.html
│   ├── alunos.html
│   ├── disciplinas.html
│   └── turmas.html
│
└── static/                # Arquivos estáticos (CSS e JS)
    ├── css/
    └── js/
```

---

## 🧭 Próximos passos

- [ ] Conectar com banco de dados (SQLite ou PostgreSQL)
- [ ] Implementar autenticação (login/senha)
- [ ] Adicionar mensagens de sucesso e erro nos formulários
- [ ] Adicionar testes automatizados
- [ ] Melhorar o design responsivo

---

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch com sua feature: `git checkout -b feature/minha-feature`
3. Faça commit das suas alterações: `git commit -m 'feat: minha nova feature'`
4. Faça push da sua branch: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 👤 Autor

**Henrique Tressoldi**  
Estudante de Análise e Desenvolvimento de Sistemas na UTFPR  
📍 Americano morando no Brasil  
💻 Estuda programação há 4 anos  
🌐 GitHub: [Henrique-Tressoldi](https://github.com/Henrique-Tressoldi)

---

## 📄 Licença

Este projeto ainda não possui uma licença. Entre em contato caso deseje utilizá-lo comercialmente.

---
