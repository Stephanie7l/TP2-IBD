import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("estoque_camarao.db")

st.title("Trabalho Prático II - Introdução à Banco de Dados")
st.markdown("### Visualização interativa do banco de dados \"Estoque de Camarão nas Regiões Brasileiras Sudeste e Sul\"")

# Sidebar com seleção de consulta
opcao = st.sidebar.selectbox("Selecione uma consulta:", [
    "1. Pessoas físicas no Espírito Santo",
    "2. Municípios com apresentação In Natura",
    "3. Quantidade por espécie (Jurídica)",
    "4. Locais com Camarão Sete Barbas",
    "5. Embalagens por município",
    "6. Total por município e espécie",
    "7. Evolução do Camarão Branco",
    "8. Apresentações por espécie",
    "9. Total por tipo de pessoa",
    "10. Média por espécie"
])

# Consulta 1
if opcao.startswith("1"):
    df = pd.read_sql_query("""
        SELECT d.data_envio, m.estado, m.nome AS municipio, d.local_armazenamento
        FROM Declaracao d
        JOIN Pessoa p ON d.id_pessoa = p.id
        JOIN Municipio m ON d.id_municipio = m.id
        WHERE p.tipo = 'Física' AND m.estado = 'Espírito Santo';
    """, conn)
    st.dataframe(df)

# Consulta 2
elif opcao.startswith("2"):
    df = pd.read_sql_query("""
        SELECT DISTINCT m.nome AS municipio, m.estado
        FROM Declaracao d
        JOIN Municipio m ON d.id_municipio = m.id
        WHERE d.apresentacao = 'In Natura';
    """, conn)
    st.dataframe(df)

# Consulta 3
elif opcao.startswith("3"):
    df = pd.read_sql_query("""
        SELECT pr.especie, SUM(e.quantidade_kg) AS total
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Pessoa p ON d.id_pessoa = p.id
        JOIN Produto pr ON e.id_produto = pr.id
        WHERE p.tipo = 'Jurídica'
        GROUP BY pr.especie;
    """, conn)
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(df["total"], labels=df["especie"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Distribuição por espécie - Pessoas Jurídicas")
    plt.tight_layout()
    st.pyplot(fig)

# Consulta 4
elif opcao.startswith("4"):
    df = pd.read_sql_query("""
        SELECT d.local_armazenamento, pr.especie, e.quantidade_kg
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Produto pr ON e.id_produto = pr.id
        WHERE pr.especie = 'Camarão Sete Barbas';
    """, conn)
    st.dataframe(df)

# Consulta 5
elif opcao.startswith("5"):
    df = pd.read_sql_query("""
        SELECT embalagem, COUNT(*) AS total
        FROM Declaracao
        GROUP BY embalagem
        ORDER BY total DESC;
    """, conn)
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["embalagem"], df["total"])
    ax.set_title("Frequência de tipos de embalagem")
    ax.set_xlabel("Tipo de Embalagem")
    ax.set_ylabel("Nº de Declarações")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

# Consulta 6
elif opcao.startswith("6"):
    df = pd.read_sql_query("""
        SELECT m.nome AS municipio, pr.especie, SUM(e.quantidade_kg) AS total_kg
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Municipio m ON d.id_municipio = m.id
        JOIN Produto pr ON e.id_produto = pr.id
        GROUP BY m.nome, pr.especie;
    """, conn)
    pivot = df.pivot(index="municipio", columns="especie", values="total_kg").fillna(0)
    st.dataframe(pivot)

# Consulta 7
elif opcao.startswith("7"):
    df = pd.read_sql_query("""
        SELECT d.data_envio, SUM(e.quantidade_kg) AS total_branco
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Produto pr ON e.id_produto = pr.id
        WHERE pr.especie = 'Camarão Branco'
        GROUP BY d.data_envio
        ORDER BY d.data_envio;
    """, conn)
    df["data_envio"] = pd.to_datetime(df["data_envio"], dayfirst=True)
    df = df.sort_values("data_envio")
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["data_envio"], df["total_branco"], marker="o")
    ax.set_title("Evolução de Camarão Branco por data")
    ax.set_xlabel("Data")
    ax.set_ylabel("Total (kg)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

# Consulta 8
elif opcao.startswith("8"):
    df = pd.read_sql_query("""
        SELECT DISTINCT pr.especie, d.apresentacao
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Produto pr ON e.id_produto = pr.id;
    """, conn)
    st.dataframe(df)

# Consulta 9
elif opcao.startswith("9"):
    df = pd.read_sql_query("""
        SELECT p.tipo AS tipo_pessoa, SUM(e.quantidade_kg) AS total_kg
        FROM Estoque e
        JOIN Declaracao d ON e.id_declaracao = d.id
        JOIN Pessoa p ON d.id_pessoa = p.id
        GROUP BY p.tipo;
    """, conn)
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["tipo_pessoa"], df["total_kg"])
    ax.set_title("Total de camarões por tipo de pessoa")
    ax.set_xlabel("Tipo de Pessoa")
    ax.set_ylabel("Total (kg)")
    plt.tight_layout()
    st.pyplot(fig)

# Consulta 10
elif opcao.startswith("10"):
    df = pd.read_sql_query("""
        SELECT pr.especie, AVG(e.quantidade_kg) AS media_kg
        FROM Estoque e
        JOIN Produto pr ON e.id_produto = pr.id
        GROUP BY pr.especie
        ORDER BY media_kg DESC;
    """, conn)
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["especie"], df["media_kg"])
    ax.set_title("Média de quilos por tipo de camarão")
    ax.set_xlabel("Média (kg)")
    ax.set_ylabel("Espécie")
    plt.tight_layout()
    st.pyplot(fig)

conn.close()
