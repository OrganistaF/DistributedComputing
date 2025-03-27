# DistributedComputing - Tic Tac Toe Online

Este es un proyecto para la clase de computación distribuida en la Universidad Panamericana. Consiste en un juego de Tic Tac Toe (Gato) en el que dos usuarios pueden conectarse y jugar en tiempo real. 

## 📌 Características

- Conexión entre dos jugadores a través de una arquitectura cliente-servidor.
- Sincronización en tiempo real del tablero de juego.
- Registro del número de victorias de cada jugador.
- Interfaz gráfica sencilla para mejorar la experiencia del usuario.

## 🛠️ Tecnologías Utilizadas

- **C**: Implementación del servidor y la lógica del juego.
- **Python**: Cliente y GUI para interactuar con el usuario.

## 📂 Estructura del Proyecto
```bash
/DistributedComputing
│── /server       # Código fuente del servidor en C
│── /client       # Código fuente del cliente en Python
│── /gui          # Interfaz gráfica en Python
│── README.md     # Documentación del proyecto
```


## 🚀 Instalación y Ejecución

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu_usuario/DistributedComputing.git
cd DistributedComputing
```

### 2️⃣ Ejecutar el servidor (en C)
```bash
cd server
gcc server.c -o server
./server
```

### 3️⃣ Ejecutar el cliente (en Python)
```bash
cd ../client
python client.py
```

