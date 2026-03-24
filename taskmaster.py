import streamlit as st
import json
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="TaskMaster Kanban", layout="wide", page_icon="📋")

# Aquí es donde practicas CSS: definimos cómo se ve cada "tarjeta" de tarea
st.markdown("""
    <style>
    /* Estilo para los títulos de las columnas (las cajas de arriba) */
    .header-pendiente { 
        background-color: #ff6b6b; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;
    }
    .header-proceso { 
        background-color: #feca57; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;
    }
    .header-terminado { 
        background-color: #1dd1a1; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;
    }
    
    /* Estilo de las tarjetas de tareas */
    .task-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #ccc;
        color: #2f3640; /* Texto oscuro dentro de la tarjeta blanca para que se lea bien */
    }
    
    /* Colores de los bordes según prioridad */
    .prioridad-alta { border-left-color: #ee5253; }
    .prioridad-media { border-left-color: #ffd32a; }
    .prioridad-baja { border-left-color: #10ac84; }
    
    /* Esto cambiará el estilo de todos los botones que tengan la palabra 'Eliminar' */
    button:contains("Eliminar") {
    color: #ff4b4b !important;
    border-color: #ff4b4b !important;
    }
    
    .header-archivado { 
    background-color: #8395a7; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. PERSISTENCIA DE DATOS ---
def cargar_tareas():
    if os.path.exists('kanban_data.json'):
        with open('kanban_data.json', 'r') as f:
            return json.load(f)
    return []

def guardar_tareas(tareas):
    with open('kanban_data.json', 'w') as f:
        json.dump(tareas, f, indent=4)

if 'tareas' not in st.session_state:
    st.session_state.tareas = cargar_tareas()

# --- 3. INTERFAZ: AÑADIR TAREA ---
st.title("📋 TaskMaster: Tu Tablero Kanban")

with st.sidebar:
    st.header("➕ Nueva Tarea")
    with st.form("form_tarea", clear_on_submit=True):
        titulo = st.text_input("¿Qué hay que hacer?")
        prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
        submit = st.form_submit_button("Añadir al tablero")
        
        if submit and titulo:
            nueva = {"id": len(st.session_state.tareas), "titulo": titulo, "prioridad": prioridad, "estado": "Pendiente"}
            st.session_state.tareas.append(nueva)
            guardar_tareas(st.session_state.tareas)
            st.rerun()

# --- 4. EL TABLERO (CON COLUMNA DE ARCHIVO) ---
col1, col2, col3 = st.columns(3)

estados = [
    ("⏳ Pendiente", "Pendiente", col1, "Empezar →", "header-pendiente"),
    ("🚀 En Proceso", "En Proceso", col2, "Terminar ✅", "header-proceso"),
    ("🎯 Terminado", "Terminado", col3, "Borrar 🔥", "header-terminado"),
]

for nombre_col, estado_id, columna, texto_boton, clase_css in estados:
    with columna:
        st.markdown(f'<div class="{clase_css}"><h3>{nombre_col}</h3></div>', unsafe_allow_html=True)
        
        tareas_estado = [t for t in st.session_state.tareas if t['estado'] == estado_id]
        
        for tarea in tareas_estado:
            clase_prioridad = f"prioridad-{tarea['prioridad'].lower()}"
            
            st.markdown(f"""
                <div class="task-card {clase_prioridad}">
                    <strong>{tarea['titulo']}</strong><br>
                    <small>Prioridad: {tarea['prioridad']}</small>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(texto_boton, key=f"btn_{tarea['id']}"):
                # FLUJO DE ESTADOS:
                if estado_id == "Pendiente":
                    tarea['estado'] = "En Proceso"
                elif estado_id == "En Proceso":
                    tarea['estado'] = "Terminado"
                elif estado_id == "Terminado":
                    st.session_state.tareas.remove(tarea) # Borrado definitivo
                
                guardar_tareas(st.session_state.tareas)
                st.rerun()