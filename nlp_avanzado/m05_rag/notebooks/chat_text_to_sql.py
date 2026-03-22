try:
    import torch
    torch.classes.__path__ = []
except Exception:
    pass

import os
import json
import duckdb
import streamlit as st
import time

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS


st.set_page_config(page_title="SQL Chatbot RAG", layout="wide")
st.title("SQL Chatbot con RAG + DuckDB")

if "current_response" not in st.session_state:
    st.session_state.current_response = None

if "current_question" not in st.session_state:
    st.session_state.current_question = ""


# ========= CONFIG =========
DATASET_PATH = "../data/sql_dataset_bourbaki.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    OPENAI_API_KEY = st.text_input("Ingresa tu OPENAI_API_KEY", type="password")

if not OPENAI_API_KEY:
    st.warning("Ingresa tu API key para continuar.")
    st.stop()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# ========= CARGA DATASET =========
@st.cache_resource
def load_dataset_and_build_docs():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    documents = []
    table_lookup = {}

    for table_name, item in dataset.items():
        description = item.get("description", "").strip()
        schema = item.get("schema", "").strip()
        examples = item.get("examples", [])

        example_blocks = []
        for i, ex in enumerate(examples, start=1):
            ex_desc = ex.get("description", "").strip()
            ex_sql = ex.get("sql", "").strip()
            example_blocks.append(
                f"Ejemplo {i}:\n"
                f"Descripción: {ex_desc}\n"
                f"SQL: {ex_sql}"
            )

        page_content = (
            f"Tabla: {table_name}\n"
            f"Descripción: {description}\n"
            f"Schema: {schema}\n\n"
            f"Ejemplos:\n" + "\n\n".join(example_blocks)
        )

        documents.append(
            Document(
                page_content=page_content,
                metadata={
                    "table_name": table_name,
                    "source_type": "table_doc"
                }
            )
        )

        table_lookup[table_name] = {
            "table_name": table_name,
            "description": description,
            "schema": schema,
            "examples": examples
        }

    return documents, table_lookup


# ========= DUCKDB =========
@st.cache_resource
def build_duckdb_conn():
    conn = duckdb.connect(database=":memory:")

    setup_sql = """
    CREATE TABLE users (id INT PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100) UNIQUE, phone VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    INSERT INTO users VALUES
    (1, 'Ana', 'Gomez', 'cliente@example.com', '555-0101', '2026-02-15 10:00:00'),
    (2, 'Carlos', 'Ruiz', 'carlos.r@mail.com', NULL, '2026-03-01 14:30:00'),
    (3, 'Beatriz', 'Perez', 'bea.p@mail.com', '555-0103', '2026-03-10 09:15:00'),
    (4, 'David', 'Lopes', 'david.l@mail.com', NULL, '2026-01-20 11:20:00'),
    (5, 'Elena', 'Torres', 'elena.t@mail.com', '555-0105', '2026-03-16 16:45:00'),
    (6, 'Fernando', 'Silva', 'fer.s@mail.com', '555-0106', '2026-02-28 08:00:00'),
    (7, 'Gabriela', 'Cruz', 'gabi.c@mail.com', '555-0107', '2026-03-05 13:10:00'),
    (8, 'Hugo', 'Diaz', 'hugo.d@mail.com', NULL, '2026-03-12 17:55:00'),
    (9, 'Isabel', 'Ortiz', 'isa.o@mail.com', '555-0109', '2026-01-05 12:00:00'),
    (10, 'Jorge', 'Rios', 'jorge.r@mail.com', '555-0110', '2026-03-17 09:00:00');

    CREATE TABLE categories (id INT PRIMARY KEY, parent_id INT, name VARCHAR(100), description TEXT);
    INSERT INTO categories VALUES
    (1, NULL, 'Electronics', 'Gadgets and devices'),
    (2, NULL, 'Clothing', 'Apparel and accessories'),
    (3, 1, 'Laptops', 'Computers and notebooks'),
    (4, 1, 'Smartphones', 'Mobile devices'),
    (5, 2, 'Menswear', 'Men clothing'),
    (6, 5, 'Shirts', 'T-shirts and button-downs'),
    (7, 5, 'Pants', 'Jeans and trousers'),
    (8, 2, 'Womenswear', 'Women clothing'),
    (9, 8, 'Dresses', 'Casual and formal dresses'),
    (10, NULL, 'Home & Garden', 'Furniture and tools');

    CREATE TABLE products (id INT PRIMARY KEY, category_id INT, name VARCHAR(255), price DECIMAL(10, 2), stock_quantity INT, sku VARCHAR(50) UNIQUE, is_active BOOLEAN);
    INSERT INTO products VALUES
    (1, 3, 'Pro Laptop 15', 1299.99, 15, 'PROD-123', TRUE),
    (2, 4, 'Smartphone X', 799.50, 0, 'SKU-002', TRUE),
    (3, 6, 'Cotton T-Shirt', 19.99, 100, 'SKU-003', TRUE),
    (4, 7, 'Denim Jeans', 49.99, 50, 'SKU-004', TRUE),
    (5, 9, 'Summer Dress', 39.99, 0, 'SKU-005', FALSE),
    (6, 3, 'Basic Laptop 13', 599.00, 30, 'SKU-006', TRUE),
    (7, 10, 'Garden Shovel', 25.00, 20, 'SKU-007', TRUE),
    (8, 10, 'Table Lamp', 35.50, 10, 'SKU-008', FALSE),
    (9, 4, 'Budget Phone', 299.00, 0, 'SKU-009', TRUE),
    (10, 6, 'Polo Shirt', 29.99, 45, 'SKU-010', TRUE);

    CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, order_date TIMESTAMP, status VARCHAR(50), total_amount DECIMAL(10, 2));
    INSERT INTO orders VALUES
    (1, 1, '2024-05-10 10:00:00', 'cancelled', 1299.99),
    (2, 1, '2026-03-17 08:30:00', 'pending', 49.99),
    (3, 2, '2026-03-16 14:00:00', 'completed', 799.50),
    (4, 3, '2024-11-20 09:15:00', 'cancelled', 39.99),
    (5, 4, '2026-03-17 11:20:00', 'completed', 599.00),
    (6, 5, '2026-02-28 16:45:00', 'completed', 19.99),
    (7, 6, '2026-03-15 08:00:00', 'pending', 25.00),
    (8, 7, '2026-03-17 13:10:00', 'pending', 35.50),
    (9, 8, '2024-01-12 17:55:00', 'completed', 299.00),
    (10, 9, '2026-03-17 12:00:00', 'pending', 29.99);

    CREATE TABLE order_items (id INT PRIMARY KEY, order_id INT, product_id INT, quantity INT, unit_price DECIMAL(10, 2));
    INSERT INTO order_items VALUES
    (1, 1, 1, 1, 1299.99),
    (2, 2, 4, 1, 49.99),
    (3, 3, 2, 1, 799.50),
    (4, 4, 5, 1, 39.99),
    (5, 5, 6, 1, 599.00),
    (6, 6, 3, 1, 19.99),
    (7, 7, 7, 1, 25.00),
    (8, 8, 8, 1, 35.50),
    (9, 9, 9, 1, 299.00),
    (10, 10, 10, 1, 29.99);

    CREATE TABLE reviews (id INT PRIMARY KEY, product_id INT, user_id INT, rating INT, comment TEXT, created_at TIMESTAMP);
    INSERT INTO reviews VALUES
    (1, 1, 2, 5, 'Amazing laptop!', '2026-03-15 10:00:00'),
    (2, 2, 3, 1, 'Battery drains too fast.', '2026-02-20 14:30:00'),
    (3, 3, 4, 4, 'Good quality cotton.', '2026-03-10 09:15:00'),
    (4, 1, 5, 5, 'Best purchase ever.', '2026-03-16 11:20:00'),
    (5, 5, 6, 2, 'Size runs small.', '2026-01-20 16:45:00'),
    (6, 6, 7, 4, 'Great value for money.', '2026-02-28 08:00:00'),
    (7, 7, 8, 5, 'Sturdy and reliable.', '2026-03-05 13:10:00'),
    (8, 8, 9, 1, 'Arrived broken.', '2026-03-12 17:55:00'),
    (9, 9, 10, 3, 'Its okay for the price.', '2026-01-05 12:00:00'),
    (10, 10, 1, 5, 'Fits perfectly.', '2026-03-17 09:00:00');

    CREATE TABLE shipping_details (id INT PRIMARY KEY, order_id INT, address_line1 VARCHAR(255), city VARCHAR(100), state VARCHAR(100), postal_code VARCHAR(20), tracking_number VARCHAR(100), carrier VARCHAR(50));
    INSERT INTO shipping_details VALUES
    (1, 1, '123 Main St', 'Bogota', 'Cundinamarca', '110111', 'TRK-001', 'FedEx'),
    (2, 2, '456 Elm St', 'Medellin', 'Antioquia', '050001', 'TRK-002', 'UPS'),
    (3, 3, '789 Oak Ave', 'Cali', 'Valle', '760001', 'TRK-003', 'FedEx'),
    (4, 4, '321 Pine Rd', 'Cartagena', 'Bolivar', '130001', 'TRK-004', 'DHL'),
    (5, 5, '654 Cedar Ln', 'Barranquilla', 'Atlantico', '080001', 'TRK-005', 'FedEx'),
    (6, 6, '987 Birch Blvd', 'Bucaramanga', 'Santander', '680001', 'TRK-006', 'UPS'),
    (7, 7, '147 Walnut St', 'Pereira', 'Risaralda', '660001', 'TRK-007', 'FedEx'),
    (8, 8, '258 Cherry Ct', 'Manizales', 'Caldas', '170001', 'TRK-008', 'DHL'),
    (9, 9, '369 Spruce Way', 'Santa Marta', 'Magdalena', '470001', 'TRK-009', 'FedEx'),
    (10, 10, '741 Ash Dr', 'Cucuta', 'Norte de Santander', '540001', 'TRK-010', 'UPS');

    CREATE TABLE promotions (id INT PRIMARY KEY, code VARCHAR(50) UNIQUE, discount_percentage DECIMAL(5, 2), start_date DATE, end_date DATE, is_active BOOLEAN);
    INSERT INTO promotions VALUES
    (1, 'VERANO20', 20.00, '2026-03-01', '2026-03-31', TRUE),
    (2, 'WELCOME10', 10.00, '2026-01-01', '2026-12-31', TRUE),
    (3, 'FLASH50', 50.00, '2026-03-15', '2026-03-20', TRUE),
    (4, 'WINTER30', 30.00, '2025-12-01', '2026-02-28', FALSE),
    (5, 'VIP25', 25.00, '2026-01-01', '2026-12-31', TRUE),
    (6, 'SPRING15', 15.00, '2026-03-20', '2026-06-20', FALSE),
    (7, 'BF2025', 40.00, '2025-11-25', '2025-11-30', FALSE),
    (8, 'CYBER2025', 45.00, '2025-12-01', '2025-12-02', FALSE),
    (9, 'FREESHIP', 100.00, '2026-03-01', '2026-03-31', TRUE),
    (10, 'HALLOWEEN', 15.00, '2025-10-25', '2025-10-31', FALSE);
    """
    conn.execute(setup_sql)
    return conn


# ========= RAG =========
@st.cache_resource
def build_retriever(_documents):
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(_documents, embedding_model)
    return vectorstore.as_retriever(search_kwargs={"k": 3})


@st.cache_resource
def build_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def retrieve_relevant_tables(question: str, retriever, table_lookup: dict, k: int = 3):
    results = retriever.invoke(question)

    selected_tables = []
    context_blocks = []
    seen = set()

    for doc in results[:k]:
        table_name = doc.metadata.get("table_name")
        if not table_name or table_name in seen:
            continue

        seen.add(table_name)
        table_info = table_lookup.get(table_name)
        if not table_info:
            continue

        selected_tables.append(table_name)

        examples = table_info.get("examples", [])
        example_text = []

        for i, ex in enumerate(examples, start=1):
            ex_desc = ex.get("description", "").strip()
            ex_sql = ex.get("sql", "").strip()
            example_text.append(
                f"Ejemplo {i}:\n"
                f"- Descripción: {ex_desc}\n"
                f"- SQL: {ex_sql}"
            )

        block = (
            f"Tabla: {table_name}\n"
            f"Descripción: {table_info.get('description', '')}\n"
            f"Schema: {table_info.get('schema', '')}\n"
            f"Ejemplos:\n" + "\n".join(example_text)
        )
        context_blocks.append(block)

    final_context = "\n\n" + ("\n\n" + "=" * 80 + "\n\n").join(context_blocks)

    return {
        "question": question,
        "selected_tables": selected_tables,
        "context": final_context
    }


def generate_sql(question: str, retrieved_context: str, llm) -> str:
    prompt = f"""
Eres un experto en SQL para DuckDB.

Tu tarea es generar UNA consulta SQL válida y correcta para responder la pregunta del usuario.

Reglas:
- Usa solo las tablas y columnas disponibles en el contexto.
- No inventes tablas ni columnas.
- Genera SQL compatible con DuckDB.
- Devuelve únicamente la consulta SQL.
- No uses markdown.
- No agregues explicaciones.
- Cuando uses agregaciones, asigna aliases claros y legibles.
- Evita SELECT * salvo que el usuario pida explícitamente todos los campos.
- Prefiere seleccionar solo las columnas necesarias para responder.
- Si la pregunta pide información “por producto”, “por usuario”, “por pedido” o similares, y existe una tabla relacionada con nombres o etiquetas legibles, prefiere hacer JOIN para devolver campos entendibles por humanos en lugar de solo IDs.
- Prefiere resultados legibles para negocio, usando nombres descriptivos cuando sea posible.
- Si usas funciones de agregación y seleccionas columnas no agregadas, incluye esas columnas en el GROUP BY.
- Si la pregunta pide filtrar resultados agregados, usa HAVING en lugar de WHERE.

Pregunta del usuario:
{question}

Contexto disponible:
{retrieved_context}
"""
    response = llm.invoke(prompt)
    return response.content.strip()

def fix_sql_with_error(question: str, retrieved_context: str, failed_sql: str, error_message: str, llm) -> str:
    prompt = f"""
Eres un experto en SQL para DuckDB.

La siguiente consulta SQL falló al ejecutarse.
Debes corregirla.

Reglas:
- Usa solo las tablas y columnas disponibles en el contexto.
- No inventes tablas ni columnas.
- Devuelve únicamente SQL válido para DuckDB.
- No uses markdown.
- No agregues explicaciones.
- Si usas agregaciones y columnas no agregadas, incluye GROUP BY.
- Si el filtro depende de agregaciones, usa HAVING.

Pregunta original:
{question}

Contexto disponible:
{retrieved_context}

SQL con error:
{failed_sql}

Error de DuckDB:
{error_message}
"""
    response = llm.invoke(prompt)
    return response.content.strip()


def clean_sql(sql_text: str) -> str:
    sql_text = sql_text.strip()

    if sql_text.startswith("```sql"):
        sql_text = sql_text[len("```sql"):].strip()
    elif sql_text.startswith("```"):
        sql_text = sql_text[len("```"):].strip()

    if sql_text.endswith("```"):
        sql_text = sql_text[:-3].strip()

    return sql_text


def answer_question_safe(question: str, retriever, table_lookup: dict, conn, llm):
    retrieval_output = retrieve_relevant_tables(
        question=question,
        retriever=retriever,
        table_lookup=table_lookup,
        k=3
    )

    raw_sql = generate_sql(
        question=retrieval_output["question"],
        retrieved_context=retrieval_output["context"],
        llm=llm
    )

    sql_query = clean_sql(raw_sql)

    try:
        result_df = conn.execute(sql_query).df()
        error = None
    except Exception as e:
        first_error = str(e)

        try:
            fixed_raw_sql = fix_sql_with_error(
                question=retrieval_output["question"],
                retrieved_context=retrieval_output["context"],
                failed_sql=sql_query,
                error_message=first_error,
                llm=llm
            )
            sql_query = clean_sql(fixed_raw_sql)
            result_df = conn.execute(sql_query).df()
            error = None
        except Exception as e2:
            result_df = None
            error = str(e2)

    return {
        "question": question,
        "selected_tables": retrieval_output["selected_tables"],
        "sql_query": sql_query,
        "result_df": result_df,
        "error": error
    }


def typewriter_text(text: str, placeholder, speed: float = 0.01):
    current = ""
    for char in text:
        current += char
        placeholder.markdown(current)
        time.sleep(speed)


def build_natural_response(response: dict) -> str:
    if response["error"]:
        return f"Ocurrió un error al ejecutar la consulta: {response['error']}"

    df = response["result_df"]

    if df is None or df.empty:
        return "No encontré resultados para tu consulta."

    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        column = df.columns[0]
        return f"Encontré este resultado: {column} = {value}."

    return f"Encontré {len(df)} resultados."


def typewriter_words(text: str, placeholder, speed: float = 0.05):
    words = text.split()
    current = ""
    for word in words:
        current += word + " "
        placeholder.markdown(current)
        time.sleep(speed)


# ========= APP =========
documents, table_lookup = load_dataset_and_build_docs()
retriever = build_retriever(documents)
conn = build_duckdb_conn()
llm = build_llm()

with st.form("question_form", clear_on_submit=False):
    question = st.text_input("Haz una pregunta sobre la base de datos:")
    submitted = st.form_submit_button("Consultar")

if submitted and question.strip():
    st.session_state.current_question = question.strip()
    st.session_state.current_response = None

    with st.spinner("Consultando la base de datos..."):
        response = answer_question_safe(
            question=st.session_state.current_question,
            retriever=retriever,
            table_lookup=table_lookup,
            conn=conn,
            llm=llm
        )
        st.session_state.current_response = response

response = st.session_state.current_response

if response:
    st.subheader("Respuesta")
    natural_text = build_natural_response(response)
    answer_placeholder = st.empty()
    typewriter_words(natural_text, answer_placeholder, speed=0.04)

    st.subheader("Tablas recuperadas")
    st.write(response["selected_tables"])

    st.subheader("SQL generado")
    sql_placeholder = st.empty()
    typewriter_text(
        f"```sql\n{response['sql_query']}\n```",
        sql_placeholder,
        speed=0.003
    )

    if response["error"]:
        st.subheader("Error")
        st.error(response["error"])
    else:
        st.subheader("Resultado")
        st.table(response["result_df"])