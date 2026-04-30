from fastapi import FastAPI, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymysql
import mysql.connector
import hashlib
from datetime import date, datetime

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")

def hash_senha(senha: str) -> str:
    """Transforma a senha em um código SHA-256 irreversível"""
    return hashlib.sha256(senha.encode()).hexdigest()

def calcular_idade(nascimento):
    if not nascimento:
        return "N/A"
    if isinstance(nascimento, str):
        try:
            nascimento = datetime.strptime(nascimento, '%Y-%m-%d').date()
        except ValueError:
            return "N/A"
    
    hoje = date.today()
    anos = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    if anos == 0:
        meses = (hoje.year - nascimento.year) * 12 + hoje.month - nascimento.month
        return f"{meses} meses"
    return f"{anos} anos"

def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="petshop"
    )
    
    # Garante que a tabela clientes exista automaticamente!
    cursor = conn.cursor(buffered=True)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            cpf VARCHAR(20) NOT NULL,
            nascimento VARCHAR(15) NOT NULL,
            telefone VARCHAR(20) NOT NULL,
            senha VARCHAR(100) NOT NULL
        )
    """)
    
    # Garante que a tabela pets tenha a coluna cliente_id para vincular o pet ao dono
    try:
        cursor.execute("ALTER TABLE pets ADD COLUMN cliente_id INT")
    except:
        pass # Se der erro, é porque a coluna já existe
    
    # Garante que a tabela pets tenha as novas colunas de medidas
    try:
        cursor.execute("ALTER TABLE pets ADD COLUMN peso DECIMAL(5,2), ADD COLUMN altura DECIMAL(5,2), ADD COLUMN comprimento DECIMAL(5,2), ADD COLUMN largura DECIMAL(5,2)")
    except:
        pass
    
    # Tabelas Administrativas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(100) NOT NULL
        )
    """)
    # Cria um admin padrão caso não exista nenhum
    cursor.execute("SELECT * FROM admin WHERE email='admin@gmail.com'")
    if not cursor.fetchone():
        senha_admin = hash_senha('123456')
        cursor.execute("INSERT INTO admin (email, senha) VALUES ('admin@gmail.com', %s)", (senha_admin,))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            cargo VARCHAR(100) NOT NULL,
            salario DECIMAL(10,2) NOT NULL,
            telefone VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    
    return conn

# ROTA PRINCIPAL (Página Inicial)
@app.get("/", response_class=HTMLResponse)
def read_home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

# LOGIN
@app.post("/login")
def login(request: Request, email: str = Form(...), senha: str = Form(...), db=Depends(get_db)):
    senha_hasheada = hash_senha(senha)
    with db.cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute(
            "SELECT * FROM clientes WHERE email=%s AND senha=%s",
            (email, senha_hasheada)
        )
        user = cursor.fetchone()

    if user:
        # Criamos o redirecionamento e salvamos quem logou em um "cookie" (sessão simples)
        response = RedirectResponse(url="/pets", status_code=303)
        response.set_cookie(key="cliente_id", value=str(user["id"]))
        return response
    
    return templates.TemplateResponse(request=request, name="home.html", context={"msg_login": "E-mail ou senha incorretos."})

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("cliente_id")
    return response

# CADASTRO
@app.post("/cadastro")
def cadastro(
    request: Request,
    fullName: str = Form(...),
    email: str = Form(...),
    cpf: str = Form(...),
    birth: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):
    with db.cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute("SELECT * FROM clientes WHERE email=%s OR cpf=%s OR telefone=%s", (email, cpf, phone))
        cliente_existente = cursor.fetchone()
        if cliente_existente:
            if cliente_existente['email'] == email:
                error_field = "email"
                error_msg = "E-mail já está cadastrado."
            elif cliente_existente['cpf'] == cpf:
                error_field = "cpf"
                error_msg = "CPF já está cadastrado."
            else:
                error_field = "phone"
                error_msg = "Telefone já está cadastrado."
            
            return templates.TemplateResponse(request=request, name="home.html", context={
                "open_cadastro": True,
                "error_field": error_field,
                "error_msg": error_msg,
                "form_data": {"fullName": fullName, "email": email, "cpf": cpf, "birth": birth, "phone": phone}
            })
        
        senha_hasheada = hash_senha(password)
        cursor.execute(
            "INSERT INTO clientes (nome, email, cpf, nascimento, telefone, senha) VALUES (%s, %s, %s, %s, %s, %s)", 
            (fullName, email, cpf, birth, phone, senha_hasheada)
        )
        db.commit()

    return templates.TemplateResponse(request=request, name="home.html", context={"msg_login": "Conta criada com sucesso! Faça login.", "saved_email": email})

# ROTA PLANOS
@app.get("/planos", response_class=HTMLResponse)
def read_planos(request: Request):
    return templates.TemplateResponse(request=request, name="planos.html")

#PETS 
@app.get("/pets", response_class=HTMLResponse)
def listar_pets(request: Request, db=Depends(get_db)):
    cliente_id = request.cookies.get("cliente_id")
    if not cliente_id:
        return RedirectResponse(url="/", status_code=303)

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM pets WHERE cliente_id=%s", (cliente_id,))
        pets = cursor.fetchall()
        for pet in pets:
            pet['idade'] = calcular_idade(pet['nascimento'])
    return templates.TemplateResponse(request=request, name="pets.html", context={"pets": pets})

@app.post("/pets")
def add_pet(request: Request, nome: str = Form(...), nascimento: str = Form(...),
            especie: str = Form(...), raca: str = Form(...),
            peso: float = Form(...), altura: float = Form(...),
            comprimento: float = Form(...), largura: float = Form(...),
            db=Depends(get_db)):
    cliente_id = request.cookies.get("cliente_id")
    if not cliente_id:
        return RedirectResponse(url="/", status_code=303)

    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO pets (cliente_id, nome, nascimento, especie, raca, peso, altura, comprimento, largura) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (cliente_id, nome, nascimento, especie, raca, peso, altura, comprimento, largura)
        )
        db.commit()
    return RedirectResponse(url="/pets", status_code=303)

# AGENDA (Substitui o antigo /eventos GET)
@app.get("/agenda", response_class=HTMLResponse)
def listar_eventos(request: Request, db=Depends(get_db)):
    cliente_id = request.cookies.get("cliente_id")
    if not cliente_id:
        return RedirectResponse(url="/", status_code=303)

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT e.*, p.nome as pet_nome 
            FROM eventos e
            LEFT JOIN pets p ON e.pet_id = p.id
            WHERE p.cliente_id = %s
        """, (cliente_id,))
        eventos = cursor.fetchall()
        
        cursor.execute("SELECT * FROM pets WHERE cliente_id=%s", (cliente_id,))
        pets = cursor.fetchall()
        
    return templates.TemplateResponse(request=request, name="agenda.html", context={"eventos": eventos, "pets": pets})

@app.post("/eventos")
def add_evento(pet_id: int = Form(...), data: str = Form(...),
               hora: str = Form(...), tipo: str = Form(...),
               descricao: str = Form(...), local: str = Form(""),
               observacoes: str = Form(""), db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO eventos 
            (pet_id,data,hora,tipo,descricao,local,observacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (pet_id, data, hora, tipo, descricao, local, observacoes))
        db.commit()
    return RedirectResponse(url="/agenda", status_code=303)

# DEMAIS PÁGINAS DA ÁREA DO CLIENTE
@app.get("/meu-plano", response_class=HTMLResponse)
def read_meu_plano(request: Request):
    return templates.TemplateResponse(request=request, name="Meu_plano.html")

@app.get("/calendario", response_class=HTMLResponse)
def read_calendario(request: Request):
    return templates.TemplateResponse(request=request, name="calendario.html")

@app.get("/agendar-consulta", response_class=HTMLResponse)
def read_agendar_consulta(request: Request):
    return templates.TemplateResponse(request=request, name="Agendar_consulta.html")

#FUNCIONARIOS
@app.get("/funcionarios")
def listar_funcionarios(db=Depends(get_db)):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM funcionarios")
        return cursor.fetchall()


@app.post("/funcionarios")
def add_funcionario(
    nome: str = Form(...),
    cargo: str = Form(...),
    salario: float = Form(...),
    telefone: str = Form(...),
    db=Depends(get_db)
):
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO funcionarios (nome, cargo, salario, telefone) VALUES (%s,%s,%s,%s)",
            (nome, cargo, salario, telefone)
        )
        db.commit()

    return {"msg": "Funcionário cadastrado"}


@app.delete("/funcionarios/{id}")
def deletar_funcionario(id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM funcionarios WHERE id=%s", (id,))
        db.commit()

    return {"msg": "Funcionário removido"}


@app.put("/funcionarios/{id}")
def atualizar_funcionario(
    id: int,
    nome: str = Form(...),
    cargo: str = Form(...),
    salario: float = Form(...),
    telefone: str = Form(...),
    db=Depends(get_db)
):
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE funcionarios SET nome=%s, cargo=%s, salario=%s, telefone=%s WHERE id=%s",
            (nome, cargo, salario, telefone, id)
        )
        db.commit()

    return {"msg": "Funcionário atualizado"}

# ==========================================
# ROTAS ADMINISTRATIVAS
# ==========================================

@app.get("/login-admin", response_class=HTMLResponse)
def read_login_admin(request: Request):
    return templates.TemplateResponse(request=request, name="loginAdm.html")

@app.post("/login-admin")
def process_login_admin(request: Request, email: str = Form(...), senha: str = Form(...), db=Depends(get_db)):
    senha_hasheada = hash_senha(senha)
    with db.cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute("SELECT * FROM admin WHERE email=%s AND senha=%s", (email, senha_hasheada))
        admin = cursor.fetchone()
    
    if admin:
        return RedirectResponse(url="/admin", status_code=303)
    
    return templates.TemplateResponse(request=request, name="loginAdm.html", context={"msg_login": "Credenciais inválidas."})

@app.get("/admin", response_class=HTMLResponse)
def painel_admin(request: Request, db=Depends(get_db)):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM cargos")
        cargos = cursor.fetchall()
        cursor.execute("SELECT * FROM funcionarios")
        funcionarios = cursor.fetchall()
        cursor.execute("SELECT id, nome, email, cpf, telefone FROM clientes")
        clientes = cursor.fetchall()
    return templates.TemplateResponse(request=request, name="admin.html", context={"cargos": cargos, "funcionarios": funcionarios, "clientes": clientes})

@app.post("/admin/cargos")
def add_cargo_admin(nome: str = Form(...), db=Depends(get_db)):
    with db.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO cargos (nome) VALUES (%s)", (nome,))
            db.commit()
        except:
            pass # Ignora se o cargo já existir
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/funcionarios")
def add_funcionario_admin(nome: str = Form(...), cargo: str = Form(...), salario: float = Form(...), telefone: str = Form(...), db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO funcionarios (nome, cargo, salario, telefone) VALUES (%s,%s,%s,%s)", (nome, cargo, salario, telefone))
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/funcionarios/{id}/deletar")
def deletar_funcionario_admin(id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM funcionarios WHERE id=%s", (id,))
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)